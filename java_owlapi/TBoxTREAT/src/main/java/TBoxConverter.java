import org.semanticweb.HermiT.Configuration;
import org.semanticweb.HermiT.Reasoner;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.formats.RDFXMLDocumentFormat;
import org.semanticweb.owlapi.formats.TurtleDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import org.semanticweb.owlapi.util.*;
import uk.ac.manchester.cs.jfact.JFactFactory;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;

public class TBoxConverter {
    public static void toNT(String in_file, String out_file) throws Exception {
        System.out.println("convert to NT file: " + in_file);
        File initialFile = new File(in_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(inputStream);

        NTriplesDocumentFormat nTriplesFormat = new NTriplesDocumentFormat();
        File inferredOntologyFile = new File(out_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            manager.saveOntology(ontology, nTriplesFormat, outputStream);
        } catch (OWLOntologyStorageException e) {
            e.printStackTrace();
            throw e;
        }
    }

    public static void getTBoxSubset(String in_tbox_file, String out_tbox_file, String subset_type_file, String subset_property_file)  throws Exception {
        List<String> toKeepClasses = new ArrayList<>();
        List<String> toKeepProperties = new ArrayList<>();
        try (Stream<String> lines1 = Files.lines(Paths.get(subset_type_file))) {
            lines1.forEach(toKeepClasses::add);
        }
        try (Stream<String> lines2 = Files.lines(Paths.get(subset_property_file))) {
            lines2.forEach(toKeepProperties::add);
        }

        File initialFile = new File(in_tbox_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_tbox_file);
        }
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(inputStream);
        // remove annotations, datatype
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ont.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax: toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            man.applyChange(removeAxiom);
        }

        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        OWLDataFactory dataFactory = man.getOWLDataFactory();
        Reasoner.ReasonerFactory reasonerFactory = new Reasoner.ReasonerFactory();
        OWLReasoner reasoner = reasonerFactory.createReasoner(ont, configuration); // It takes time to create Hermit reasoner

        //get  all parent classes
        List<String> moreClasses = new ArrayList<>();
        for (String class_uri : toKeepClasses) {
            OWLClass c = dataFactory.getOWLClass(class_uri);
            NodeSet<OWLClass> sups = reasoner.getSuperClasses(c);
            for (OWLClass sup : sups.getFlattened()) {
                moreClasses.add(sup.toString());
            }
        }
        List<String> toExclude =  new ArrayList<>(Arrays.asList("http://dbpedia.org/class/yago/",
                "http://www.ontologydesignpatterns.org/" ,
                "http://www.wikidata.org/"));
        moreClasses.forEach((String uri) -> {
            if (!toKeepClasses.contains(uri) && !toExclude.stream().anyMatch(uri::contains)) {toKeepClasses.add(uri);};
        });
        List<String> moreOps = new ArrayList<>();
        for (String pro_uri : toKeepProperties) {
            OWLObjectProperty op = dataFactory.getOWLObjectProperty(pro_uri);
            NodeSet<OWLObjectPropertyExpression> pSups = reasoner.getSuperObjectProperties(op.getNamedProperty(), false);
            for (OWLObjectPropertyExpression sup : pSups.getFlattened()) {
                moreOps.add(sup.toString());
            }
        }
        moreOps.forEach((String uri) -> {
            if (!toKeepProperties.contains(uri)) {toKeepProperties.add(uri);};
        });

        OWLEntityRemover entRemover = new OWLEntityRemover(ont);
        ont.classesInSignature().forEach(element -> {
            if (!toKeepClasses.contains(element.getIRI().toString())) {
                element.accept(entRemover);
                man.applyChanges(entRemover.getChanges());
            };
        });

        OWLEntityRemover entRemover2 = new OWLEntityRemover(ont);
        ont.datatypesInSignature().forEach(element -> {
            if (!toKeepClasses.contains(element.getIRI().toString())) {
                element.accept(entRemover2);
                man.applyChanges(entRemover2.getChanges());
            };
        });

        List<OWLAxiom> toRemoveAxiom2 = new ArrayList<OWLAxiom>();
        ont.objectPropertiesInSignature().forEach(element -> {
            if (!toKeepProperties.contains(element.getIRI().toString())) {
                toRemoveAxiom2.addAll(ont.getAxioms(element));
            };
        });

        ont.dataPropertiesInSignature().forEach(element -> {
            if (!toKeepProperties.contains(element.getIRI().toString())) {
                toRemoveAxiom2.addAll(ont.getAxioms(element));
            };
        });

        for (OWLAxiom ax: toRemoveAxiom2) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            man.applyChange(removeAxiom);
        }

        TurtleDocumentFormat format = new TurtleDocumentFormat();
        File inferredOntologyFile = new File(out_tbox_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            man.saveOntology(ont, format, outputStream);
        } catch (OWLOntologyStorageException e) {
            e.printStackTrace();
            throw e;
        }

    }
}
