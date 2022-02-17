package TBoxScanner;

import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLObjectPropertyDomainAxiom;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
//this class is to learn patterns for possible domain classes,
// the pattern is used to check the schema correctness of a triple, which is different from IJPs
public class PatternDomain extends BasePattern implements IPattern{
    public void generatePattern() {
        try {
            this.pw = this.GetPrintWriter("pos_domain");
            for (OWLObjectPropertyDomainAxiom doma : this.ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                String Prop = doma.getProperty().getNamedProperty().toString();
                String domainProp = doma.getDomain().toString();
                NodeSet<OWLClass> sof = reasoner.getSubClasses(doma.getDomain());
                pw.print(Prop + "\t" + domainProp + "\"");
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
