package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLFunctionalObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLInverseObjectPropertiesAxiom;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PatternGenInverse extends BasePattern implements IPattern {
    public void generatePattern() {
        //Inverseof(r1, r2)
        try {
            this.GetPrintWriter("gen_inverse");
            Map<String, List<String>> map = new HashMap<String, List<String>>();
            for (OWLInverseObjectPropertiesAxiom objInvers : ont.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES)) {
                String r1 = objInvers.getFirstProperty().toString();
                String r2 = objInvers.getSecondProperty().toString();
                if (map.containsKey(r1)) {
                    map.get(r1).add(r2);
                } else {
                    List<String> vers = new ArrayList<String>();
                    vers.add(r2);
                    map.put(r1, vers);
                }
            }
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
