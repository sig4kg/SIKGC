package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLObjectPropertyRangeAxiom;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.util.*;

public class Pattern16 extends BasePattern implements IPattern {

    public void generatePattern() {
        //Range(r1) disjoint Range (r2) -> (x  r1 e1),(y r2 e1)
        try {
            this.GetPrintWriter("16");
            Map<String, Set<OWLClass>> map=new HashMap<String, Set<OWLClass>>();
            Map<String, List<String>> result_map=new HashMap<String, List<String>>();
            for (OWLObjectPropertyRangeAxiom ax1 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)){
                String r = ax1.getProperty().getNamedProperty().toString();
                NodeSet<OWLClass> sof = reasoner.getDisjointClasses(ax1.getRange());
                map.put(r, sof.getFlattened());
            }
            for (OWLObjectPropertyRangeAxiom ax1 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)){
                String r1 = ax1.getProperty().getNamedProperty().toString();
                OWLClass Range_r1 = ax1.getRange().asOWLClass();
                for (String r2 : map.keySet()) {
                    if (r2.equals(r1)) {
                        continue;
                    }
                    if (map.get(r2).contains(Range_r1)) {
                        if(result_map.containsKey(r1)) {
                            result_map.get(r1).add(r2);
                        } else {
                            List<String> vers = new ArrayList<String>();
                            vers.add(r2);
                            result_map.put(r1, vers);
                        }
                    }
                }
            }
            for (String fi : result_map.keySet()){
                List<String> value_l = result_map.get(fi);
                String line = fi + "\t" + String.join( "@@", value_l);
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
