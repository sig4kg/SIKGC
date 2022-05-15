package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLObjectPropertyDomainAxiom;
import org.semanticweb.owlapi.model.OWLObjectPropertyRangeAxiom;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.util.*;

public class PatternTypeDisjointness extends BasePattern implements IPattern {

    public void generatePattern() {
        //Class disjointness
        Map<String, List<String>> result_map = new HashMap<String, List<String>>();
        for (OWLClass cls : ont.getClassesInSignature()) {
            if (!cls.isNamed()) {
                continue;
            }
            String c_uri = cls.toString();
            Set<OWLClass> sof = reasoner.getDisjointClasses(cls).getFlattened();
            if (sof.size() > 0) {
                List<String> vers = new ArrayList<String>();
                for (OWLClass dc : sof) {
                    if (dc.isNamed()) {
                        vers.add(dc.toString());
                    }
                }
                result_map.put(c_uri, vers);
            }
        }
        try {
            this.GetPrintWriter("class_disjointness");
            for (String fi : result_map.keySet()) {
                List<String> value_l = result_map.get(fi);
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
