import org.semanticweb.owlapi.formats.OWLXMLDocumentFormat;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.Random;

public class KoncludeUtil {
    String Konclude_bin;
    String Konclude_config;
    String output_dir;
    Random r = new Random();
    public KoncludeUtil(String Konclude_bin, String output_dir) {
        this.Konclude_bin = Konclude_bin;
        this.output_dir = output_dir;
        this.Konclude_config = Konclude_bin.substring(0, Konclude_bin.lastIndexOf("/") + 1) + "../Configs/default-config.xml";
    }

    private String getTmpName(String filePrefix) {
        int i = this.r.nextInt(100);
        return this.output_dir + filePrefix + i + ".xml";
    }

    private Boolean waitUntilFileSaved(String fileName, int timeout) {
        int i = timeout;
        File file = new File(fileName);
        while (!file.exists()) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
            }
            if (--i <= 0) {
                System.out.println("Saving file timeout after " + timeout + " seconds");
                return false;
            }
        }
        System.out.println(fileName + " has  been saved.");
        return true;
    }

    public OWLOntology koncludeClassifier(OWLOntology ontology, OWLOntologyManager man) throws Exception {
        String tmp_infile = getTmpName("tmp_in_");
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
        }
        // wait until file is saved
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
    }

    public OWLOntology koncludeRelization(OWLOntology ontology, OWLOntologyManager man) throws Exception {
        String tmp_infile = getTmpName("tmp_r_");
        String tmp_outfile = getTmpName("tmp_r_");
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
        }
        // wait until file is saved
        System.out.println("Konclude config: " + this.Konclude_config);
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
    }
}
