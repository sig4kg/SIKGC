package TBoxScanner.deprecates;

import TBoxScanner.BasePattern;
import TBoxScanner.IPattern;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.util.Iterator;
import java.util.Set;

public class PatternGenSymetric extends BasePattern implements IPattern {
    // Symmetric(r)
    public void generatePattern() {
        try {
            this.GetPrintWriter("gen_symetric");
            for (OWLSymmetricObjectPropertyAxiom r : ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY)) {
                pw.println(r.getProperty().toString());
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
