import org.semanticweb.HermiT.Configuration;
import org.semanticweb.HermiT.Reasoner;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.formats.RDFXMLDocumentFormat;
import org.semanticweb.owlapi.formats.TurtleDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.*;
import org.semanticweb.owlapi.util.*;
import uk.ac.manchester.cs.jfact.JFactFactory;
import uk.ac.manchester.cs.owl.owlapi.OWLEquivalentObjectPropertiesAxiomImpl;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
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
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ontology.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax: toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ontology, ax);
            manager.applyChange(removeAxiom);
        }
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


    public static void getEquavalentWikiID(String in_tbox_file, String in_property_file, String out_file) throws IOException, OWLOntologyCreationException {
        List<String> properties = new ArrayList<>();
        try (Stream<String> lines1 = Files.lines(Paths.get(in_property_file))) {
            lines1.forEach(x -> {
                if (x.startsWith("http://")) {
                    properties.add(x);
                }
            });
        } catch (IOException e) {
            e.printStackTrace();
        }

        File initialFile = new File(in_tbox_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_tbox_file);
        }
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(inputStream);

        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        OWLDataFactory dataFactory = man.getOWLDataFactory();
        Reasoner.ReasonerFactory rf = new Reasoner.ReasonerFactory();
        OWLReasoner reasoner = rf.createReasoner(ont, configuration);
        Map<String, List<String>> mapUri2Ids = new HashMap<>();
        for (String rel_uri : properties) {
            OWLObjectProperty p = dataFactory.getOWLObjectProperty(rel_uri);
            Node<OWLObjectPropertyExpression> equ_ps = reasoner.getEquivalentObjectProperties(p);
            List<String> eqps = new ArrayList<>();
            for (OWLObjectPropertyExpression ep : equ_ps) {
                String strp = ep.getNamedProperty().toString();
                if (strp.contains("wikidata")) {
                    String[] equURI = strp.split("/", -1);
                    eqps.add(equURI[equURI.length -1]);
                }
            }
            if (eqps.size() > 0) {
                mapUri2Ids.put(rel_uri, eqps);
            }
        }
        File f = new File(out_file);
        FileWriter fw = new FileWriter(f);
        PrintWriter pw = new PrintWriter(fw);
        for (Map.Entry<String, List<String>> entry : mapUri2Ids.entrySet()) {
            String dbpediaURI = entry.getKey();
            List<String> wikiId = entry.getValue();
            pw.print(dbpediaURI + "\t");
            for(String wid: wikiId) {
                pw.print(wid  + "\t");
            }
            pw.println();
        }
        pw.close();
    }


    public static void getTBoxSubset(String in_tbox_file, String out_tbox_file, String subset_type_file, String subset_property_file)  throws Exception {
        List<String> toKeepClasses = new ArrayList<>();
        List<String> toKeepProperties = new ArrayList<>();
        try (Stream<String> lines1 = Files.lines(Paths.get(subset_type_file))) {
            lines1.forEach(x -> {
                if (x.startsWith("http://")) {
                    toKeepClasses.add(x);
                }
            });
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
        // remove annotations
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ont.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax: toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            man.applyChange(removeAxiom);
        }
        List<String> toExclude =  new ArrayList<>(Arrays.asList("http://dbpedia.org/class/yago/",
                "http://www.ontologydesignpatterns.org/" ,
                "http://www.wikidata.org/"));
        // remove some classes
        System.out.println("remove other classes");
        OWLEntityRemover entRemover = new OWLEntityRemover(ont);
        ont.classesInSignature().forEach(element -> {
            if (element.isNamed() && toExclude.stream().anyMatch(element.getIRI().toString()::contains)) {
                element.accept(entRemover);
                man.applyChanges(entRemover.getChanges());
            };
        });

        // remove datatypes
        System.out.println("remove datatypes");
        OWLEntityRemover entRemover2 = new OWLEntityRemover(ont);
        ont.datatypesInSignature().forEach(element -> {
            if (!toKeepClasses.contains(element.getIRI().toString()) && element.isNamed()) {
                element.accept(entRemover2);
                man.applyChanges(entRemover2.getChanges());
            };
        });

        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        OWLDataFactory dataFactory = man.getOWLDataFactory();
        Reasoner.ReasonerFactory reasonerFactory = new Reasoner.ReasonerFactory();
        OWLReasoner reasoner = reasonerFactory.createReasoner(ont, configuration); // It takes time to create Hermit reasoner
        // materialise TBox
        System.out.println("Materialising.");
        reasoner.precomputeInferences(
                InferenceType.CLASS_HIERARCHY,
                InferenceType.CLASS_ASSERTIONS,
                InferenceType.OBJECT_PROPERTY_HIERARCHY,
                InferenceType.OBJECT_PROPERTY_ASSERTIONS
        );
        List<InferredAxiomGenerator<? extends OWLAxiom>> generators = new ArrayList<>();
        generators.add(new InferredSubClassAxiomGenerator());
        generators.add(new InferredDisjointClassesAxiomGenerator());
        generators.add(new InferredEquivalentClassAxiomGenerator());
        generators.add(new InferredEquivalentObjectPropertyAxiomGenerator());
        generators.add(new InferredInverseObjectPropertiesAxiomGenerator());
        generators.add(new InferredObjectPropertyCharacteristicAxiomGenerator());
        generators.add(new InferredSubObjectPropertyAxiomGenerator());
        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, generators);
        OWLOntology inferredAxiomsOntology = man.createOntology();
        iog.fillOntology(dataFactory, inferredAxiomsOntology);
        System.out.println("Merge materialized  TBox.");
        OWLOntologyMerger merger = new OWLOntologyMerger(man);
        IRI mergedOntologyIRI1 = IRI.create("http://www.semanticweb.com/merged");
        ont = merger.createMergedOntology(man, mergedOntologyIRI1);
        //get  all parent classes
        List<String> moreClasses = new ArrayList<>();
        for (String class_uri : toKeepClasses) {
            OWLClass c = dataFactory.getOWLClass(class_uri);
            NodeSet<OWLClass> sups = reasoner.getSuperClasses(c);
            for (OWLClass sup : sups.getFlattened()) {
                moreClasses.add(sup.toString());
            }
        }

        moreClasses.forEach((String uri) -> {
            if (!toKeepClasses.contains(uri) && !toExclude.stream().anyMatch(uri::contains)) {toKeepClasses.add(uri);};
        });

        //get all parent properties
        List<String> moreOps = new ArrayList<>();
        for (String pro_uri : toKeepProperties) {
            OWLObjectProperty op = dataFactory.getOWLObjectProperty(pro_uri);
            NodeSet<OWLObjectPropertyExpression> pSups = reasoner.getSuperObjectProperties(op.getNamedProperty(), false);
            for (OWLObjectPropertyExpression sup : pSups.getFlattened()) {
                moreOps.add(sup.toString());
            }
        }

        //get reverse properties
        //get all parent properties
        for (String pro_uri : toKeepProperties) {
            OWLObjectProperty op = dataFactory.getOWLObjectProperty(pro_uri);
            OWLObjectPropertyExpression inv = reasoner.getInverseObjectProperties(op).getRepresentativeElement();
            if (inv.isNamed()) {
                moreOps.add(inv.toString());
            }
        }
        moreOps.forEach((String uri) -> {
            if (!toKeepProperties.contains(uri) &&
                    !uri.contains("http://www.ontologydesignpatterns.org/")
                    && ! uri.contains("owl:topObjectProperty"))
            {toKeepProperties.add(uri);};
        });

        // fix domain and range
        ArrayList<String> toFixDomain = new ArrayList<>();
        ArrayList<String> toFixRange = new ArrayList<>();
        Set<OWLAxiom> domainsAndRanges = new HashSet<OWLAxiom>();
        for (String p_uri : toKeepProperties) {
            OWLObjectProperty op = dataFactory.getOWLObjectProperty(p_uri);
            Set<OWLObjectPropertyDomainAxiom> pd = ont.getObjectPropertyDomainAxioms(op);
            if (pd.size() == 0) {
                toFixDomain.add(p_uri);
            } else {
                pd.forEach((OWLObjectPropertyDomainAxiom ax) ->{
                    String d = ax.getDomain().toString();
                    if (toKeepClasses.contains(d)) {
                        toKeepClasses.add(d);
                    }
                });
            }
            Set<OWLObjectPropertyRangeAxiom> pr = ont.getObjectPropertyRangeAxioms(op);
            if (pr.size() == 0) {
                toFixRange.add(p_uri);
            } else {
                pr.forEach((OWLObjectPropertyRangeAxiom ax) ->{
                    String d = ax.getRange().toString();
                    if (toKeepClasses.contains(d)) {
                        toKeepClasses.add(d);
                    }
                });
            }
        }

        // remove other prefix classes
        System.out.println("remove other classes");
        OWLEntityRemover entRemover1 = new OWLEntityRemover(ont);
        ont.classesInSignature().forEach(element -> {
            if (!toKeepClasses.contains(element.getIRI().toString()) && element.isNamed()) {
                element.accept(entRemover1);
                man.applyChanges(entRemover1.getChanges());
            };
        });

        //remove other properties
        System.out.println("remove other properties");
        OWLEntityRemover entRemover3 = new OWLEntityRemover(ont);
        ont.objectPropertiesInSignature().forEach(element -> {
            if (!toKeepProperties.contains(element.getIRI().toString())) {
                element.accept(entRemover3);
                man.applyChanges(entRemover3.getChanges());
            };
        });
        ont.dataPropertiesInSignature().forEach(element -> {
            if (!toKeepProperties.contains(element.getIRI().toString())) {
                element.accept(entRemover3);
                man.applyChanges(entRemover3.getChanges());
            };
        });

        NTriplesDocumentFormat format = new NTriplesDocumentFormat();
        File inferredOntologyFile = new File(out_tbox_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            man.saveOntology(ont, format, outputStream);
        } catch (OWLOntologyStorageException e) {
            e.printStackTrace();
            throw e;
        }
        File f = new File("fixDomain.txt");
        FileWriter fw = new FileWriter(f);
        PrintWriter pw = new PrintWriter(fw);
        toFixDomain.forEach(pw::println);
        pw.close();

        File f2 = new File("fixRange.txt");
        FileWriter fw2 = new FileWriter(f2);
        PrintWriter pw2 = new PrintWriter(fw2);
        toFixRange.forEach(pw2::println);
        pw2.close();
    }
}
