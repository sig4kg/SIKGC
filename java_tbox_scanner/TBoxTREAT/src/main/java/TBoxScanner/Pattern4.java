package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;

public class Pattern4 extends BasePattern implements IPattern{

    public void generatePattern() {
        try {
            pw = this.GetPrintWriter("4");
            for (OWLObjectProperty prop : ont.getObjectPropertiesInSignature()) {
                NodeSet<OWLObjectPropertyExpression> properties = reasoner.getSubObjectProperties(prop, false);
                //if the size == 1, it means the property does not have any subobject property.
                if (properties.getNodes().size() > 1) {
                    String rangeSup = new String();
                    String relations = new String();
                    for (OWLObjectPropertyRangeAxiom op : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                        if (op.getProperty().equals(prop.getNamedProperty())) {
                            //System.out.print(op.getProperty().toString()+"\t");
                            //System.out.println(op.getDomain().toString());
                            relations = op.getProperty().toString();
                            rangeSup = op.getRange().toString();
                            rangeSup = rangeSup.substring(1, rangeSup.length() - 1);
                        }
                    }
                    String check = new String();
                    java.util.Iterator<Node<OWLObjectPropertyExpression>> itr = properties.getNodes().iterator();
                    while (itr.hasNext()) {
                        //SubProps[0] berisikan subProperty dari Property prop
                        //akses elemen pertama dari subproperty
                        //String[] subProps = properties.getNodes().iterator().next().toString().split("InverseOf");
                        //before splitting based on InverseOf, check whether itr contains only Node( owl:bottomObjectProperty )]
                        check = itr.next().toString();
                        System.out.println("Cek " + check);
                        if (!(check.contentEquals("Node( owl:bottomObjectProperty )"))) {
                            //working only for the ontology that has Inverse of for each property
                            String rangeSub1 = new String();
                            if (check.contains("InverseOf")) {
                                String[] subProps = check.split("InverseOf");

                                if (subProps[0].length() < 8) {
                                    //if list subproperty dimulai dari inverse dulu, maka penanganannya sbb:
                                    String[] temp = subProps[1].split("\\) ");
                                    //temp[1] adalah nama subproperty yang dicari.
                                    if (temp[1].contains("http")) {
                                        temp[1] = temp[1].substring(1, temp[1].length() - 3);
                                        OWLObjectProperty opry = factory.getOWLObjectProperty(IRI.create(temp[1]));
                                        for (OWLObjectPropertyRangeAxiom opsi : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                                            if (opsi.getProperty().equals(opry)) {
                                                rangeSub1 = opsi.getRange().toString();
                                                rangeSub1 = rangeSub1.substring(1, rangeSub1.length() - 1);
                                                OWLClass oSup = factory.getOWLClass(IRI.create(rangeSup));
                                                OWLClass oSub1 = factory.getOWLClass(IRI.create(rangeSub1));
                                                if (!(oSup.toString().equals(oSub1.toString()))) {
                                                    OWLAxiom axiom = factory.getOWLDisjointClassesAxiom(Arrays.asList(oSup, oSub1));
                                                    boolean classesAreDisjoint = reasoner.isEntailed(axiom);
                                                    if (classesAreDisjoint) {
                                                        pw.println(relations);
                                                    }
                                                }
                                            }
                                        }
                                    }
                                } else {
                                    String rangeSub = new String();
                                    String[] subPropx = subProps[0].split("Node\\( ");
                                    //remove the character < di awal dan > di akhir string
                                    subPropx[1] = subPropx[1].substring(1, subPropx[1].length() - 2);
                                    OWLObjectProperty oprx = factory.getOWLObjectProperty(IRI.create(subPropx[1]));
                                    for (OWLObjectPropertyRangeAxiom ops : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                                        if (ops.getProperty().equals(oprx)) {
                                            //System.out.print(ops.getProperty().toString()+"\t");
                                            //System.out.print(ops.getDomain().toString());
                                            //System.out.println();
                                            rangeSub = ops.getRange().toString();
                                            rangeSub = rangeSub.substring(1, rangeSub.length() - 1);
                                            OWLClass oSup = factory.getOWLClass(IRI.create(rangeSup));
                                            OWLClass oSub = factory.getOWLClass(IRI.create(rangeSub));
                                            if (!(oSup.toString().equals(oSub.toString()))) {
                                                OWLAxiom axiom = factory.getOWLDisjointClassesAxiom(Arrays.asList(oSup, oSub));
                                                boolean classesAreDisjoint = reasoner.isEntailed(axiom);
                                                if (classesAreDisjoint) {
                                                    pw.println(relations);
                                                }
                                            }
                                        }
                                    }
                                }
                            }//if(check.contains("InverseOf"))
                            else {
                                //jika check tidak ada InverseOf
                                //perlu didebugging lagi belum masuk kesini...
                                String rangeSub = new String();
                                String[] subPropx = check.split("Node\\( ");
                                //remove the character < di awal dan > di akhir string
                                subPropx[1] = subPropx[1].substring(1, subPropx[1].length() - 3);
                                OWLObjectProperty oprx = factory.getOWLObjectProperty(IRI.create(subPropx[1]));
                                for (OWLObjectPropertyRangeAxiom ops : ont.getAxioms(AxiomType.OBJECT_PROPERTY_RANGE)) {
                                    if (ops.getProperty().equals(oprx)) {
                                        //System.out.print(ops.getProperty().toString()+"\t");
                                        //System.out.print(ops.getDomain().toString());
                                        //System.out.println();
                                        rangeSub = ops.getRange().toString();
                                        rangeSub = rangeSub.substring(1, rangeSub.length() - 1);
                                        OWLClass oSup = factory.getOWLClass(IRI.create(rangeSup));
                                        OWLClass oSub = factory.getOWLClass(IRI.create(rangeSub));
                                        if (!(oSup.toString().equals(oSub.toString()))) {
                                            OWLAxiom axiom = factory.getOWLDisjointClassesAxiom(Arrays.asList(oSup, oSub));
                                            boolean classesAreDisjoint = reasoner.isEntailed(axiom);
                                            if (classesAreDisjoint) {
                                                pw.println(relations);
                                            }
                                        }
                                    }
                                }
                            }
                        }//end dari if(!(check.contentEquals("Node( owl:bottomObjectProperty )")))
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
