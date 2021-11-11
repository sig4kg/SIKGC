package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;

public class Pattern3 extends BasePattern implements IPattern{

    public void generatePattern() {
        try {
            pw = this.GetPrintWriter("3");
            for (OWLObjectProperty prop : ont.getObjectPropertiesInSignature()) {   //R2
                NodeSet<OWLObjectPropertyExpression> properties = reasoner.getSubObjectProperties(prop, false);
                //if the size == 1, it means the property does not have any subobject property.
                if (properties.getNodes().size() > 1) { //R2 has subobjects
                    String domaSup = new String();
                    String relations = new String();
                    for (OWLObjectPropertyDomainAxiom op : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) { // all domains
                        if (op.getProperty().equals(prop.getNamedProperty())) {
                            //System.out.print(op.getProperty().toString()+"\t");
                            //System.out.println(op.getDomain().toString());
                            relations = op.getProperty().toString();    //R2
                            domaSup = op.getDomain().toString(); //D(R2)
                            domaSup = domaSup.substring(1, domaSup.length() - 1);
                        }
                    }
                    String check = new String();
                    java.util.Iterator<Node<OWLObjectPropertyExpression>> itr = properties.getNodes().iterator(); //R1
                    while (itr.hasNext()) {
                        //SubProps[0] contain subProperty from Property prop
                        //visit first element of subproperty
                        //String[] subProps = properties.getNodes().iterator().next().toString().split("InverseOf");
                        //before splitting based on InverseOf, check whether itr contains only Node( owl:bottomObjectProperty )]
                        check = itr.next().toString();
                        if (!(check.contentEquals("Node( owl:bottomObjectProperty )"))) {
                            //working only for the ontology that has Inverse in the text file for each property
                            String domaSub1 = new String();
                            if (check.contains("InverseOf")) {
                                String[] subProps = check.split("InverseOf");
                                if (subProps[0].length() < 8) {
                                    //if list subproperty dimulai dari inverse dulu, maka penanganannya sbb:
                                    String[] temp = subProps[1].split("\\) ");
                                    //temp[1] adalah nama subproperty yang dicari.
                                    //untuk pattern 3,4 harus dicek dulu apakah temp1 punya http atau tidak ?
                                    //kalau punya http code berikut bisa jalan, kalau tidak cari cara lain
                                    //kalau temp[1] tidak memiliki http berarti bukan subproperty yang penting utk diproses
                                    if (temp[1].contains("http")) {
                                        temp[1] = temp[1].substring(1, temp[1].length() - 3);
                                        OWLObjectProperty opry = factory.getOWLObjectProperty(IRI.create(temp[1]));
                                        for (OWLObjectPropertyDomainAxiom opsi : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                                            if (opsi.getProperty().equals(opry)) {
                                                //System.out.print(opsi.getProperty().toString()+"\t");
                                                //System.out.print(opsi.getDomain().toString());
                                                //System.out.println();
                                                domaSub1 = opsi.getDomain().toString();
                                                domaSub1 = domaSub1.substring(1, domaSub1.length() - 1);
                                                OWLClass oSup = factory.getOWLClass(IRI.create(domaSup));
                                                OWLClass oSub1 = factory.getOWLClass(IRI.create(domaSub1));
                                                //jika Osup dan Osub1 berbeda stringnya, baru dicheck sama reasoner
                                                if (!(oSup.toString().equals(oSub1.toString()))) {
                                                    OWLAxiom axiom = factory.getOWLDisjointClassesAxiom(Arrays.asList(oSup, oSub1));
                                                    boolean classesAreDisjoint = reasoner.isEntailed(axiom);
                                                    if (classesAreDisjoint) {
                                                        //pw.println(relations);
                                                        pw.println(opry.toString());
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }//end dari if(subProps[0].length()<8)
                                else {
                                    String domaSub = new String();
                                    String[] subPropx = subProps[0].split("Node\\( ");
                                    //remove the character < di awal dan > di akhir string
                                    subPropx[1] = subPropx[1].substring(1, subPropx[1].length() - 2);
                                    OWLObjectProperty oprx = factory.getOWLObjectProperty(IRI.create(subPropx[1]));
                                    for (OWLObjectPropertyDomainAxiom ops : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                                        if (ops.getProperty().equals(oprx)) {
                                            //System.out.print(ops.getProperty().toString()+"\t");
                                            //System.out.print(ops.getDomain().toString());
                                            //System.out.println();
                                            domaSub = ops.getDomain().toString();
                                            domaSub = domaSub.substring(1, domaSub.length() - 1);
                                            OWLClass oSup = factory.getOWLClass(IRI.create(domaSup));
                                            OWLClass oSub = factory.getOWLClass(IRI.create(domaSub));
                                            if (!(oSup.toString().equals(oSub.toString()))) {
                                                OWLAxiom axiom = factory.getOWLDisjointClassesAxiom(Arrays.asList(oSup, oSub));
                                                boolean classesAreDisjoint = reasoner.isEntailed(axiom);
                                                if (classesAreDisjoint) {
                                                    //pw.println(relations);
                                                    pw.println(oprx.toString());
                                                }
                                            }
                                        }
                                    }
                                }
                            }//if(check.contains("InverseOf"))
                            else {
                                //jika check tidak ada InverseOf
                                String domaSub = new String();
                                String[] subPropx = check.split("Node\\( ");
                                //remove the character < di awal dan > di akhir string
                                subPropx[1] = subPropx[1].substring(1, subPropx[1].length() - 3);
                                OWLObjectProperty oprx = factory.getOWLObjectProperty(IRI.create(subPropx[1]));
                                for (OWLObjectPropertyDomainAxiom ops : ont.getAxioms(AxiomType.OBJECT_PROPERTY_DOMAIN)) {
                                    if (ops.getProperty().equals(oprx)) {
                                        //System.out.print(ops.getProperty().toString()+"\t");
                                        //System.out.print(ops.getDomain().toString());
                                        //System.out.println();
                                        domaSub = ops.getDomain().toString();
                                        domaSub = domaSub.substring(1, domaSub.length() - 1);
                                        OWLClass oSup = factory.getOWLClass(IRI.create(domaSup));
                                        OWLClass oSub = factory.getOWLClass(IRI.create(domaSub));
                                        if (!(oSup.toString().equals(oSub.toString()))) {
                                            OWLAxiom axiom = factory.getOWLDisjointClassesAxiom(Arrays.asList(oSup, oSub));
                                            boolean classesAreDisjoint = reasoner.isEntailed(axiom);
                                            if (classesAreDisjoint) {
                                                pw.println(oprx.toString());
                                                //pw.println(relations);
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
