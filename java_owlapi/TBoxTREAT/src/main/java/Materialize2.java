import org.semanticweb.HermiT.Configuration;
import org.semanticweb.HermiT.Reasoner.ReasonerFactory;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.formats.TurtleDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.util.*;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public class Materialize2 {
    public static void checkConsistency(String in_tbox_file, String in_abox_file, String out_file) throws Exception {
        System.out.println("Materializing: " + in_tbox_file + " and " + in_abox_file);
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        if (!in_abox_file.equals("")) {
            File initialFileA = new File(in_abox_file);
            InputStream inputStreamA = new FileInputStream(initialFileA);
            OWLOntology ontologyA = manager.loadOntologyFromOntologyDocument(inputStreamA);
            if (inputStreamA == null) {
                throw new IllegalArgumentException("file not found! " + in_abox_file);
            }
        } else {
            System.out.println("no abox for materialization, will use tbox only.");
        }

        File initialFileB = new File(in_tbox_file);
        InputStream inputStreamB = new FileInputStream(initialFileB);
        // the stream holding the file content
        if (inputStreamB == null) {
            throw new IllegalArgumentException("file not found! " + in_tbox_file);
        }
        OWLOntology ontologyB = manager.loadOntologyFromOntologyDocument(inputStreamB);
        // merge tbox and abox
        System.out.println("Merge tbox and abox.");
        OWLOntologyMerger merger = new OWLOntologyMerger(manager);
        IRI mergedOntologyIRI1 = IRI.create("http://www.semanticweb.com/merged");
        OWLOntology ontology = merger.createMergedOntology(manager, mergedOntologyIRI1);
        // create Hermit reasoner
        OWLDataFactory df = manager.getOWLDataFactory();
        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        ReasonerFactory rf = new ReasonerFactory();
        OWLReasoner reasoner = rf.createReasoner(ontology, configuration);
        boolean consistencyCheck = reasoner.isConsistent();
        if (consistencyCheck) {
            System.out.println("tbox and abox are consistent.");
        } else {
            System.out.println("tbox and abox are not consistent.");
        }
        File ontologyFile = new File(out_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(ontologyFile)) {
            // We use the nt format as for the input ontology.
            NTriplesDocumentFormat format = new NTriplesDocumentFormat();
//            TurtleDocumentFormat format = new TurtleDocumentFormat();
//            N3DocumentFormat format = new N3DocumentFormat();
            manager.saveOntology(ontology, format, outputStream);
            System.out.println("Output saved: " + out_file);
        } catch (Exception e) {
            System.out.println(e.getMessage());
            e.printStackTrace();
        }
    }
    public static void materialize(String in_tbox_file, String in_abox_file, String out_file) throws Exception {
        System.out.println("Materializing: " + in_tbox_file + " and " + in_abox_file);
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        File initialFileB = new File(in_tbox_file);
        InputStream inputStreamB = new FileInputStream(initialFileB);
        // the stream holding the file content
        if (inputStreamB == null) {
            throw new IllegalArgumentException("file not found! " + in_tbox_file);
        }
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(inputStreamB);
        if (!in_abox_file.equals("")) {
            File initialFileA = new File(in_abox_file);
            InputStream inputStreamA = new FileInputStream(initialFileA);
            if (inputStreamA == null) {
                throw new IllegalArgumentException("file not found! " + in_abox_file);
            }
            // the object property converted to annotation property automaticly
//            OWLOntology ontologyA = manager.loadOntologyFromOntologyDocument(inputStreamA);
            // merge abox one by one
            System.out.println("Merge tbox and abox.");
            OWLOntologyMerger merger = new OWLOntologyMerger(manager);
            IRI mergedOntologyIRI1 = IRI.create("http://www.semanticweb.com/merged");
            ontology = merger.createMergedOntology(manager, mergedOntologyIRI1);
        } else {
            System.out.println("no extra abox file for materialization, will use one file only.");
        }
        // create Hermit reasoner
        OWLDataFactory df = manager.getOWLDataFactory();
        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        ReasonerFactory rf = new ReasonerFactory();
        OWLReasoner reasoner = rf.createReasoner(ontology, configuration);
        boolean consistencyCheck = reasoner.isConsistent();
        if (!consistencyCheck) {
            System.out.println("Inconsistent input Ontology, Please check the OWL File");
        }
//        for (OWLNamedIndividual ind : ontology.getIndividualsInSignature()){
//            Set<OWLObjectPropertyAssertionAxiom> s = ontology.getObjectPropertyAssertionAxioms(ind);
//            if(s.size() > 0) {
//                System.out.println("stop");
//            }
//        }

        System.out.println("Materialising, may take time......");
        reasoner.precomputeInferences(
                InferenceType.CLASS_HIERARCHY,
                InferenceType.CLASS_ASSERTIONS,
                InferenceType.OBJECT_PROPERTY_HIERARCHY,
                InferenceType.OBJECT_PROPERTY_ASSERTIONS
        );
        List<InferredAxiomGenerator<? extends OWLAxiom>> generators = new ArrayList<>();
//        generators.add(new InferredSubClassAxiomGenerator());
        generators.add(new InferredClassAssertionAxiomGenerator());
//        generators.add(new InferredDisjointClassesAxiomGenerator());
//        generators.add(new InferredEquivalentClassAxiomGenerator());
//        generators.add(new InferredEquivalentObjectPropertyAxiomGenerator());
//        generators.add(new InferredInverseObjectPropertiesAxiomGenerator());
//        generators.add(new InferredObjectPropertyCharacteristicAxiomGenerator());
//        generators.add(new InferredSubObjectPropertyAxiomGenerator());

//         NOTE: InferredPropertyAssertionGenerator significantly slows down
//         inference computation
        generators.add(new org.semanticweb.owlapi.util.InferredPropertyAssertionGenerator());

//        generators.add(new InferredDataPropertyCharacteristicAxiomGenerator());
//        generators.add(new InferredEquivalentDataPropertiesAxiomGenerator());
//        generators.add(new InferredSubDataPropertyAxiomGenerator());

        List<InferredIndividualAxiomGenerator<? extends OWLIndividualAxiom>> individualAxioms =
                new ArrayList<>();
        generators.addAll(individualAxioms);

        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, generators);
        OWLOntology inferredAxiomsOntology = manager.createOntology();
        iog.fillOntology(df, inferredAxiomsOntology);
        File inferredOntologyFile = new File(out_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            // We use the nt format as for the input ontology.
            NTriplesDocumentFormat format = new NTriplesDocumentFormat();
//            TurtleDocumentFormat format = new TurtleDocumentFormat();
//            N3DocumentFormat format = new N3DocumentFormat();
            manager.saveOntology(inferredAxiomsOntology, format, outputStream);
            System.out.println("Output saved: " + out_file);
        } catch (Exception e) {
            System.out.println(e.getMessage());
            e.printStackTrace();
        }
        System.out.println("Done with materialization");
    }
}