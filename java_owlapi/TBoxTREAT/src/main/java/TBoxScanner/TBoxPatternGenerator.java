package TBoxScanner;

import TBoxScanner.deprecates.*;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import uk.ac.manchester.cs.jfact.JFactFactory;
import uk.ac.manchester.cs.owl.owlapi.OWLLiteralImplPlain;

import java.io.*;
import java.util.*;
import java.util.function.Supplier;

/*
     Script that do TBoxScanner.

      */
public class TBoxPatternGenerator {
    String ontology_file = "";
    String out_dir;
    OWLOntology ont = null;
    OWLReasoner reasoner;
    OWLDataFactory factory;

    public TBoxPatternGenerator(String ontoloty_file, String output_dir) {
        this.ontology_file = ontoloty_file;
        this.out_dir = output_dir;
    }

    public TBoxPatternGenerator(OWLOntology ontoloty, OWLReasoner reasoner, OWLDataFactory factory, String output_dir) {
        this.ont = ontoloty;
        this.out_dir = output_dir;
        this.reasoner = reasoner;
        this.factory = factory;
    }

    private void loadOnto() {
        try {
            OWLOntologyManager man = OWLManager.createOWLOntologyManager();
            InputStream is = this.readFileAsStream(ontology_file);
            ont = man.loadOntologyFromOntologyDocument(is);
            OWLReasonerFactory rf = new JFactFactory();
            reasoner = rf.createReasoner(ont);
            factory = man.getOWLDataFactory();
        } catch (OWLOntologyCreationException | IllegalArgumentException | FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    public void getAllClasses() {
        try {
            if (ont == null && ontology_file.length() > 0) {
                loadOnto();
            }
            Set<OWLAnnotationAssertionAxiom> all_axioms = ont.getAxioms(AxiomType.ANNOTATION_ASSERTION);
            File rel2text_txt = new File(out_dir + "/rel2text.txt");
            FileWriter rel2text_f = new FileWriter(rel2text_txt);
            PrintWriter rel2text_w = new PrintWriter(rel2text_f);
            for (OWLAnnotationAssertionAxiom axi : all_axioms) {
                if (axi.getProperty().isComment() && ((OWLLiteralImplPlain) (axi.getValue())).getLang().equals("en")) {
                    String subj = ((IRI) (axi.getSubject())).toString();
                    String comment = ((OWLLiteralImplPlain) (axi.getValue())).getLiteral();
                    if (comment != "none") {
                        rel2text_w.print(subj + "\t" + comment + "\n");
                    }
                }
            }
            rel2text_w.close();
            System.out.println(out_dir);
            File all_classes = new File(out_dir + "/AllClasses.txt");
            FileWriter FW_classes = new FileWriter(all_classes);
            PrintWriter pw_class = new PrintWriter(FW_classes);
            ont.classesInSignature().forEach(element -> {
                pw_class.print(element.getIRI().toString() + '\n');
            });
            pw_class.close();
            File all_op = new File(out_dir + "/AllObjectProperties.txt");
            FileWriter fw_op = new FileWriter(all_op);
            PrintWriter pw_op = new PrintWriter(fw_op);
            ont.objectPropertiesInSignature().forEach(element -> {
                pw_op.print(element.getIRI().toString() + '\n');
            });
            pw_op.close();
        } catch (IOException | IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    public void GeneratePatterns() {
        try {
            if (ont == null && ontology_file.length() > 0) {
                loadOnto();
            }
            ArrayList<Supplier<BasePattern>> patternConsumersIJPs = RegesterIJPatterns();
            ArrayList<Supplier<BasePattern>> patternConsumersSchemaCorrect = RegesterSchemaCorrectPatterns();
            for (Supplier<BasePattern> p : patternConsumersIJPs) {
                System.out.println("Generating neg pattern: " + p.get().toString());
                p.get().SetOWLAPIContext(ont, reasoner, factory, out_dir).generatePattern();
            }
            for (Supplier<BasePattern> p : patternConsumersSchemaCorrect) {
                System.out.println("Generating pos pattern: " + p.get().toString());
                p.get().SetOWLAPIContext(ont, reasoner, factory, out_dir).generatePattern();
            }
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    private ArrayList<Supplier<BasePattern>> RegesterIJPatterns() {
        ArrayList<Supplier<BasePattern>> patternConsumers = new ArrayList<>();
        patternConsumers.add(PatternDLLite::new);
        patternConsumers.add(PatternAsymmetric::new);
        patternConsumers.add(PatternIrreflexive::new);
        return patternConsumers;
    }

    private ArrayList<Supplier<BasePattern>> RegesterSchemaCorrectPatterns() {
        ArrayList<Supplier<BasePattern>> patternConsumers = new ArrayList<>();
        patternConsumers.add(PatternPosDomain::new);
        patternConsumers.add(PatternPosRange::new);
        return patternConsumers;
    }

    private InputStream readFileAsStream(String fileName) throws FileNotFoundException {
        // The class loader that loaded the class
//        ClassLoader classLoader = getClass().getClassLoader();
//        InputStream inputStream = classLoader.getResourceAsStream(fileName);
        File initialFile = new File(fileName);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + fileName);
        } else {
            return inputStream;
        }
    }
}
