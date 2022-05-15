package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;

public class Pattern11 extends BasePattern implements IPattern {

    public void generatePattern() {
        //domain of r1 is disjoint with domain of r2
        // D(r1)=C1, D(r2)=C2, C1 disjoint C2, <x r1 e1> <x r2 e2>
        try {
            this.GetPrintWriter("11");
            for (OWLObjectPropertyDomainAxiom r1Axiom : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                String r1 = r1Axiom.getProperty().getNamedProperty().toString();
                NodeSet<OWLClass> sof = reasoner.getDisjointClasses(r1Axiom.getDomain());
                List<String> disjoint_r2 = new ArrayList<String>();
                for (OWLObjectPropertyDomainAxiom r2Axiom : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                    String r2 = r2Axiom.getProperty().getNamedProperty().toString();
                    if (r1.equalsIgnoreCase(r2)) {
                        continue;
                    }
                    Set<OWLClass> doma2 = r2Axiom.getDomain().getClassesInSignature();
                    for (OWLClass r2_domain : doma2) {
                        if (sof.containsEntity(r2_domain)) {
                            disjoint_r2.add(r2);
                            break;
                        }
                    }
                }
                if (disjoint_r2.size() > 0) {
                    pw.print(r1 + "\t");
                    //pw.print(Prop+"\t");
                    for (String rr2 : disjoint_r2) {
                        pw.print(rr2.toString() + "@@");
                    }
                    pw.println();
                }
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
