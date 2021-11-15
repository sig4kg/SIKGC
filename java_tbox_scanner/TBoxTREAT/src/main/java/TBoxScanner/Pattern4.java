package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.util.Arrays;
import java.util.Set;

public class Pattern4 extends BasePattern implements IPattern {
//Range(r1)=R1, Range(r2)=R2, r1 in r2, R1 disjoint R2
    public void generatePattern() {
        try {
            pw = this.GetPrintWriter("4");
            for (OWLObjectPropertyRangeAxiom proRange : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                OWLObjectProperty r2_p = proRange.getProperty().getNamedProperty();
//                IRI r2_iri = r2_p.getIRI();
                NodeSet<OWLObjectPropertyExpression> subProperties = reasoner.getSubObjectProperties(r2_p, false);
                if (subProperties.getNodes().size() <= 1) {
                    continue;
                }
                String r2_range = proRange.getRange().toString();
                //R1
                for (Node<OWLObjectPropertyExpression> subProExpression : subProperties.getNodes()) {
                    if (subProExpression.isBottomNode()) {
                        continue;
                    }
                    OWLObjectPropertyExpression r1_subPro = subProExpression.getRepresentativeElement();
                    if (!r1_subPro.isOWLObjectProperty()) {
                        continue;
                    }
                    Set<OWLObjectPropertyAxiom> r1_opa = ont.getAxioms(r1_subPro);
                    for (OWLObjectPropertyAxiom opa : r1_opa) {
                        if (opa.isOfType(AxiomType.OBJECT_PROPERTY_RANGE)) {
                            String r1_range = proRange.getRange().toString();
                            if (r2_range.equals(r1_range)) {
                                continue;
                            }
                            OWLClass oSup = factory.getOWLClass(r2_range);
                            OWLClass oSub = factory.getOWLClass(r1_range);
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
