package TBoxScanner;

import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLIrreflexiveObjectPropertyAxiom;

import java.io.IOException;

public class PatternIrreflexive extends BasePattern implements IPattern {

    public void generatePattern() {
    // Irreflexive(r)
        try {
            this.GetPrintWriter("PatternIrreflexive.txt");
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
