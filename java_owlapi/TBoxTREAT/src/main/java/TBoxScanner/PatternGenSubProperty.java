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
    //r1 subpropertyof r2  -> r1 r2@@r22@@r222
    public void generatePattern() {
        try {
            pw = this.GetPrintWriter("gen_subproperty");
            for (OWLObjectProperty r1 : ont.getObjectPropertiesInSignature()) {
                NodeSet<OWLObjectPropertyExpression> rsups = reasoner.getSuperObjectProperties(r1, false);
                if (rsups.getNodes().size() <= 1) {
                    continue;
                }
                //R2s
                List<String> r2_names = new ArrayList<>();
                for (Node<OWLObjectPropertyExpression> r2_supProExpression : rsups.getNodes()) {
                    if (r2_supProExpression.isBottomNode()) {
                        continue;
                    }
                    OWLObjectPropertyExpression r2_supPro = r2_supProExpression.getRepresentativeElement();
                    if (!r2_supPro.isOWLObjectProperty()) {
                        continue;
                    }
                    String r2 = r2_supPro.getNamedProperty().toString();
                    r2_names.add(r2);
                }
                if (r2_names.size() == 0) {
                    continue;
                } else {
                    String line = r1 + "\t" + String.join("@@", r2_names);
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
