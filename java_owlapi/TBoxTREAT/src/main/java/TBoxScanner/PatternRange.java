package TBoxScanner;

import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLObjectPropertyRangeAxiom;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;

//this class is to learn patterns for possible range classes,
// the pattern is used to check the schema correctness of a triple, which is different from IJPs
public class PatternRange extends BasePattern implements IPattern{
    public void generatePattern() {
        try {
            this.pw = this.GetPrintWriter("pos_range");
            for (OWLObjectPropertyRangeAxiom range : this.ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                String Prop = range.getProperty().getNamedProperty().toString();
                String ranProp = range.getRange().toString();
                NodeSet<OWLClass> sof = reasoner.getSubClasses(range.getRange());
                pw.print(Prop + "\t" + ranProp + "\"");
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
