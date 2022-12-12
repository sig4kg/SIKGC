import ReasonerUtils.HermitUtil;
import ReasonerUtils.TrOWLUtil;
import TBoxScanner.PatternDLLite;
import TBoxScanner.TBoxPatternGenerator;
import org.junit.Assert;
import org.junit.Test;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import org.semanticweb.owlapi.util.DefaultPrefixManager;
import uk.ac.manchester.cs.jfact.JFactFactory;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Stream;

public class TestExplanation {
    OWLOntologyManager man = OWLManager.createOWLOntologyManager();
    OWLDataFactory dataFactory = man.getOWLDataFactory();
    TrOWLUtil trOWLUtil = new TrOWLUtil("./");
    HermitUtil hermitUtil = new HermitUtil("./");
    String testAxioms = "";
    String ontPath = "";



    private OWLOntology loadRes(String ontology_file) {
        try {
            File initialFile = new File(ontology_file);
            InputStream is = new FileInputStream(initialFile);
            // the stream holding the file content
            if (is == null) {
                throw new IllegalArgumentException("file not found! " + ontology_file);
            }
            OWLOntology ont = man.loadOntologyFromOntologyDocument(is);
            return ont;
        } catch (OWLOntologyCreationException | IllegalArgumentException | FileNotFoundException e) {
            e.printStackTrace();
            return null;
        }
    }

    private Set<OWLAxiom> loadTocheck(String axiom_file, OWLDataFactory df) {
        Set<OWLAxiom> tocheck = new HashSet<>();
        try {
            // the stream holding the file content
            BufferedReader br = new BufferedReader(new FileReader(axiom_file));
            for(String line; (line = br.readLine()) != null; ) {
                String[] tri = line.trim().split("\t");
                if (tri.length != 3) {
                    continue;
                }
                OWLNamedIndividual subj = df.getOWLNamedIndividual(tri[0]);
                OWLNamedIndividual obj = df.getOWLNamedIndividual(tri[2]);
                OWLObjectProperty rel = df.getOWLObjectProperty(tri[1]);
                // To specify that :John is related to :Mary via the :hasWife property
                // we create an object property assertion and add it to the ontology
                OWLObjectPropertyAssertionAxiom propertyAssertion = df
                        .getOWLObjectPropertyAssertionAxiom(rel, subj, obj);
                tocheck.add(propertyAssertion);
            }
            return tocheck;
        } catch ( IllegalArgumentException | IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    @Test
    public void testTREAT() throws OWLOntologyCreationException {
        testAxioms = "./output/treatTest/tocheck.csv";
        ontPath = "./output/treatTest/tbox_abox.nt";
        OWLOntology ont = loadRes(ontPath);
//        hermitUtil.getInconsistentSubsets(ont, man);
        trOWLUtil.getInconsistentSubsets(ont, man);
    }

    @Test
    public void testDB() throws OWLOntologyCreationException {
        testAxioms = "./output/testDB/tocheck.csv";
        ontPath = "./output/testDB/tbox_abox.nt";
        OWLOntology ont = loadRes(ontPath);
//        hermitUtil.getInconsistentSubsets(ont, man);
        trOWLUtil.getInconsistentSubsets(ont, man);
    }

    @Test
    public void testNELL() throws OWLOntologyCreationException {
        testAxioms = "./output/testNELL/inv.csv";
        ontPath = "./output/testNELL/tbox_abox.nt";
        OWLOntology ont = loadRes(ontPath);
//        Set<OWLAxiom> tocheck = loadTocheck(testAxioms, dataFactory);
        hermitUtil.getInconsistentSubsets(ont, man);
//        trOWLUtil.getInconsistentSubsets(ont, man);
    }

    @Test
    public void testTrOWL() throws OWLOntologyCreationException {

    }
}
