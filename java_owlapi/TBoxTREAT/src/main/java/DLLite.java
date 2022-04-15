import java.io.*;
import java.util.*;

import ReasonerUtils.IReasonerUtil;
import eu.trowl.owlapi3.rel.reasoner.dl.RELReasoner;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.util.*;


public class DLLite {
    final private String output_dir;
    protected OWLOntologyManager man;
    protected OWLDataFactory factory;
    protected OWLOntology ont;
    private OWLClass owlThing;
    String base = "http://treat";

    public DLLite(String output_dir) {
//        this.koncludeUtil = new KoncludeUtil(Konclude_bin, output_dir);
        this.output_dir = output_dir;
    }

    private void loadOnto(String ontology_file) {
        try {
            man = OWLManager.createOWLOntologyManager();
            File initialFile = new File(ontology_file);
            InputStream inputStream = new FileInputStream(initialFile);
            // the stream holding the file content
            ont = man.loadOntologyFromOntologyDocument(inputStream);
            factory = man.getOWLDataFactory();
            owlThing = factory.getOWLThing();
        } catch (OWLOntologyCreationException | IllegalArgumentException | FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    private void saveOnto(OWLOntology toSaveOnto, String fileName) {
        System.out.println("Saving new ontology " + this.output_dir + fileName);
        File inferredOntologyFile = new File(this.output_dir + fileName);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            // We use the nt format as for the input ontology.
             NTriplesDocumentFormat format = new NTriplesDocumentFormat();
//            TurtleDocumentFormat format = new TurtleDocumentFormat();
            man.saveOntology(toSaveOnto, format, outputStream);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    private OWLClassExpression getDomain(OWLObjectProperty p) {
        for (OWLAxiom ax : this.ont.getAxioms(p)) {
            if (ax.getAxiomType().equals(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                return ((OWLObjectPropertyDomainAxiom) ax).getDomain();
            }
        }
        return this.owlThing;
    }

    private OWLClassExpression getRange(OWLObjectProperty p) {
        for (OWLAxiom ax : this.ont.getAxioms(p)) {
            if (ax.getAxiomType().equals(AxiomType.OBJECT_PROPERTY_RANGE)) {
                return ((OWLObjectPropertyRangeAxiom) ax).getRange();
            }
        }
        return this.owlThing;
    }

    private void addRandRivs(Map<String, OWLClassExpression> mapCache) {
        System.out.println("Creating D...");
        for (OWLObjectProperty R : ont.getObjectPropertiesInSignature()) {
            if (!R.isNamed()) {
                continue;
            }
            // expression for R and R-
            OWLClassExpression expD1 = factory.getOWLObjectSomeValuesFrom(R, this.owlThing);
            OWLSubClassOfAxiom rpSub1 = factory.getOWLSubClassOfAxiom(expD1, getDomain(R));
            OWLClassExpression expD2 = factory.getOWLObjectSomeValuesFrom(R.getInverseProperty(), this.owlThing);
            OWLSubClassOfAxiom rpSub2 = factory.getOWLSubClassOfAxiom(expD2, getRange(R));
            man.addAxiom(ont, rpSub1);
            man.addAxiom(ont, rpSub2);
            // additianal class for (\some R) and (\some R-)
            String nameR = R.getNamedProperty().getIRI().toString();
            List<String> splits = splitIRI(nameR);
            String classNameD1 = splits.get(0) + "#some_" + splits.get(1);
            String classNameD2 = splits.get(0) + "#some_ivs_" + splits.get(1);
            OWLClass D1 = factory.getOWLClass(IRI.create(classNameD1));
            OWLClass D2 = factory.getOWLClass(IRI.create(classNameD2));
            // map D1 to (\some R) and D2 to (\some R-)
            OWLAxiom def1 = factory.getOWLEquivalentClassesAxiom(D1, expD1);
            OWLAxiom def2 = factory.getOWLEquivalentClassesAxiom(D2, expD2);
            man.addAxiom(ont, def1);
            man.addAxiom(ont, def2);
            mapCache.put(D1.getIRI().toString(), expD1);
            mapCache.put(D2.getIRI().toString(), expD2);
        }
    }

    private List<String> splitIRI(String iri) {
        String clsIRIStr = iri;
        int splitIndex = 0;
        if (clsIRIStr.contains("#")) {
            splitIndex = clsIRIStr.lastIndexOf('#');
        } else {
            splitIndex = clsIRIStr.lastIndexOf('/');
        }
        String prefix = clsIRIStr.substring(0, splitIndex);
        String name = clsIRIStr.substring(splitIndex + 1);
        return Arrays.asList(prefix, name);
    }

    private void addNegD(Map<String, OWLClassExpression> mapCache) {
        System.out.println("Creating neg D...");
        for (OWLClass cls : ont.getClassesInSignature()) {
            if (!cls.isNamed()) {
                continue;
            }
            String clsIRIStr = cls.getIRI().toString();
            List<String> splits = splitIRI(clsIRIStr);
            String negClsName = splits.get(0) + "#neg_" + splits.get(1);
            OWLClass negCls = factory.getOWLClass(IRI.create(negClsName));
            OWLClassExpression expCompl = cls.getObjectComplementOf();
            OWLAxiom negDef = factory.getOWLEquivalentClassesAxiom(negCls, expCompl);
            man.addAxiom(ont, negDef);
            mapCache.put(negCls.getIRI().toString(), expCompl);
        }
    }

    public void owl2dlliteOrginal(IReasonerUtil reasonerUtil, String in_file) throws Exception {
        System.out.println("To DL-lite: " + in_file);
        // load ontology from file
        loadOnto(in_file);
        // remove annotations
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ont.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax : toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            this.man.applyChange(removeAxiom);
        }
        // a map to keep additional class IRI to class expression
        Map<String, OWLClassExpression> map = new HashMap<String, OWLClassExpression>();
        // Now create restrictions to describe the class of individual object properties
        addRandRivs(map);
        addNegD(map);
        // Schema + Delta, then inference
        OWLOntology infOnt1 = reasonerUtil.classify(ont, man);

        // merge ont and infOnt1
        System.out.println("merging infOnt1 to ont...");
        OWLOntologyMerger merger = new OWLOntologyMerger(man);
        IRI mergedOntologyIRI1 = IRI.create("http://www.semanticweb.com/merged1");
        OWLOntology merged1 = merger.createMergedOntology(man, mergedOntologyIRI1);
        System.out.println("Removing ont and infOnt1...");
        man.removeOntology(ont);
        man.removeOntology(infOnt1);
        // replace D, N with expressions
        System.out.println("Replace D and N with expressions...");
        Set<OWLSubClassOfAxiom> subclassof = merged1.getAxioms(AxiomType.SUBCLASS_OF);
        for (OWLSubClassOfAxiom s : subclassof) {
            OWLClassExpression sub = s.getSubClass();
            OWLClassExpression sup = s.getSuperClass();
            String subIRI = "";
            String supIRI = "";
            if (sub.isNamed()) {
                subIRI = ((OWLClass) sub).getIRI().toString();
            }
            if (sup.isNamed()) {
                supIRI = ((OWLClass) sup).getIRI().toString();
            }
            if (map.containsKey(subIRI) || map.containsKey(supIRI)) {
                OWLClassExpression recoverSub = map.getOrDefault(subIRI, sub);
                OWLClassExpression recoverSup = map.getOrDefault(supIRI, sup);
                OWLSubClassOfAxiom recoverAX = factory.getOWLSubClassOfAxiom(recoverSub, recoverSup);
                // Add the axiom to our ontology
                AddAxiom tmpaddAx = new AddAxiom(merged1, recoverAX);
                man.applyChange(tmpaddAx);
            }
        }
        // remove additional classes
        System.out.println("Removing D and N...");
        OWLEntityRemover remover = new OWLEntityRemover(merged1);
        for (OWLClass namedClass : merged1.getClassesInSignature()) {
            if (map.containsKey(namedClass.getIRI().toString())) {
                namedClass.accept(remover);
            }
        }
        man.applyChanges(remover.getChanges());
        // new schema = Schema.classification ( recover D and N)
        System.out.println("Infer recovered schema + delta ...");

        //B1 \in B2 or B1 \in \negB2
//        OWLOntology infOnt2 = this.koncludeUtil.koncludeClassifier(merged1, man);
        OWLOntology infOnt2 = reasonerUtil.classify(merged1, man);
        // Now get the inferred ontology generator to generate some inferred
        // axioms for us (into our fresh ontology). We specify the reasoner that
        // we want to use and the inferred axiom generators that we want to use.
        // merge new inferred atoms
        System.out.println("Merging infOnt2 with last round merged...");
        IRI mergedOntologyIRI2 = IRI.create("http://www.semanticweb.com/merged2");
        OWLOntologyMerger merger2 = new OWLOntologyMerger(man);
        OWLOntology merged2 = merger2.createMergedOntology(man, mergedOntologyIRI2);

        // if for materialization we remove unwanted axioms like asymmetric etc.
        // if for inconsistency justification, we keep these axioms.
        System.out.println("Removing additional properties ...");
        toRemoveAxiom = new ArrayList<>();
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY));
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY));
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.EQUIVALENT_OBJECT_PROPERTIES));
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.REFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.IRREFLEXIVE_OBJECT_PROPERTY));
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.TRANSITIVE_OBJECT_PROPERTY));
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.SUB_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.DISJOINT_CLASSES));
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.EQUIVALENT_CLASSES));

        for (OWLAxiom ax : toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(merged2, ax);
            man.applyChange(removeAxiom);
        }
        saveOnto(merged2, "tbox_dllite.nt");
    }

    public void owl2dllite_less(IReasonerUtil reasonerUtil, String in_file) throws Exception {
        loadOnto(in_file);
        String base = "http://org.semanticweb.restrictionexample";
        OWLDataFactory factory = man.getOWLDataFactory();
        // remove annotations
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ont.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax : toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            man.applyChange(removeAxiom);
        }
        // a map to keep additional class IRI to class expression
        Map<String, OWLClassExpression> map = new HashMap<String, OWLClassExpression>();
        System.out.println("Creating N...");
        for (OWLClass cls : ont.getClassesInSignature()) {
            if (!cls.isNamed()) {
                continue;
            }
            String clsName = cls.toStringID();
            if (clsName.contains("#")) {
                clsName = clsName.substring(clsName.lastIndexOf('#') + 1, clsName.length());
            } else {
                clsName = clsName.substring(clsName.lastIndexOf('/') + 1, clsName.length());
            }
            String negClsName = base + "#neg_" + clsName;
            OWLClass negCls = factory.getOWLClass(IRI.create(negClsName));
            OWLClassExpression expCompl = cls.getObjectComplementOf();
            OWLAxiom negDef = factory.getOWLEquivalentClassesAxiom(negCls, expCompl);
            man.addAxiom(ont, negDef);
            map.put(negCls.getIRI().toString(), expCompl);
        }
        System.out.println("Infer A and neg A");
        OWLOntology infOnt1 = reasonerUtil.classify(ont, man);
        // merge ont and infOnt1
        System.out.println("merging infOnt1 to ont...");
        OWLOntologyMerger merger = new OWLOntologyMerger(man);
        IRI mergedOntologyIRI1 = IRI.create("http://www.semanticweb.com/merged1");
        OWLOntology merged1 = merger.createMergedOntology(man, mergedOntologyIRI1);
        // remove class disjointness
        System.out.println("Removing DISJOINT_CLASSES axioms ...");
        List<OWLAxiom> toRemoveAxiom0 = new ArrayList<OWLAxiom>();
        toRemoveAxiom0.addAll(merged1.getAxioms(AxiomType.DISJOINT_CLASSES));
        for (OWLAxiom ax : toRemoveAxiom0) {
            RemoveAxiom removeAxiom = new RemoveAxiom(merged1, ax);
            man.applyChange(removeAxiom);
        }
        //keep the merged1 only
        man.removeOntology(ont);
        man.removeOntology(infOnt1);

        // find all properties with domain and range
        List<String> propertysWithDomain = new ArrayList<>();
        for (OWLObjectPropertyDomainAxiom doma : merged1.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
            propertysWithDomain.add(doma.getProperty().getNamedProperty().toStringID());
            // add expression  axiom
            OWLObjectProperty r_p = doma.getProperty().getNamedProperty();
            OWLClassExpression someRP = factory.getOWLObjectSomeValuesFrom(r_p, factory.getOWLThing());
            OWLSubClassOfAxiom rpSub = factory.getOWLSubClassOfAxiom(someRP, doma.getDomain());
            man.addAxiom(merged1, rpSub);
        }
        List<String> propertysWithRange = new ArrayList<>();
        for (OWLObjectPropertyRangeAxiom rg : merged1.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
            propertysWithRange.add(rg.getProperty().getNamedProperty().toStringID());
            // add expression  axiom
            OWLObjectProperty r_p = rg.getProperty().getNamedProperty();
            OWLClassExpression someRRP = factory.getOWLObjectSomeValuesFrom(r_p.getInverseProperty(), factory.getOWLThing());
            OWLSubClassOfAxiom rrpSub = factory.getOWLSubClassOfAxiom(someRRP, rg.getRange());
            man.addAxiom(merged1, rrpSub);
        }
        // Now create restrictions to describe the class of individual object properties without domain or range
        System.out.println("Creating D and neg D...");
        for (OWLObjectProperty R : merged1.getObjectPropertiesInSignature()) {
            if (!R.isNamed()) {
                continue;
            }
            String nameR = R.getNamedProperty().toStringID();
            if (propertysWithDomain.contains(nameR) && propertysWithRange.contains(nameR)) {
                continue;
            }
            String nameRShort = "";
            if (nameR.contains("#")) {
                nameRShort = nameR.substring(nameR.lastIndexOf('#') + 1, nameR.length());
            } else {
                nameRShort = nameR.substring(nameR.lastIndexOf('/') + 1, nameR.length());
            }
            if (!propertysWithDomain.contains(nameR)) {
                // additianal class for (\some R)
                OWLClassExpression expD1 = factory.getOWLObjectSomeValuesFrom(R, factory.getOWLThing());
                String classNameD1 = base + "#some_" + nameRShort;
                OWLClass D1 = factory.getOWLClass(IRI.create(classNameD1));
                OWLAxiom def1 = factory.getOWLEquivalentClassesAxiom(D1, expD1);  // map D1 to (\some R)
                man.addAxiom(merged1, def1);
                map.put(D1.getIRI().toString(), expD1);
                // add neg for D1
                String negClsNameD1 = base + "#neg_some_" + nameRShort;
                OWLClass negClsD1 = factory.getOWLClass(IRI.create(negClsNameD1));
                OWLClassExpression expComplD1 = D1.getObjectComplementOf();
                OWLAxiom negDefD1 = factory.getOWLEquivalentClassesAxiom(negClsD1, expComplD1);
                man.addAxiom(merged1, negDefD1);
                map.put(negClsNameD1, expComplD1);
            }
            // expression for R-
            if (!propertysWithRange.contains(nameR)) {
                OWLClassExpression expD2 = factory.getOWLObjectSomeValuesFrom(R.getInverseProperty(), factory.getOWLThing());
                // additianal class for  (\some R-)
                String classNameD2 = base + "#some_ivs_" + nameRShort;
                OWLClass D2 = factory.getOWLClass(IRI.create(classNameD2));
                // map D1 to (\some R) and D2 to (\some R-)
                OWLAxiom def2 = factory.getOWLEquivalentClassesAxiom(D2, expD2);
                man.addAxiom(merged1, def2);
                map.put(D2.getIRI().toString(), expD2);
                // add neg for D2
                String negClsNameD2 = base + "#neg_some_ivs_" + nameRShort;
                OWLClass negClsD2 = factory.getOWLClass(IRI.create(negClsNameD2));
                OWLClassExpression expComplD2 = D2.getObjectComplementOf();
                OWLAxiom negDefD2 = factory.getOWLEquivalentClassesAxiom(negClsD2, expComplD2);
                man.addAxiom(merged1, negDefD2);
                map.put(negClsNameD2, expComplD2);
            }
        }

        // inference D and neg D
        System.out.println("Infer D and neg D...");
        OWLOntology infOnt2 = reasonerUtil.classify(merged1, man);
        // merged1 and infOnt2
        System.out.println("merging infOnt2 to merged1...");
        OWLOntologyMerger merger2 = new OWLOntologyMerger(man);
        IRI mergedOntologyIRI2 = IRI.create("http://www.semanticweb.com/merged2");
        OWLOntology merged2 = merger2.createMergedOntology(man, mergedOntologyIRI2);
        //keep only the merged2
        man.removeOntology(merged1);
        man.removeOntology(infOnt2);
        // replace D, N with expressions
        System.out.println("Replace D and N with expressions...");
        Set<OWLSubClassOfAxiom> subclassof = merged2.getAxioms(AxiomType.SUBCLASS_OF);
        for (OWLSubClassOfAxiom s : subclassof) {
            OWLClassExpression sub = s.getSubClass();
            OWLClassExpression sup = s.getSuperClass();
            String subIRI = "";
            String supIRI = "";
            if (sub.isNamed()) {
                subIRI = ((OWLClass) sub).getIRI().toString();
            }
            if (sup.isNamed()) {
                supIRI = ((OWLClass) sup).getIRI().toString();
            }
            if (map.containsKey(subIRI) || map.containsKey(supIRI)) {
                OWLClassExpression recoverSub = map.getOrDefault(subIRI, sub);
                OWLClassExpression recoverSup = map.getOrDefault(supIRI, sup);
                OWLSubClassOfAxiom recoverAX = factory.getOWLSubClassOfAxiom(recoverSub, recoverSup);
                // Add the axiom to our ontology
                AddAxiom tmpaddAx = new AddAxiom(merged2, recoverAX);
                man.applyChange(tmpaddAx);
            }
        }
        // remove additional classes
        System.out.println("Removing D and N...");
        OWLEntityRemover remover = new OWLEntityRemover(merged2);
        for (OWLClass namedClass : merged2.getClassesInSignature()) {
            if (map.containsKey(namedClass.getIRI().toString())) {
                namedClass.accept(remover);
            }
        }
        man.applyChanges(remover.getChanges());
        // new schema = Schema.classification ( recover D and N)
        System.out.println("Infer recovered schema + delta ...");
        OWLOntology infOnt3 = reasonerUtil.classify(merged2, man);
        // merge new inferred atoms
        System.out.println("Merging infOnt3 and merged2 to merged3");
        IRI mergedOntologyIRI3 = IRI.create("http://www.semanticweb.com/merged3");
        OWLOntology merged3 = merger.createMergedOntology(man, mergedOntologyIRI3);
        man.removeOntology(merged2);
        man.removeOntology(infOnt3);
        // remove unwanted axioms like asymmetric etc.
        System.out.println("Removing additional properties ...");
        List<OWLAxiom> toRemoveAxiom3 = new ArrayList<OWLAxiom>();
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.EQUIVALENT_OBJECT_PROPERTIES));
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.REFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.IRREFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.TRANSITIVE_OBJECT_PROPERTY));
//        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES));
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.SUB_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.EQUIVALENT_CLASSES));
        for (OWLAxiom ax : toRemoveAxiom3) {
            RemoveAxiom removeAxiom = new RemoveAxiom(merged3, ax);
            man.applyChange(removeAxiom);
        }
        // remove redundants: a /sub b, b /sub c, a /sub c ---> delete a /sub c
//        redtUtil = new SubClassOfRedundant(merged.getAxioms(AxiomType.SUBCLASS_OF));
//        for (OWLAxiom ax: redtUtil.findRedundants()) {
//            RemoveAxiom removeAxiom = new RemoveAxiom(merged, ax);
//            man.applyChange(removeAxiom);
//        }
        saveOnto(merged3, "tbox_dllite.nt");
    }

    public void owl2reduce(String in_file) throws Exception {
        System.out.println("To reduce: " + in_file);
        // load ontology from file
        File initialFile = new File(in_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(inputStream);
        // remove annotations
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ont.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax : toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            man.applyChange(removeAxiom);
        }

        // remove unwanted axioms like asymmetric etc.
        System.out.println("Removing additional properties ...");
        List<OWLAxiom> toRemoveAxiom3 = new ArrayList<OWLAxiom>();
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.EQUIVALENT_OBJECT_PROPERTIES));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.REFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.IRREFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.TRANSITIVE_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.SUB_OBJECT_PROPERTY));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.DISJOINT_CLASSES));
        toRemoveAxiom3.addAll(ont.getAxioms(AxiomType.EQUIVALENT_CLASSES));
        for (OWLAxiom ax : toRemoveAxiom3) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            man.applyChange(removeAxiom);
        }
        saveOnto(ont, "tbox_reduce.nt");
    }
}
