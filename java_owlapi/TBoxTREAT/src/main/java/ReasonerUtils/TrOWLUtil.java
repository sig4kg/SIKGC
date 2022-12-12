package ReasonerUtils;

import eu.trowl.owlapi3.rel.reasoner.dl.RELReasoner;
import eu.trowl.owlapi3.rel.reasoner.dl.RELReasonerFactory;
import eu.trowl.owlapi3.rel.util.InferredSubClassAxiomMultiGenerator;
import eu.trowl.owlapi3.rel.util.InferredSubObjectPropertyAxiomMultiGenerator;
import org.semanticweb.HermiT.Configuration;
import org.semanticweb.HermiT.Reasoner;
import org.semanticweb.owl.explanation.api.Explanation;
import org.semanticweb.owl.explanation.api.ExplanationGenerator;
import org.semanticweb.owl.explanation.impl.blackbox.checker.InconsistentOntologyExplanationGeneratorFactory;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.OWLXMLDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import org.semanticweb.owlapi.util.*;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.*;
import java.util.function.Supplier;

public class TrOWLUtil extends ReasonerBase {
    String output_dir;

    public TrOWLUtil(String output_dir) {
        this.output_dir = output_dir;
    }

    public OWLReasoner getReasoner(OWLOntology ontology) {
        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        RELReasonerFactory rf = new RELReasonerFactory();
        OWLReasoner reasoner = rf.createReasoner(ontology);
        return reasoner;
    }

    public Set<Explanation<OWLAxiom>> getInconsistentSubsets(OWLOntology ontology, OWLOntologyManager man) {
        long start = System.currentTimeMillis();
        Set<Explanation<OWLAxiom>> explanationSet = new HashSet<>();
        Supplier<OWLOntologyManager> m = OWLManager::createOWLOntologyManager;
        OWLDataFactory df = man.getOWLDataFactory();
        RELReasonerFactory rf = new RELReasonerFactory();
        InconsistentOntologyExplanationGeneratorFactory igf =
                new InconsistentOntologyExplanationGeneratorFactory(rf, df, m,3*60*60*1000);
        OWLReasoner reasoner = getReasoner(ontology);
        ExplanationGenerator<OWLAxiom> generator = igf.createExplanationGenerator(ontology);
        Boolean isCon = reasoner.isConsistent();
        long end1 = System.currentTimeMillis();
        System.out.println("CC Time takes " +
                (end1 - start) + "ms");
        if (!isCon) {
            OWLAxiom ax = df.getOWLSubClassOfAxiom(df.getOWLThing(), df.getOWLNothing());
            explanationSet = generator.getExplanations(ax, 50);
            long end2 = System.currentTimeMillis();
            System.out.println("GJ Time takes " +
                    (end2 - start)/1000 + "s");
        }
        return explanationSet;
    }

    public OWLOntology classify(OWLOntology ontology, OWLOntologyManager man) {
        OWLReasoner reasoner = getReasoner(ontology);

        boolean consistencyCheck = reasoner.isConsistent();
        OWLDataFactory df = man.getOWLDataFactory();
        if (!consistencyCheck) {
            System.out.println("Inconsistent input Ontology, Please check the OWL File");
        }
        //flatten

        System.out.println("Classification, may take time......");
        reasoner.precomputeInferences(
                InferenceType.CLASS_ASSERTIONS,
                InferenceType.CLASS_HIERARCHY,
                InferenceType.SAME_INDIVIDUAL,
                InferenceType.OBJECT_PROPERTY_ASSERTIONS,
                InferenceType.OBJECT_PROPERTY_HIERARCHY,
                InferenceType.DISJOINT_CLASSES
        );
        List<InferredAxiomGenerator<? extends OWLAxiom>> generators = new ArrayList<>();
        generators.add(new InferredSubClassAxiomMultiGenerator());
        generators.add(new InferredSubObjectPropertyAxiomMultiGenerator());
        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, generators);
        try {
            OWLOntology infOnt = man.createOntology();
            iog.fillOntology(df, infOnt);
            return infOnt;
        } catch (OWLOntologyCreationException e) {
            System.out.println(e.getMessage());
            return null;
        }
    }

    public OWLOntology realize(OWLOntology ontology, OWLOntologyManager man) {
        // create reasoner
        OWLReasoner reasoner = getReasoner(ontology);
        OWLDataFactory df = man.getOWLDataFactory();

        boolean consistencyCheck = reasoner.isConsistent();
        if (!consistencyCheck) {
            System.out.println("Inconsistent input Ontology, Please check the OWL File");
        }
        System.out.println("Materialising type assertions and property assertions, may take time......");
        reasoner.precomputeInferences(
                InferenceType.CLASS_ASSERTIONS,
                InferenceType.CLASS_HIERARCHY,
                InferenceType.OBJECT_PROPERTY_ASSERTIONS,
                InferenceType.OBJECT_PROPERTY_HIERARCHY
        );
        List<InferredAxiomGenerator<? extends OWLAxiom>> generators = new ArrayList<>();
        generators.add(new InferredClassAssertionAxiomGenerator());
        generators.add(new InferredPropertyAssertionGenerator());
        List<InferredIndividualAxiomGenerator<? extends OWLIndividualAxiom>> individualAxioms =
                new ArrayList<>();
        generators.addAll(individualAxioms);

        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, generators);
        try {
            OWLOntology inferredAxiomsOntology = man.createOntology();
            iog.fillOntology(df, inferredAxiomsOntology);
            return inferredAxiomsOntology;
        } catch (OWLOntologyCreationException e) {
            System.out.println(e.getMessage());
            return null;
        }
    }
}
