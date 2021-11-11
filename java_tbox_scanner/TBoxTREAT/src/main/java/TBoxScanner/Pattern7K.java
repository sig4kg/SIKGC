package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Iterator;

public class Pattern7K extends BasePattern implements IPattern {

    public void generatePattern() {
        //the tenth pattern (need to remove the duplicate
        //r2 symmetric, r3 asymmetric
        //r1 subclassof r2, r1 subclassof r3,
        //o{utputkan r1
        try {
            this.GetPrintWriter("7");
            String subProprel = new String();
            for (OWLSubObjectPropertyOfAxiom osa10 : ont.getAxioms(AxiomType.SUB_OBJECT_PROPERTY)) {
                subProprel = osa10.getSubProperty().toString();
                OWLObjectPropertyExpression opr10 = osa10.getSubProperty();
                NodeSet<OWLObjectPropertyExpression> nopr10 = reasoner.getSuperObjectProperties(opr10);

                if (nopr10.getNodes().size() > 1) {
                    String check10 = new String();
                    Iterator<Node<OWLObjectPropertyExpression>> itr10 = nopr10.getNodes().iterator();
                    //iterate over the list of SuperProperties
                    int markAsym = 0;
                    int markSym = 0;
                    while (itr10.hasNext()) {
                        check10 = itr10.next().toString();
                        if (!(check10.contentEquals("Node( owl:topObjectProperty )"))) {
                            if (check10.contains("InverseOf")) {
                                String[] superProps = check10.split("InverseOf");
                                if (superProps[0].length() < 8) {
                                    String[] temp = superProps[1].split("\\) ");
                                    if (temp[1].contains("http")) {
                                        temp[1] = temp[1].substring(1, temp[1].length() - 3);
                                        OWLObjectProperty opry10 = factory.getOWLObjectProperty(IRI.create(temp[1]));
                                        for (OWLAsymmetricObjectPropertyAxiom asy : ont.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY)) {
                                            if (asy.getProperty().equals(opry10)) {
                                                markAsym++;
                                                break;
                                            }
                                        }
                                        for (OWLSymmetricObjectPropertyAxiom sym10 : ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY)) {
                                            if (sym10.getProperty().equals(opry10)) {
                                                markSym++;
                                                break;
                                            }
                                        }
                                        if ((markAsym > 0) && (markSym > 0)) {
                                            //ini dia
                                            markAsym = 0;
                                            markSym = 0;
                                            pw.println(subProprel);
                                        }
                                    }
                                } else//list subproperty dimulai dari node dulu bukan inverse, penanganan sbb:
                                {
                                    //String rangeSub = new String();
                                    String[] superPropx10 = superProps[0].split("Node\\( ");
                                    //remove the character < di awal dan > di akhir string
                                    superPropx10[1] = superPropx10[1].substring(1, superPropx10[1].length() - 2);
                                    OWLObjectProperty oprx10 = factory.getOWLObjectProperty(IRI.create(superPropx10[1]));
                                    for (OWLAsymmetricObjectPropertyAxiom asym : ont.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY)) {
                                        if (asym.getProperty().equals(oprx10)) {
                                            //check apakah ada super object property dari subProprel yang symmetric
                                            markAsym++;
                                            break;
                                        }
                                    }
                                    for (OWLSymmetricObjectPropertyAxiom symm10 : ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY)) {
                                        if (symm10.getProperty().equals(oprx10)) {
                                            markSym++;
                                            break;
                                        }
                                    }
                                    if ((markAsym > 0) && (markSym > 0)) {
                                        //ini dia
                                        markAsym = 0;
                                        markSym = 0;
                                        pw.println(subProprel);
                                    }
                                }
                            } else {//check10 tidak mengandung inverse of
                                String[] superProper10 = check10.split("Node\\( ");
                                superProper10[1] = superProper10[1].substring(1, superProper10[1].length() - 3);
                                OWLObjectProperty opj10 = factory.getOWLObjectProperty(IRI.create(superProper10[1]));
                                for (OWLAsymmetricObjectPropertyAxiom asym : ont.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY)) {
                                    if (asym.getProperty().equals(opj10)) {
                                        //check apakah ada super object property dari subProprel yang symmetric
                                        markAsym++;
                                        break;
                                    }
                                }
                                for (OWLSymmetricObjectPropertyAxiom symm10 : ont.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY)) {
                                    if (symm10.getProperty().equals(opj10)) {
                                        markSym++;
                                        break;
                                    }
                                }
                                if ((markAsym > 0) && (markSym > 0)) {
                                    //ini dia
                                    markAsym = 0;
                                    markSym = 0;
                                    pw.println(subProprel);
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
