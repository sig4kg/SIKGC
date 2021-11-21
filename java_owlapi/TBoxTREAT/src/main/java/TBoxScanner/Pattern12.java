package TBoxScanner;

import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLAsymmetricObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLFunctionalObjectPropertyAxiom;

import java.io.IOException;

public class Pattern12 extends BasePattern implements IPattern{

    public void generatePattern() {
        //FunctionalProperty(r) ----- <x r y> <x r z>
        try {
            this.GetPrintWriter("12");
            for (OWLFunctionalObjectPropertyAxiom funcp : ont.getAxioms(AxiomType.FUNCTIONAL_OBJECT_PROPERTY)) {
                pw.println(funcp.getProperty().toString());
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
