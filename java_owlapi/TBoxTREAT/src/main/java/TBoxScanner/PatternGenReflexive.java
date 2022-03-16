package TBoxScanner;


import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLReflexiveObjectPropertyAxiom;

import java.io.IOException;

public class PatternGenReflexive extends BasePattern implements IPattern {

    public void generatePattern() {
        // reflexive(r)
        try {
            this.GetPrintWriter("gen_reflexive");
            for (OWLReflexiveObjectPropertyAxiom irl : ont.getAxioms(AxiomType.REFLEXIVE_OBJECT_PROPERTY)) {
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
