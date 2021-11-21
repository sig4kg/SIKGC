import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.formats.RDFXMLDocumentFormat;
import org.semanticweb.owlapi.model.*;

import java.io.*;

public class FormatConverter {
    public static void toNT(String in_file, String out_file) throws Exception {
        System.out.println("convert to OWL file: " + in_file);
        File initialFile = new File(in_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(inputStream);
//        FileWriter fileWriter = new FileWriter(out_file);
//        PrintWriter printWriter = new PrintWriter(fileWriter);
//        for (OWLAxiom owlAxiom: ontology.getAxioms()){
//            owlAxiom.isAxiom();
//        }
//        ontology.axioms().forEach(owlAxiom -> printWriter.write(owlAxiom.toString()));
        NTriplesDocumentFormat nTriplesFormat = new NTriplesDocumentFormat();
        File inferredOntologyFile = new File(out_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            ontology.remove();
            manager.saveOntology(ontology, nTriplesFormat, outputStream);
        } catch (OWLOntologyStorageException e) {
            e.printStackTrace();
            throw e;
        }
    }
}
