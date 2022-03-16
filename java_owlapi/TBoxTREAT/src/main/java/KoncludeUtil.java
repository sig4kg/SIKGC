import org.semanticweb.owlapi.formats.OWLXMLDocumentFormat;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.Random;

public class KoncludeUtil {
    String Konclude_bin;
    String output_dir;
    Random r = new Random();
    public KoncludeUtil(String Konclude_bin, String output_dir) {
        this.Konclude_bin = Konclude_bin;
        this.output_dir = output_dir;
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
        ProcessBuilder pb = new ProcessBuilder(this.Konclude_bin, "realisation", "-i", tmp_infile, "-o", tmp_outfile);
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
}
