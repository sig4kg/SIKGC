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

public class Pattern10 extends BasePattern implements IPattern {
    public void generatePattern() {
        //range of r1 is disjoint with range of r2
        // R(r1)=C1, R(r2)=C2, C1 disjoint C2, <e1 r1 x> <e2 r2 x>
        try {
            this.GetPrintWriter("10");
            for (OWLObjectPropertyRangeAxiom r1Axiom : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                String r1 = r1Axiom.getProperty().getNamedProperty().toString();
                if (r1.equalsIgnoreCase("<http://dbpedia.org/ontology/nominee>")) {
                    String a = "here";
                }
                NodeSet<OWLClass> sof = reasoner.getDisjointClasses(r1Axiom.getRange());
                List<String> disjoint_r2 = new ArrayList<String>();
                for (OWLObjectPropertyRangeAxiom r2Axiom : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                    String r2 = r2Axiom.getProperty().getNamedProperty().toString();
                    if(r2.equalsIgnoreCase("<http://dbpedia.org/ontology/region>")){
                        String b = "here";
                    }
                    if (r1.equalsIgnoreCase(r2)) {
                        continue;
                    }
                    Set<OWLClass> rang2 = r2Axiom.getRange().getClassesInSignature();
                    for (OWLClass r2_range : rang2) {
                        if (sof.containsEntity(r2_range)) {
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
