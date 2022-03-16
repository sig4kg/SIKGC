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
    public static void checkConsistency(String in_file, String out_file) throws Exception {
        System.out.println("Materializing: " + in_file);
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        File initialFileB = new File(in_file);
        InputStream inputStreamB = new FileInputStream(initialFileB);
        // the stream holding the file content
        if (inputStreamB == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(inputStreamB);
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
            manager.saveOntology(ontology, format, outputStream);
            System.out.println("Output saved: " + out_file);
        } catch (Exception e) {
            System.out.println(e.getMessage());
            e.printStackTrace();
        }
    }
    public static void materialize(String in_file, String out_file) throws Exception {
        System.out.println("Materializing: " + in_file);
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        File initialFileB = new File(in_file);
        InputStream inputStreamB = new FileInputStream(initialFileB);
        // the stream holding the file content
        if (inputStreamB == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(inputStreamB);
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
        System.out.println("Materialising type assertions, may take time......");
        reasoner.precomputeInferences(
                InferenceType.CLASS_ASSERTIONS
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
//        generators.add(new org.semanticweb.owlapi.util.InferredPropertyAssertionGenerator());
//        generators.add(new InferredDataPropertyCharacteristicAxiomGenerator());
//        generators.add(new InferredEquivalentDataPropertiesAxiomGenerator());
//        generators.add(new InferredSubDataPropertyAxiomGenerator());

        List<InferredIndividualAxiomGenerator<? extends OWLIndividualAxiom>> individualAxioms =
                new ArrayList<>();
        generators.addAll(individualAxioms);

        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, generators);
        OWLOntology inferredAxiomsOntology = manager.createOntology();
        iog.fillOntology(df, inferredAxiomsOntology);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(out_file)) {
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