import java.io.*;
import java.util.*;

import ReasonerUtils.IReasonerUtil;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.util.*;
import uk.ac.manchester.cs.owl.owlapi.OWLOntologyManagerImpl;


public class DLLite {
    final private String output_dir;
    public OWLOntologyManager man;
    public OWLDataFactory dataFactory;
    private final OWLClass owlThing;

    public DLLite(String output_dir) {
        this.output_dir = output_dir;
        man = OWLManager.createOWLOntologyManager();
        dataFactory = man.getOWLDataFactory();
        owlThing = dataFactory.getOWLThing();
    }

    public OWLOntology loadOnto(String ontology_file) {
        File initialFile = new File(ontology_file);
        try (InputStream inputStream = new FileInputStream(initialFile)) {
            /* the stream holding the file content */
            return man.loadOntologyFromOntologyDocument(inputStream);
        } catch (OWLOntologyCreationException | IllegalArgumentException | IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    private void saveOnto(OWLOntology toSaveOnto, String fileName) {
        System.out.println("Saving new ontology " + this.output_dir + fileName);
        File inferredOntologyFile = new File(this.output_dir + fileName);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            // We use the nt format as for the input ontology.
            NTriplesDocumentFormat format = new NTriplesDocumentFormat();
            man.saveOntology(toSaveOnto, format, outputStream);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    private OWLClassExpression getDomain(OWLOntology ont, OWLObjectProperty p) {
        for (OWLAxiom ax : ont.getAxioms(p)) {
            if (ax.getAxiomType().equals(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                return ((OWLObjectPropertyDomainAxiom) ax).getDomain();
            }
        }
        return this.owlThing;
    }

    private OWLClassExpression getRange(OWLOntology ont, OWLObjectProperty p) {
        for (OWLAxiom ax : ont.getAxioms(p)) {
            if (ax.getAxiomType().equals(AxiomType.OBJECT_PROPERTY_RANGE)) {
                return ((OWLObjectPropertyRangeAxiom) ax).getRange();
            }
        }
        return this.owlThing;
    }

    private void addRandRivs(OWLOntology ont, Map<String, OWLObject> mapCache) {
        System.out.println("Creating D...");
        for (OWLObjectProperty R : ont.getObjectPropertiesInSignature()) {
            if (!R.isNamed()) {
                continue;
            }
            // expression for R and R-
            OWLClassExpression expD1 = dataFactory.getOWLObjectSomeValuesFrom(R, this.owlThing);
            OWLSubClassOfAxiom rpSub1 = dataFactory.getOWLSubClassOfAxiom(expD1, getDomain(ont, R));
            OWLClassExpression expD2 = dataFactory.getOWLObjectSomeValuesFrom(R.getInverseProperty(), this.owlThing);
            OWLSubClassOfAxiom rpSub2 = dataFactory.getOWLSubClassOfAxiom(expD2, getRange(ont, R));
            man.addAxiom(ont, rpSub1);
            man.addAxiom(ont, rpSub2);
            // additianal class for (\some R) and (\some R-)
            String nameR = R.getNamedProperty().getIRI().toString();
            List<String> splits = splitIRI(nameR);
            String classNameD1 = splits.get(0) + "#some_" + splits.get(1);
            String classNameD2 = splits.get(0) + "#some_ivs_" + splits.get(1);
            OWLClass D1 = dataFactory.getOWLClass(IRI.create(classNameD1));
            OWLClass D2 = dataFactory.getOWLClass(IRI.create(classNameD2));
            // map D1 to (\some R) and D2 to (\some R-)
            OWLAxiom def1 = dataFactory.getOWLEquivalentClassesAxiom(D1, expD1);
            OWLAxiom def2 = dataFactory.getOWLEquivalentClassesAxiom(D2, expD2);
            man.addAxiom(ont, def1);
            man.addAxiom(ont, def2);
            mapCache.put(D1.getIRI().toString(), expD1);
            mapCache.put(D2.getIRI().toString(), expD2);
            // R-
//            OWLObjectPropertyExpression ivs_R = R.getInverseProperty();
//            String ivs_R_Name = splits.get(0) + "#ivs_" + splits.get(1);
//            OWLObjectProperty ivs_R_p = dataFactory.getOWLObjectProperty(IRI.create(ivs_R_Name));
//            OWLAxiom def3 = dataFactory.getOWLEquivalentObjectPropertiesAxiom(ivs_R_p, ivs_R);
//            man.addAxiom(ont, def3);
//            OWLAxiom def4 = dataFactory.getOWLEquivalentClassesAxiom(D2, dataFactory.getOWLObjectSomeValuesFrom(ivs_R_p, this.owlThing));
//            man.addAxiom(ont, def4);
//            mapCache.put(ivs_R_p.getIRI().toString(), ivs_R);
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

    private void addNegD(OWLOntology ont, Map<String, OWLObject> mapCache) {
        System.out.println("Creating neg D...");
        for (OWLClass cls : ont.getClassesInSignature()) {
            if (!cls.isNamed()) {
                continue;
            }
            String clsIRIStr = cls.getIRI().toString();
            List<String> splits = splitIRI(clsIRIStr);
            String negClsName = splits.get(0) + "#neg_" + splits.get(1);
            OWLClass negCls = dataFactory.getOWLClass(IRI.create(negClsName));
            OWLClassExpression expCompl = ((OWLClassExpression) mapCache.getOrDefault(clsIRIStr, cls)).getObjectComplementOf();
            OWLAxiom negDef = dataFactory.getOWLEquivalentClassesAxiom(negCls, expCompl);
            man.addAxiom(ont, negDef);
            mapCache.put(negCls.getIRI().toString(), expCompl);
        }
    }

    private void flattenInversof(OWLOntology ontology) {
        for (OWLInverseObjectPropertiesAxiom axIvs : ontology.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES)) {
            OWLObjectPropertyExpression r1 = axIvs.getFirstProperty();
            OWLObjectPropertyExpression r2 = axIvs.getSecondProperty();
            String nr1 = r1.getNamedProperty().getIRI().toString();
            List<String> splits1 = splitIRI(nr1);
            String some_r1 = splits1.get(0) + "#some_" + splits1.get(1);
            String some_ivs_r1 = splits1.get(0) + "#some_ivs_" + splits1.get(1);
            String nr2 = r2.getNamedProperty().getIRI().toString();
            List<String> splits2 = splitIRI(nr2);
            String some_r2 = splits2.get(0) + "#some_" + splits2.get(1);
            String some_ivs_r2 = splits2.get(0) + "#some_ivs_" + splits2.get(1);
            OWLAxiom ax1 = dataFactory.getOWLSubClassOfAxiom(dataFactory.getOWLClass(some_r2), dataFactory.getOWLClass(some_ivs_r1));
            OWLAxiom ax2 = dataFactory.getOWLSubClassOfAxiom(dataFactory.getOWLClass(some_ivs_r2), dataFactory.getOWLClass(some_r1));
            man.addAxiom(ontology, ax1);
            man.addAxiom(ontology, ax2);
            axIvs.asSubObjectPropertyOfAxioms().forEach((ax) -> {
                man.addAxiom(ontology, ax);});
        }
    }

    private void flattenSymetricP(OWLOntology ontology) {
        for (OWLSymmetricObjectPropertyAxiom axSym : ontology.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY)) {
            axSym.asSubPropertyAxioms().forEach((ax) -> man.addAxiom(ontology, ax));
        }
    }

    public void owl2dllite(IReasonerUtil reasonerUtil, String in_file) throws Exception {
        System.out.println("To DL-lite: " + in_file);
        // load ontology from file
        OWLOntology ont = loadOnto(in_file);
        OWLOntology merged2 = ont2dllite(reasonerUtil, ont);
        saveOnto(merged2, "tbox_dllite.nt");
    }

    public OWLOntology inferAdditionalClass(IReasonerUtil reasonerUtil, OWLOntology ont, Map<String, OWLObject> mapCache) {
        // Now create restrictions to describe the class of individual object properties
        addRandRivs(ont, mapCache);
        addNegD(ont, mapCache);
        flattenSymetricP(ont);
        flattenInversof(ont);
        // Schema + Delta, then inference
        OWLOntology infOnt1 = reasonerUtil.classify(ont, man);
        return infOnt1;
    }

    private OWLOntology inferReplacedClass(IReasonerUtil reasonerUtil, OWLOntology merged1, Map<String, OWLObject> mapCache) {
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
            if (mapCache.containsKey(subIRI) || mapCache.containsKey(supIRI)) {
                OWLClassExpression recoverSub = (OWLClassExpression)(mapCache.getOrDefault(subIRI, sub));
                OWLClassExpression recoverSup = (OWLClassExpression)(mapCache.getOrDefault(supIRI, sup));
                OWLSubClassOfAxiom recoverAX = dataFactory.getOWLSubClassOfAxiom(recoverSub, recoverSup);
                // Add the axiom to our ontology
                AddAxiom tmpaddAx = new AddAxiom(merged1, recoverAX);
                man.applyChange(tmpaddAx);
            }
        }
        // remove additional classes
        System.out.println("Removing D and N...");
        OWLEntityRemover remover = new OWLEntityRemover(merged1);
        for (OWLClass namedClass : merged1.getClassesInSignature()) {
            if (mapCache.containsKey(namedClass.getIRI().toString())) {
                namedClass.accept(remover);
            }
        }
        man.applyChanges(remover.getChanges());
        // new schema = Schema.classification ( recover D and N)
        System.out.println("Infer recovered schema + delta ...");

        //B1 \in B2 or B1 \in \negB2
//        OWLOntology infOnt2 = this.koncludeUtil.koncludeClassifier(merged1, man);
        OWLOntology infOnt2 = reasonerUtil.classify(merged1, man);
        return infOnt2;
    }

    public OWLOntology ont2dllite(IReasonerUtil reasonerUtil, OWLOntology ont) throws OWLOntologyCreationException {
        if (!man.getOntologies().contains(ont)) {

        }
        // remove annotations
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ont.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax : toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            this.man.applyChange(removeAxiom);
        }
        // a map to keep additional class IRI to class expression
        Map<String, OWLObject> map = new HashMap<>();
        OWLOntology infOnt1 = inferAdditionalClass(reasonerUtil, ont, map);

        // merge ont and infOnt1
        System.out.println("merging infOnt1 to ont...");
        OWLOntologyMerger merger = new OWLOntologyMerger(man);
        IRI mergedOntologyIRI1 = IRI.create("http://www.semanticweb.com/merged1");
        OWLOntology merged1 = merger.createMergedOntology(man, mergedOntologyIRI1);
        System.out.println("Removing ont and infOnt1...");
        man.removeOntology(ont);
        man.removeOntology(infOnt1);
        // replace additional class with expressions and infer
        inferReplacedClass(reasonerUtil, merged1, map);

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
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.EQUIVALENT_OBJECT_PROPERTIES));
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.REFLEXIVE_OBJECT_PROPERTY));
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.IRREFLEXIVE_OBJECT_PROPERTY));
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.TRANSITIVE_OBJECT_PROPERTY));
//        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.SUB_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.DISJOINT_CLASSES));
        toRemoveAxiom.addAll(merged2.getAxioms(AxiomType.EQUIVALENT_CLASSES));

        for (OWLAxiom ax : toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(merged2, ax);
            man.applyChange(removeAxiom);
        }
        return merged2;
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
