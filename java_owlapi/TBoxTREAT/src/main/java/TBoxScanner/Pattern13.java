package TBoxScanner;

import org.semanticweb.owlapi.model.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Pattern13 extends BasePattern implements IPattern{

    public void generatePattern() {
        //FunctionalProperty(r2), Inverseof(r1, r2) ---- <y r1 x> <z r1 x> and <x r2 y> <z r1 x>
        try {
            this.GetPrintWriter("13");
            List<String> functionalInverse = new ArrayList<String>();
            Map map=new HashMap<String, List>();
            for (OWLInverseFunctionalObjectPropertyAxiom inversof : ont.getAxioms(AxiomType.INVERSE_FUNCTIONAL_OBJECT_PROPERTY)) {
                functionalInverse.add(inversof.getProperty().toString());
            }

            List<String> functional = new ArrayList<String>();
            for (OWLFunctionalObjectPropertyAxiom funcp : ont.getAxioms(AxiomType.FUNCTIONAL_OBJECT_PROPERTY)) {
                functional.add(funcp.getProperty().toString());
            }
            for (OWLInverseObjectPropertiesAxiom objInvers : ont.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES)) {
                String r1 = objInvers.getFirstProperty().toString();
                String r2 = objInvers.getSecondProperty().toString();
                if(functional.contains(r1) && !functionalInverse.contains(r1)) {
                    functionalInverse.add(r1);
                }
            }
            for (String fi : functionalInverse){
                pw.println(fi);
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
