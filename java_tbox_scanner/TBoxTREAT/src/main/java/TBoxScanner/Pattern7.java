package TBoxScanner;

import org.semanticweb.owlapi.model.*;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;

public class Pattern7 extends BasePattern implements IPattern{

    public void generatePattern() {
//the seventh pattern
        String prop1r = new String();
        String prop2r = new String();
        String relation1r = new String();
        String relation2r = new String();
        try {
            this.GetPrintWriter("7");
            for (OWLObjectPropertyRangeAxiom oda1 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                relation1r = oda1.getProperty().getNamedProperty().toString();
                prop1r = oda1.getRange().toString();    //Range1
                prop1r = prop1r.substring(1, prop1r.length() - 1);
                OWLClass oProp1r = factory.getOWLClass(IRI.create(prop1r));

                for (OWLObjectPropertyRangeAxiom oda2 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                    relation2r = oda2.getProperty().getNamedProperty().toString();
                    if (!(relation1r.equalsIgnoreCase(relation2r))) {
                        prop2r = oda2.getRange().toString();    //Range2
                        prop2r = prop2r.substring(1, prop2r.length() - 1);
                        OWLClass oProp2r = factory.getOWLClass(IRI.create(prop2r));
                        if (!(oProp1r.toString().equals(oProp2r.toString()))) { //Range1 != Range2
                            OWLAxiom ax = factory.getOWLDisjointClassesAxiom(Arrays.asList(oProp1r, oProp2r));
                            boolean classesAreDisjoint = reasoner.isEntailed(ax);
                            if (classesAreDisjoint) {   // Range1 disjoint with Range2
                                pw.print(relation1r + "\t");
                                pw.print(relation2r);
                                pw.println();
                                //break;
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
