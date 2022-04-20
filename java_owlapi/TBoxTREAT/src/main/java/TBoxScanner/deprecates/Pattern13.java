package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Pattern13 extends BasePattern implements IPattern {

    public void generatePattern() {
        //FunctionalProperty(r2), Inverseof(r1, r2) ---- <y r1 x> <z r1 x> and <x r2 y> <z r1 x>
        //FunctionalProperty(r1), Inverseof(r1, r2) ---- <y r2 x> <z r2 x> and <x r1 y> <z r2 x>

        Map<String, List<String>> map = new HashMap<String, List<String>>();
//            for (OWLInverseFunctionalObjectPropertyAxiom inversof : ont.getAxioms(AxiomType.INVERSE_FUNCTIONAL_OBJECT_PROPERTY)) {
//                functionalInverse.add(inversof.getProperty().toString());
//            }

        List<String> functional = new ArrayList<String>();
        for (OWLFunctionalObjectPropertyAxiom funcp : ont.getAxioms(AxiomType.FUNCTIONAL_OBJECT_PROPERTY)) {
            functional.add(funcp.getProperty().toString());
        }
        for (OWLInverseObjectPropertiesAxiom objInvers : ont.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES)) {
            String r1 = objInvers.getFirstProperty().toString();
            String r2 = objInvers.getSecondProperty().toString();
            if (functional.contains(r1)) {
                if (map.containsKey(r1)) {
                    map.get(r1).add(r2);
                } else {
                    List<String> vers = new ArrayList<String>();
                    vers.add(r2);
                    map.put(r1, vers);
                }
            }
            if (functional.contains(r2)) {
                if (map.containsKey(r2)) {
                    map.get(r2).add(r1);
                } else {
                    List<String> vers = new ArrayList<String>();
                    vers.add(r1);
                    map.put(r2, vers);
                }
            }
        }
        try {
            this.GetPrintWriter("13");
            for (String fi : map.keySet()) {
                List<String> value_l = map.get(fi);
                String line = fi + "\t" + String.join("@@", value_l);
                pw.println(line);
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
