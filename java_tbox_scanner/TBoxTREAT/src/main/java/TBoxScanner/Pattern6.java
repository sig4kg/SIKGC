package TBoxScanner;

import org.semanticweb.owlapi.model.*;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;

public class Pattern6 extends BasePattern implements IPattern{

    public void generatePattern() {
        //the sixth pattern
        //range of r1 is disjoint with domain of r2
        String relation6_1 = new String();
        String relation6_2 = new String();
        String range6 = new String();
        String doma6 = new String();
        try {
            this.GetPrintWriter("6");
            for (OWLObjectPropertyRangeAxiom ran7 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                relation6_1 = ran7.getProperty().getNamedProperty().toString();
                range6 = ran7.getRange().toString();
                range6 = range6.substring(1, range6.length() - 1);
                OWLClass oRange6 = factory.getOWLClass(IRI.create(range6));
                for (OWLObjectPropertyDomainAxiom objd6 : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                    relation6_2 = objd6.getProperty().getNamedProperty().toString();
                    if (!(relation6_1.equalsIgnoreCase(relation6_2))) {
                        doma6 = objd6.getDomain().toString();
                        doma6 = doma6.substring(1, doma6.length() - 1);
                        OWLClass odoma6 = factory.getOWLClass(IRI.create(doma6));
                        if (!(odoma6.toString().equals(oRange6.toString()))) {
                            OWLAxiom ax6 = factory.getOWLDisjointClassesAxiom(Arrays.asList(oRange6, odoma6));
                            boolean classesAreDisjoint = reasoner.isEntailed(ax6);
                            if (classesAreDisjoint) {
                                pw.print(relation6_1 + "\t");
                                pw.print(relation6_2);
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
