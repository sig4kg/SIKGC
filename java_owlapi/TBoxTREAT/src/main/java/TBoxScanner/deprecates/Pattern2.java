package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLObjectPropertyRangeAxiom;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.io.PrintWriter;

public class Pattern2 extends BasePattern implements IPattern {
    public void generatePattern() {
        try {
            pw = this.GetPrintWriter("2");
            for (OWLObjectPropertyRangeAxiom rang : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                //Range = rang.getProperty().getNamedProperty().getIRI().getShortForm();
                String Range = rang.getProperty().getNamedProperty().toString();
                String rangeProp = rang.getRange().toString();
                NodeSet<OWLClass> sof3 = reasoner.getDisjointClasses(rang.getRange());
                pw.print(Range + "\t" + rangeProp + "\t");
                //pw.print(Range+"\t");
                for (OWLClass ox : sof3.getFlattened()) {
                    pw.print(ox.toString() + "\"");
                    //untuk IBM menggunakan short form, untuk dbpedia full url
                    //pw.print(ox.toString()+"\"");
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

