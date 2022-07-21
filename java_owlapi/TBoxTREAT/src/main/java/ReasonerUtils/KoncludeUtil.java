package ReasonerUtils;

import org.semanticweb.owlapi.formats.OWLXMLDocumentFormat;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.OWLReasoner;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class KoncludeUtil extends ReasonerBase {
    String Konclude_bin;
    String Konclude_config;

    public KoncludeUtil(String Konclude_bin, String output_dir) {
        this.Konclude_bin = Konclude_bin;
        this.output_dir = output_dir;
        this.Konclude_config = Konclude_bin.substring(0, Konclude_bin.lastIndexOf("/") + 1) + "../Configs/default-config.xml";
    }

    public List<OWLAxiom> getInconsistentSubset(OWLOntology ontology, OWLOntologyManager man, List<OWLAxiom> toCheckAxioms) {
        List<OWLAxiom> inconsistentTriples = new ArrayList<>();
        for(OWLAxiom ax : toCheckAxioms) {
            man.addAxiom(ontology, ax);
            OWLReasoner reasoner = getReasoner(ontology);
            if (!reasoner.isConsistent()) {
                RemoveAxiom removeAxiom = new RemoveAxiom(ontology, ax);
                man.applyChange(removeAxiom);
                inconsistentTriples.add(ax);
            }
        }
        return inconsistentTriples;
    }

    // Konclude class
    public OWLOntology classify(OWLOntology ontology, OWLOntologyManager man) {
        String tmp_infile = this.getTmpName("tmp_in_");
        String tmp_outfile = getTmpName("tmp_out_");
        //save middle onto to owlxml, this used as input of Konclude binary
        System.out.println("Saving middle ontology " + tmp_infile);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream tmp_infile_stream = new FileOutputStream(tmp_infile)) {
            // We use the owlxml format as for the input ontology, Konclude only supports xml formats
            OWLXMLDocumentFormat format = new OWLXMLDocumentFormat();
            man.saveOntology(ontology, format, tmp_infile_stream);
            waitUntilFileSaved(tmp_infile, 10);
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return null;
        }
        // wait until file is saved
        try {
            ProcessBuilder pb1 = new ProcessBuilder("ls", this.Konclude_bin);
            pb1.redirectOutput(ProcessBuilder.Redirect.INHERIT);
            Process p1 = pb1.start();
            int status1 = p1.waitFor();
            ProcessBuilder pb = new ProcessBuilder(this.Konclude_bin, "classification", "-i", tmp_infile, "-o", tmp_outfile);
            pb.redirectOutput(ProcessBuilder.Redirect.INHERIT);
            Process p = pb.start();
            int status = p.waitFor();

            System.out.println("Exited with status: " + status);
            OWLOntology tmp_onto = null;
            if (status == 0) {
                // load inferenced ontology
                waitUntilFileSaved(tmp_outfile, 10);
                tmp_onto = man.loadOntologyFromOntologyDocument(new File(tmp_outfile));
            }
            return tmp_onto;
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return null;
        }
    }

    public OWLOntology realize(OWLOntology ontology, OWLOntologyManager man) {
        String tmp_infile = getTmpName("tmp_rin_");
        String tmp_outfile = getTmpName("tmp_rout_");
        //save middle onto to owlxml, this used as input of Konclude binary
        System.out.println("Saving middle ontology " + tmp_infile);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream tmp_infile_stream = new FileOutputStream(tmp_infile)) {
            // We use the owlxml format as for the input ontology, Konclude only supports xml formats
            OWLXMLDocumentFormat format = new OWLXMLDocumentFormat();
            man.saveOntology(ontology, format, tmp_infile_stream);
            waitUntilFileSaved(tmp_infile, 10);
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return null;
        }
        // wait until file is saved
        System.out.println("Konclude config: " + this.Konclude_config);
        try {
            ProcessBuilder pb1 = new ProcessBuilder(this.Konclude_bin, "realisation", "-c", this.Konclude_config, "-i", tmp_infile, "-o", tmp_outfile);
            pb1.redirectOutput(ProcessBuilder.Redirect.INHERIT);
            Process p1 = pb1.start();
            int status1 = p1.waitFor();
            System.out.println("Konclude realisation exited with status: " + status1);
            OWLOntology tmp_onto = null;
            if (status1 == 0) {
                // load inferenced ontology
                waitUntilFileSaved(tmp_outfile, 10);
                tmp_onto = man.loadOntologyFromOntologyDocument(new File(tmp_outfile));
            }
            // run role queries to get relation assertions
            //./Konclude sparqlfile -i tmp_r_7.xml -s role-instance-queries.sparql -o test.xml
            String sparql_file = this.output_dir + "role_queries.sparql";
            String rel_out_file = this.output_dir + "materialized_role_instance.xml";
            ProcessBuilder pb2 = new ProcessBuilder(this.Konclude_bin, "sparqlfile", "-c", this.Konclude_config, "-i", tmp_infile, "-s", sparql_file, "-o", rel_out_file);
            pb2.redirectOutput(ProcessBuilder.Redirect.INHERIT);
            Process p2 = pb2.start();
            int status2 = p2.waitFor();
            System.out.println("Konclude sparql query exited with status: " + status2);
            return tmp_onto;
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return null;
        }
    }
}
