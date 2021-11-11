package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Iterator;

public class Pattern6K extends BasePattern implements IPattern{

    public void generatePattern() {
//the ninth pattern
        try {
            this.GetPrintWriter("9");
            for (OWLAsymmetricObjectPropertyAxiom oba9 : ont.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY)) {
                OWLObjectPropertyExpression expr = oba9.getProperty();
                NodeSet<OWLObjectPropertyExpression> properties9 = reasoner.getSubObjectProperties(expr, false);
                //if the size == 1, it means the property does not have any subobject property.
                if (properties9.getNodes().size() > 1) {
                    //cek apakah properties9 ada yang symmetric.
                    String check9 = new String();
                    Iterator<Node<OWLObjectPropertyExpression>> itr9 = properties9.getNodes().iterator();
                    while (itr9.hasNext()) {
                        check9 = itr9.next().toString();
                        if (!(check9.contentEquals("Node( owl:bottomObjectProperty )"))) {
                            if (check9.contains("InverseOf")) {
                                String[] subProps = check9.split("InverseOf");
                                if (subProps[0].length() < 8) {
                                    String[] temp = subProps[1].split("\\) ");
                                    temp[1] = temp[1].substring(1, temp[1].length() - 3);
                                    OWLObjectProperty opry9 = factory.getOWLObjectProperty(IRI.create(temp[1]));
                                    for (OWLSymmetricObjectPropertyAxiom osa9 : ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY)) {
                                        if (osa9.getProperty().equals(opry9)) {
                                            pw.println(osa9.getProperty().toString());
                                        }
                                    }
                                } else//list subproperty dimulai dari node dulu bukan inverse, penanganan sbb:
                                {
                                    //String rangeSub = new String();
                                    String[] subPropx9 = subProps[0].split("Node\\( ");
                                    //remove the character < di awal dan > di akhir string
                                    subPropx9[1] = subPropx9[1].substring(1, subPropx9[1].length() - 2);
                                    OWLObjectProperty oprx9 = factory.getOWLObjectProperty(IRI.create(subPropx9[1]));
                                    //for (OWLObjectPropertyRangeAxiom ops : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                                    for (OWLSymmetricObjectPropertyAxiom osa9 : ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY)) {
                                        if (osa9.getProperty().equals(oprx9)) {
                                            pw.println(osa9.getProperty().toString());
                                        }
                                    }
                                }
                            } else {
                                String[] subPropx9 = check9.split("Node\\( ");
                                subPropx9[1] = subPropx9[1].substring(1, subPropx9[1].length() - 3);
                                //temp[1]=temp[1].substring(1,temp[1].length()-3);
                                OWLObjectProperty opry9 = factory.getOWLObjectProperty(IRI.create(subPropx9[1]));
                                for (OWLSymmetricObjectPropertyAxiom osa9 : ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY)) {
                                    if (osa9.getProperty().equals(opry9)) {
                                        pw.println(osa9.getProperty().toString());
                                    }
                                }
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
