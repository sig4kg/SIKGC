package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.util.Iterator;
import java.util.Set;

public class Pattern6 extends BasePattern implements IPattern {

    // Symmetric(r1), Asymmetric(r2), r1 subproperty r2
    public void generatePattern() {
        Set<OWLAsymmetricObjectPropertyAxiom> allAsyOP = ont.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY);
        Set<OWLSymmetricObjectPropertyAxiom> allSymOP = ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY);
        if (allAsyOP.size() == 0 || allSymOP.size() == 0) {
            return;
        }
        try {
            this.GetPrintWriter("6");
            for (OWLAsymmetricObjectPropertyAxiom r2 : allAsyOP) {
                OWLObjectPropertyExpression r2_ope = r2.getProperty();
                NodeSet<OWLObjectPropertyExpression> r1s = reasoner.getSubObjectProperties(r2_ope, false);
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
                    for (OWLSymmetricObjectPropertyAxiom r1_symop : allSymOP) {
                        if (r1_symop.getProperty().equals(r2_ope)) {
                            pw.println(r1_symop.getProperty().toString());
                        }
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
