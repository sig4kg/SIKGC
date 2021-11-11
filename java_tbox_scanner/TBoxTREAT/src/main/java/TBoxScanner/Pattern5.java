package TBoxScanner;

import org.semanticweb.owlapi.model.*;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;

public class Pattern5 extends BasePattern implements IPattern{

    public void generatePattern() {
        try {
            this.GetPrintWriter("5");
            long start5Time = System.nanoTime();
            //we disable pattern 5 until 7 for ISWC publication (because it is too long)
            //the fifth pattern
            String prop1 = new String();
            String prop2 = new String();
            String relation1 = new String();
            String relation2 = new String();
            for (OWLObjectPropertyDomainAxiom oda1 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                relation1 = oda1.getProperty().getNamedProperty().toString();
                prop1 = oda1.getDomain().toString(); // D1
                prop1 = prop1.substring(1, prop1.length() - 1);
                OWLClass oProp1 = factory.getOWLClass(IRI.create(prop1));

                for (OWLObjectPropertyDomainAxiom oda2 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                    relation2 = oda2.getProperty().getNamedProperty().toString();
                    if (!(relation1.equalsIgnoreCase(relation2))) {
                        prop2 = oda2.getDomain().toString();    // D2
                        prop2 = prop2.substring(1, prop2.length() - 1);
                        OWLClass oProp2 = factory.getOWLClass(IRI.create(prop2));
                        if (!(oProp2.toString().equals(oProp1.toString()))) {   // D1 != D2
                            OWLAxiom ax = factory.getOWLDisjointClassesAxiom(Arrays.asList(oProp1, oProp2));
                            boolean classesAreDisjoint = reasoner.isEntailed(ax);
                            if (classesAreDisjoint) {   // D1 and D2 disjoint
                                pw.print(relation1 + "\t");
                                pw.print(relation2);
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
//        long end5Time = System.nanoTime();
//        System.out.println("module 5 took "+((end5Time-start5Time)/1000000)+" ms");
    }
}
