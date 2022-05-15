package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLObjectPropertyDomainAxiom;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.io.PrintWriter;

public class Pattern1 extends BasePattern implements IPattern {
    public void generatePattern() {
        try {
            this.pw = this.GetPrintWriter("1");
            for (OWLObjectPropertyDomainAxiom doma : this.ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                //Prop = doma.getProperty().getNamedProperty().getIRI().getShortForm();
                String Prop = doma.getProperty().getNamedProperty().toString();
                String domainProp = doma.getDomain().toString();
                NodeSet<OWLClass> sof = reasoner.getDisjointClasses(doma.getDomain());
                pw.print(Prop + "\t" + domainProp + "\t");
                //pw.print(Prop+"\t");
                for (OWLClass ox : sof.getFlattened()) {
                    //pw.print(ox.getIRI().getShortForm()+"\"");
                    pw.print(ox.toString() + "\"");
                }
                pw.println();

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
