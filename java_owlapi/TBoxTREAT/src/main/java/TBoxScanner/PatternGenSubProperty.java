package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;

public class PatternGenSubProperty extends BasePattern implements IPattern {
    //r1 subpropertyof r2
    public void generatePattern() {
        try {
            pw = this.GetPrintWriter("gen_subproperty");
            for (OWLObjectProperty r2 : ont.getObjectPropertiesInSignature()) {
                NodeSet<OWLObjectPropertyExpression> rsubs = reasoner.getSubObjectProperties(r2, false);
                if (rsubs.getNodes().size() <= 1) {
                    continue;
                }
                //R1
                List<String> r1_names = new ArrayList<>();
                for (Node<OWLObjectPropertyExpression> r1_subProExpression : rsubs.getNodes()) {
                    if (r1_subProExpression.isBottomNode()) {
                        continue;
                    }
                    OWLObjectPropertyExpression r1_subPro = r1_subProExpression.getRepresentativeElement();
                    if (!r1_subPro.isOWLObjectProperty()) {
                        continue;
                    }
                    String r1 = r1_subPro.getNamedProperty().toString();
                    r1_names.add(r1);
                }
                if (r1_names.size() == 0) {
                    continue;
                } else {
                    String line = r2 + "\t" + String.join("@@", r1_names);
                    pw.println(line);
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
