import ReasonerUtils.IReasonerUtil;
import ReasonerUtils.KoncludeUtil;
import ReasonerUtils.TrOWLUtil;
import org.semanticweb.HermiT.Configuration;
import org.semanticweb.HermiT.Reasoner.ReasonerFactory;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.OWLReasoner;

import java.io.*;

public class Materialize {
    String output_dir;
    protected OWLOntologyManager man;
    protected OWLDataFactory factory;
    protected OWLOntology ont;

    public Materialize(String output_dir) {
        this.output_dir = output_dir;
    }

    private void loadOnto(String ontology_file) {
        try {
            man = OWLManager.createOWLOntologyManager();
            File initialFile = new File(ontology_file);
            InputStream inputStream = new FileInputStream(initialFile);
            // the stream holding the file content
            if (inputStream == null) {
                throw new IllegalArgumentException("file not found! " + ontology_file);
            } else {
                ont = man.loadOntologyFromOntologyDocument(inputStream);
                factory = man.getOWLDataFactory();
            }
        } catch (OWLOntologyCreationException | IllegalArgumentException | FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    private void saveOnto(OWLOntology toSaveOnto) {
        String out_file = this.output_dir + "/materialized_tbox_abox.nt";
        try (OutputStream outputStream = new FileOutputStream(out_file)) {
            // We use the nt format as for the input ontology.
            NTriplesDocumentFormat format = new NTriplesDocumentFormat();
            man.saveOntology(toSaveOnto, format, outputStream);
            System.out.println("Output saved: " + out_file);
        } catch (Exception e) {
            System.out.println(e.getMessage());
            e.printStackTrace();
        }
    }


    public void checkConsistency(String in_file) throws Exception {
        System.out.println("check consistency: " + in_file);
        loadOnto(in_file);
        // create Hermit reasoner
        OWLDataFactory df = man.getOWLDataFactory();
        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        ReasonerFactory rf = new ReasonerFactory();
        OWLReasoner reasoner = rf.createReasoner(ont, configuration);
        boolean consistencyCheck = reasoner.isConsistent();
        if (consistencyCheck) {
            System.out.println("tbox and abox are consistent.");
        } else {
            System.out.println("tbox and abox are not consistent.");
        }
    }

    public void materialize(IReasonerUtil reasonUtil, String in_file) throws Exception {
        System.out.println("Materializing: " + in_file);
        loadOnto(in_file);
        OWLOntology inferredAxiomsOntology = reasonUtil.realize(ont, man);
        saveOnto(inferredAxiomsOntology);
        System.out.println("Done with materialization");
    }
}