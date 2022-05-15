package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.util.Arrays;
import java.util.Set;

public class Pattern3 extends BasePattern implements IPattern {
    // domain(r1)=D1, domain(r2)=D2, r1 subpropertyof r2, D1 disjoint D2
    public void generatePattern() {
        try {
            pw = this.GetPrintWriter("3");
            for (OWLObjectPropertyDomainAxiom r2PDA : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                OWLObjectProperty r2_p = r2PDA.getProperty().getNamedProperty();
                String r2_domain = r2PDA.getDomain().toString();
                NodeSet<OWLObjectPropertyExpression> r1OPEs = reasoner.getSubObjectProperties(r2_p, false);
                if (r1OPEs.getNodes().size() <= 1) {
                    continue;
                }
                //R1
                for (Node<OWLObjectPropertyExpression> r1_subProExpression : r1OPEs.getNodes()) {
                    if (r1_subProExpression.isBottomNode()) {
                        continue;
                    }
                    OWLObjectPropertyExpression r1_subPro = r1_subProExpression.getRepresentativeElement();
                    if (!r1_subPro.isOWLObjectProperty()) {
                        continue;
                    }
                    Set<OWLObjectPropertyAxiom> r1_ProDoma = ont.getAxioms(r1_subPro);
                    for (OWLObjectPropertyAxiom opa : r1_ProDoma) {
                        if (opa.isOfType(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                            String r1_domain = r2PDA.getDomain().toString();
                            if (r2_domain.equals(r1_domain)) {
                                continue;
                            }
                            OWLClass oSup = factory.getOWLClass(r2_domain);
                            OWLClass oSub = factory.getOWLClass(r1_domain);
                            OWLAxiom disjointAxiom = factory.getOWLDisjointClassesAxiom(Arrays.asList(oSup, oSub));
                            boolean classesAreDisjoint = reasoner.isEntailed(disjointAxiom);
                            if (classesAreDisjoint) {
                                pw.println(r1_subPro.getNamedProperty().toString());
                            }
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
