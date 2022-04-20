package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.util.*;

public class Pattern14 extends BasePattern implements IPattern {

    public void generatePattern() {
        //Domain(r1) disjoint Domain (r2) -> (e1  r1 x),(e2 r2 y)
        try {
            this.GetPrintWriter("14");
            Map<String, Set<OWLClass>> map=new HashMap<String, Set<OWLClass>>();
            Map<String, List<String>> result_map=new HashMap<String, List<String>>();
            for (OWLObjectProperty rr :ont.getObjectPropertiesInSignature()) {
                NodeSet<OWLClass> d = reasoner.getObjectPropertyDomains(rr);
                Set<OWLClass> df = d.getFlattened();
            }
            for (OWLObjectPropertyDomainAxiom ax1 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)){
                String r = ax1.getProperty().getNamedProperty().toString();
                NodeSet<OWLClass> sof = reasoner.getDisjointClasses(ax1.getDomain());
                map.put(r, sof.getFlattened());
            }
            for (OWLObjectPropertyDomainAxiom ax1 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)){
                String r1 = ax1.getProperty().getNamedProperty().toString();
                OWLClass domain_r1 = ax1.getDomain().asOWLClass();
                for (String r2 : map.keySet()) {
                    if (r2.equals(r1)) {
                        continue;
                    }
                    if (map.get(r2).contains(domain_r1)) {
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
