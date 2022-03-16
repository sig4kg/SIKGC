import java.awt.image.Kernel;
import java.io.*;
import java.util.*;
//import com.clarkparsia.pellet.owlapiv3.PelletReasonerFactory;
import org.semanticweb.HermiT.Configuration;
import org.semanticweb.HermiT.Reasoner.ReasonerFactory;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.formats.OWLXMLDocumentFormat;
import org.semanticweb.owlapi.formats.TurtleDocumentFormat;
import org.semanticweb.owlapi.io.StringDocumentTarget;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
//import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
//import org.semanticweb.owlapi.reasoner.structural.StructuralReasonerFactory;
import org.semanticweb.owlapi.util.*;

import java.util.Random;

import uk.ac.manchester.cs.owl.owlapi.OWLSubClassOfAxiomImpl;


public class DLLite {
    private KoncludeUtil koncludeUtil;
    private String output_dir;

    public DLLite(String Konclude_bin, String output_dir) {
        this.koncludeUtil = new KoncludeUtil(Konclude_bin, output_dir);
        this.output_dir = output_dir;
    }

    public void owl2dlliteOrginal(String in_file, String out_file) throws Exception {
        System.out.println("To DL-lite: " + in_file);
        // load ontology from file
        File initialFile = new File(in_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(inputStream);
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
        // Now create restrictions to describe the class of individual object properties
        System.out.println("Creating D...");
        for (OWLObjectProperty R : ont.getObjectPropertiesInSignature()) {
            if (!R.isNamed()) {
                continue;
            }
            // expression for R and R-
            OWLClassExpression expD1 = factory.getOWLObjectSomeValuesFrom(R, factory.getOWLThing());
            OWLClassExpression expD2 = factory.getOWLObjectSomeValuesFrom(R.getInverseProperty(), factory.getOWLThing());
            // additianal class for (\some R) and (\some R-)
            String nameR = R.getNamedProperty().toStringID();
            if (nameR.contains("#")) {
                nameR = nameR.substring(nameR.lastIndexOf('#') + 1, nameR.length());
            } else {
                nameR = nameR.substring(nameR.lastIndexOf('/') + 1, nameR.length());
            }
            String classNameD1 = base + "#some_" + nameR;
            String classNameD2 = base + "#some_ivs_" + nameR;
            OWLClass D1 = factory.getOWLClass(IRI.create(classNameD1));
            OWLClass D2 = factory.getOWLClass(IRI.create(classNameD2));
            // map D1 to (\some R) and D2 to (\some R-)
            OWLAxiom def1 = factory.getOWLEquivalentClassesAxiom(D1, expD1);
            OWLAxiom def2 = factory.getOWLEquivalentClassesAxiom(D2, expD2);
            man.addAxiom(ont, def1);
            man.addAxiom(ont, def2);
            map.put(D1.getIRI().toString(), expD1);
            map.put(D2.getIRI().toString(), expD2);
        }
        // now create restriction to describe the named classes
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
        //save middle to owlxml
        System.out.println("Saving middle ontology " + out_file + ".xml");
        File inferredOntologyFile0 = new File(out_file + ".xml");
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile0)) {
            // We use the nt format as for the input ontology.
            OWLXMLDocumentFormat format = new OWLXMLDocumentFormat();
//            TurtleDocumentFormat format = new TurtleDocumentFormat();
            man.saveOntology(ont, format, outputStream);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

        // Schema + Delta, then inference
        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        ReasonerFactory rf = new ReasonerFactory();
        OWLReasoner reasoner = rf.createReasoner(ont, configuration); // It takes time to create Hermit reasoner
        System.out.println("Infer Schema + Delta...");
        reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY);
        List<InferredAxiomGenerator<? extends OWLAxiom>> gens = new ArrayList<InferredAxiomGenerator<? extends OWLAxiom>>();
        gens.add(new InferredSubClassAxiomGenerator());
        OWLOntology infOnt1 = man.createOntology();
        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, gens);
        iog.fillOntology(man.getOWLDataFactory(), infOnt1);
        // merge ont and infOnt1
        System.out.println("merging infOnt1 to ont...");
        OWLOntologyMerger merger = new OWLOntologyMerger(man);
        IRI mergedOntologyIRI1 = IRI.create("http://www.semanticweb.com/merged1");
        OWLOntology merged = merger.createMergedOntology(man, mergedOntologyIRI1);
        System.out.println("Removing ont and infOnt1...");
        man.removeOntology(ont);
        man.removeOntology(infOnt1);

//        // remove redundants: a /sub b, b /sub c, a /sub c ---> delete a /sub c
//        SubClassOfRedundant redtUtil = new SubClassOfRedundant(merged.getAxioms(AxiomType.SUBCLASS_OF));
//        List<OWLSubClassOfAxiom> toRemove = redtUtil.findRedundants();
//        for (OWLAxiom ax: toRemove) {
//            RemoveAxiom removeAxiom = new RemoveAxiom(merged, ax);
//            man.applyChange(removeAxiom);
//        }
        // replace D, N with expressions
        System.out.println("Replace D and N with expressions...");
        Set<OWLSubClassOfAxiom> subclassof = merged.getAxioms(AxiomType.SUBCLASS_OF);
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
                AddAxiom tmpaddAx = new AddAxiom(merged, recoverAX);
                man.applyChange(tmpaddAx);
            }
        }
        // remove additional classes
        System.out.println("Removing D and N...");
        OWLEntityRemover remover = new OWLEntityRemover(merged);
        for (OWLClass namedClass : merged.getClassesInSignature()) {
            if (map.containsKey(namedClass.getIRI().toString())) {
                namedClass.accept(remover);
            }
        }
        man.applyChanges(remover.getChanges());
        // new schema = Schema.classification ( recover D and N)
        System.out.println("Infer recovered schema + delta ...");
        OWLReasoner reasoner2 = rf.createReasoner(merged, configuration);
        reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY);
        List<InferredAxiomGenerator<? extends OWLAxiom>> gens2 =
                new ArrayList<InferredAxiomGenerator<? extends OWLAxiom>>();
        gens2.add(new InferredSubClassAxiomGenerator()); //B1 \in B2 or B1 \in \negB2
        OWLOntology infOnt2 = man.createOntology();
        // Now get the inferred ontology generator to generate some inferred
        // axioms for us (into our fresh ontology). We specify the reasoner that
        // we want to use and the inferred axiom generators that we want to use.
        InferredOntologyGenerator iog2 = new InferredOntologyGenerator(reasoner2, gens2);
        iog2.fillOntology(man.getOWLDataFactory(), infOnt2);
        // merge new inferred atoms
        System.out.println("Merging infOnt2 with last round merged...");
        IRI mergedOntologyIRI2 = IRI.create("http://www.semanticweb.com/merged2");
        merged = merger.createMergedOntology(man, mergedOntologyIRI2);
        // remove unwanted axioms like asymmetric etc.
        System.out.println("Removing additional properties ...");
        toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.EQUIVALENT_OBJECT_PROPERTIES));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.REFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.IRREFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.TRANSITIVE_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.SUB_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.DISJOINT_CLASSES));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.EQUIVALENT_CLASSES));

        for (OWLAxiom ax : toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(merged, ax);
            man.applyChange(removeAxiom);
        }
        // remove redundants: a /sub b, b /sub c, a /sub c ---> delete a /sub c
//        redtUtil = new SubClassOfRedundant(merged.getAxioms(AxiomType.SUBCLASS_OF));
//        for (OWLAxiom ax: redtUtil.findRedundants()) {
//            RemoveAxiom removeAxiom = new RemoveAxiom(merged, ax);
//            man.applyChange(removeAxiom);
//        }
        System.out.println("Saving new ontology " + out_file);
        File inferredOntologyFile = new File(out_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            // We use the nt format as for the input ontology.
//             NTriplesDocumentFormat format = new NTriplesDocumentFormat();
            TurtleDocumentFormat format = new TurtleDocumentFormat();
            man.saveOntology(merged, format, outputStream);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    public void owl2dllite(String in_file) throws Exception {
        System.out.println("To DL-lite: " + in_file);
        // load ontology from file
        File initialFile = new File(in_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(inputStream);
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
        OWLOntology infOnt1 = this.koncludeUtil.koncludeClassifier(ont, man);
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
        OWLOntology infOnt2 = this.koncludeUtil.koncludeClassifier(merged1, man);
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
        OWLOntology infOnt3 = this.koncludeUtil.koncludeClassifier(merged2, man);
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
        toRemoveAxiom3.addAll(merged3.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES));
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
        String out_file_name = this.output_dir + "tbox_dllite.nt";
        System.out.println("Saving new ontology " + out_file_name);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(out_file_name)) {
            // We use the nt format as for the input ontology.
            NTriplesDocumentFormat format = new NTriplesDocumentFormat();
//            TurtleDocumentFormat format = new TurtleDocumentFormat();
            man.saveOntology(merged3, format, outputStream);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }
}
