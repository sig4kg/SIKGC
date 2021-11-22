import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

//import com.clarkparsia.pellet.owlapiv3.PelletReasonerFactory;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.io.StringDocumentTarget;
import org.semanticweb.owlapi.model.OWLAxiom;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import org.semanticweb.owlapi.reasoner.structural.StructuralReasonerFactory;
import org.semanticweb.owlapi.util.InferredAxiomGenerator;
import org.semanticweb.owlapi.util.InferredOntologyGenerator;
import org.semanticweb.owlapi.util.InferredSubClassAxiomGenerator;


public class DLLite {

    public void shouldCreateInferredAxioms(String in_file, String out_file) throws Exception {
        System.out.println("to DL-lite: " + in_file);
        File initialFile = new File(in_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        // Create a reasoner factory.
        // See Profiles for a list of known reasoner factories; note that you
        // will need to add the reasoner and any dependency to the classpath for
        // this to work.
        // The structural reasoner is a mock reasoner that does no inferences;
        // it is used only for examples.
        OWLReasonerFactory reasonerFactory = new StructuralReasonerFactory();
//        reasonerFactory = new PelletReasonerFactory();

        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(inputStream);
        // Create the reasoner and classify the ontology
        OWLReasoner reasoner = reasonerFactory.createNonBufferingReasoner(ont);
        reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY);
        // To generate an inferred ontology we use implementations of inferred
        // axiom generators to generate the parts of the ontology we want (e.g.
        // subclass axioms, equivalent classes axioms, class assertion axiom
        // etc. - see the org.semanticweb.owlapi.util package for more
        // implementations). Set up our list of inferred axiom generators
        List<InferredAxiomGenerator<? extends OWLAxiom>> gens =
                new ArrayList<InferredAxiomGenerator<? extends OWLAxiom>>();
        gens.add(new InferredSubClassAxiomGenerator());
        // Put the inferred axioms into a fresh empty ontology - note that there
        // is nothing stopping us stuffing them back into the original asserted
        // ontology if we wanted to do this.
        OWLOntology infOnt = man.createOntology();
        // Now get the inferred ontology generator to generate some inferred
        // axioms for us (into our fresh ontology). We specify the reasoner that
        // we want to use and the inferred axiom generators that we want to use.
        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, gens);
        iog.fillOntology(man.getOWLDataFactory(), infOnt);
        // Save the inferred ontology. (Replace the IRI with one that is
        // appropriate for your setup)
        man.saveOntology(infOnt, new StringDocumentTarget());
    }

}
