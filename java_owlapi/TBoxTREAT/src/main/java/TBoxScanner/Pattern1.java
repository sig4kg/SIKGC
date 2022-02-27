package TBoxScanner;

import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLObjectPropertyDomainAxiom;
import org.semanticweb.owlapi.reasoner.NodeSet;
import java.io.IOException;
import java.io.PrintWriter;
import org.semanticweb.owlapi.model.*;

import java.util.HashSet;
import java.util.Set;


public class Pattern1 extends BasePattern implements IPattern{
    public void generatePattern() {
        try {
            this.pw = this.GetPrintWriter("1");
            for (OWLObjectProperty ops : ont.getObjectPropertiesInSignature()) {
                Set<OWLClass> doma = reasoner.getObjectPropertyDomains(ops).getFlattened();
                if (doma.size() == 0) {
                    continue;
                }
                Set<String> domainProps = new HashSet<>();
                Set<String> disjoints = new HashSet<>();
                for (OWLClass d : doma) {
                    domainProps.add(d.getIRI().toString());
                    Set<OWLClass> disjs = reasoner.getDisjointClasses(d).getFlattened();
                    for (OWLClass dis : disjs) {
                        disjoints.add(dis.getIRI().toString());
                    }
                }
                pw.print(ops.getIRI().toString() + "\t");
                for (String domain : domainProps) {
                    pw.print(domain + "\"");
                }
                pw.print("\t");
                for (String disStr : disjoints) {
                    pw.print(disStr + "\"");
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
