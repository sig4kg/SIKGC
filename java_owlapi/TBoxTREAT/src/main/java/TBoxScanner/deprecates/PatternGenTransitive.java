package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLSymmetricObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLTransitiveObjectPropertyAxiom;

import java.io.IOException;

public class PatternGenTransitive extends BasePattern implements IPattern {
    // Symmetric(r)
    public void generatePattern() {
        try {
            this.GetPrintWriter("gen_transitive");
            for (OWLTransitiveObjectPropertyAxiom r : ont.getAxioms(AxiomType.TRANSITIVE_OBJECT_PROPERTY)) {
                pw.println(r.getProperty().toString());
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
