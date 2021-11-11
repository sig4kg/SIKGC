package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.*;

public class Pattern7_1 extends BasePattern implements IPattern {

    public void generatePattern() {
        Set<OWLAsymmetricObjectPropertyAxiom> allAsyOP = ont.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY);
        Set<OWLSymmetricObjectPropertyAxiom> allSymOP = ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY);
        if (allAsyOP.size() == 0 || allSymOP.size() == 0) {
            return;
        }
        Map<String, ArrayList<String>> subP2AsyP = new HashMap<>();
        Map<String, ArrayList<String>> subP2SymP = new HashMap<>();
        for (OWLAsymmetricObjectPropertyAxiom r3 : allAsyOP) {
            OWLObjectPropertyExpression r3_ope = r3.getProperty();
            NodeSet<OWLObjectPropertyExpression> r1s = reasoner.getSubObjectProperties(r3_ope.getNamedProperty(), false);
            if (r1s.getNodes().size() <= 1) {
                continue;
            }
            for (Node<OWLObjectPropertyExpression> r1 : r1s.getNodes()) {
                if (r1.isBottomNode()) {
                    continue;
                }
                OWLObjectPropertyExpression r1_ope = r1.getRepresentativeElement();
                if (!r1_ope.isOWLObjectProperty()) {
                    continue;
                }
                if (subP2AsyP.containsKey(r1_ope.toString())) {
                    subP2AsyP.get(r1_ope.toString()).add(r3_ope.toString());
                } else {
                    ArrayList<String> superPs = new ArrayList<>();
                    superPs.add(r3_ope.toString());
                    subP2AsyP.put(r1_ope.toString(), superPs);
                }
            }
        }
        for (OWLSymmetricObjectPropertyAxiom r2 : allSymOP) {
            OWLObjectPropertyExpression r2_ope = r2.getProperty();
            NodeSet<OWLObjectPropertyExpression> r1s = reasoner.getSubObjectProperties(r2_ope.getNamedProperty(), false);
            if (r1s.getNodes().size() <= 1) {
                continue;
            }
            for (Node<OWLObjectPropertyExpression> r1 : r1s.getNodes()) {
                if (r1.isBottomNode()) {
                    continue;
                }
                OWLObjectPropertyExpression r1_ope = r1.getRepresentativeElement();
                if (!r1_ope.isOWLObjectProperty()) {
                    continue;
                }
                if (subP2SymP.containsKey(r1_ope.toString())) {
                    subP2SymP.get(r1_ope.toString()).add(r2_ope.toString());
                } else {
                    ArrayList<String> superPs = new ArrayList<>();
                    superPs.add(r2_ope.toString());
                    subP2SymP.put(r1_ope.toString(), superPs);
                }
            }
        }
        try {
            this.GetPrintWriter("7");
            for (String r1keySym : subP2SymP.keySet()) {
                for (String r1keyAsy : subP2AsyP.keySet()) {
                    if (r1keySym.equals(r1keyAsy)) {
                        pw.println(r1keyAsy);
                    }
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
