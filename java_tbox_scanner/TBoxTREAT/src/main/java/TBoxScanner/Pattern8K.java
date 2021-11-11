package TBoxScanner;

import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLIrreflexiveObjectPropertyAxiom;

import java.io.IOException;
import java.io.PrintWriter;

public class Pattern8K extends BasePattern implements IPattern {

    public void generatePattern() {
    // Irreflexive(r)
        try {
            this.GetPrintWriter("8");
            for (OWLIrreflexiveObjectPropertyAxiom irl : ont.getAxioms(AxiomType.IRREFLEXIVE_OBJECT_PROPERTY)) {
                pw.println(irl.getProperty().toString());
            }
            pw.close();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (pw != null) {
                pw.close();
            }
        }
    }
}
