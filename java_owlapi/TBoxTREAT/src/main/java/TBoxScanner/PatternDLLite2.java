package TBoxScanner;

import org.semanticweb.owlapi.model.*;
import uk.ac.manchester.cs.owl.owlapi.OWLObjectSomeValuesFromImpl;

import java.io.IOException;
import java.util.*;


public class PatternDLLite2 extends BasePattern implements IPattern {
    public final Map<OWLClassExpression, Set<OWLClassExpression>> _sub2Sups = new HashMap<>();
    Map<OWLObjectPropertyExpression, Set<OWLObjectPropertyExpression>> Rsup2Rsubs = new HashMap<>();
    Map<OWLObjectPropertyExpression, Set<OWLObjectPropertyExpression>> Rsup2RIvsSubs = new HashMap<>();

    public void generatePattern() {
        cache_subsumptions();
        generateOPPattern();
        generateFuncPattern();
    }

    private <T> void add2map(T key, T value, Map<T, Set<T>> cache_map) {
        if (cache_map.containsKey(key)) {
            cache_map.get(key).add(value);
        } else {
            Set<T> tmpAxioms = new HashSet<T>();
            tmpAxioms.add(value);
            cache_map.put(key, tmpAxioms);
        }
    }

    private void cache_subsumptions() {
        //cache all class subsumptions
        Collection<OWLSubClassOfAxiom> axioms = this.ont.getAxioms(AxiomType.SUBCLASS_OF);
        for (OWLSubClassOfAxiom ax : axioms) {
            OWLClassExpression sub = ax.getSubClass();
            OWLClassExpression sup = ax.getSuperClass();
            add2map(sub, sup, _sub2Sups);
        }
        //cache R and R- subsumptions
        Collection<OWLSubObjectPropertyOfAxiom> axiomsOP = this.ont.getAxioms(AxiomType.SUB_OBJECT_PROPERTY);
        for (OWLSubObjectPropertyOfAxiom ax : axiomsOP) {
            OWLObjectPropertyExpression sub = ax.getSubProperty();
            OWLObjectPropertyExpression sup = ax.getSuperProperty();
            if (sub == sup || !sup.isNamed()) {
                continue;
            }
            if (sub.isNamed()) {
                add2map(sup, sub, Rsup2Rsubs);
            } else {
                add2map(sup, sub, Rsup2RIvsSubs);
            }
        }
    }

    private void writeMap2File(String fileName, Map<String, Set<String>> map) {
        try {
            this.pw = this.GetPrintWriter(fileName);
            for (String fi : map.keySet()) {
                Set<String> value_l = map.get(fi);
                String line = fi + "\t" + String.join("@@", value_l);
                pw.println(line);
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

    private void writeList2File(String fileSuffix, List<String> l) {
        try {
            this.pw = this.GetPrintWriter(fileSuffix);
            for (String fi : l) {
                pw.println(fi);
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

    private Boolean isDisjoint(OWLClassExpression a, OWLClassExpression b) {
        Set<OWLClassExpression> D1sups = _sub2Sups.get(a);
        Set<OWLClassExpression> D2sups = _sub2Sups.get(b);
        if (D1sups.contains(b.getObjectComplementOf()) || D2sups.contains(a.getObjectComplementOf())) {
            return Boolean.TRUE;
        } else {
            return Boolean.FALSE;
        }
    }


    public void generateOPPattern() {
        if (_sub2Sups.size() == 0) {
            cache_subsumptions();
        }
        // consider \some R1 \cap D -> \bot, ---> \some R1 subclassof \neg D and D subclassof \neg \some R1
        // inverse \some R1 \cap D -> \bot,
        Map<String, Set<String>> domain_Pattern = new HashMap<>();
        Map<String, Set<String>> e1r1e2_e1r2e3 = new HashMap<>();
        Map<String, Set<String>> e1r1e2_e3r2e1 = new HashMap<>();
        Map<String, Set<String>> range_Pattern = new HashMap<>();
        Map<String, Set<String>> e2r1e1_e1r2e3 = new HashMap<>();
        Map<String, Set<String>> e2r1e1_e3r2e1 = new HashMap<>();
        Map<String, Set<String>> C2Cs = new HashMap<>();
        Map<String, Set<String>> C2ERs = new HashMap<>();
        Map<String, Set<String>> C2ERInvs = new HashMap<>();
        for (OWLClassExpression D1 : _sub2Sups.keySet()) {
            ClassExpressionType cet = D1.getClassExpressionType();
            if (cet.equals(ClassExpressionType.OBJECT_COMPLEMENT_OF)) {
                continue;
            }
            Set<OWLClassExpression> sups = _sub2Sups.get(D1);
            //types
            if (D1.isNamed()) {
                for (OWLClassExpression sup : sups) {
                    ClassExpressionType cetSup = sup.getClassExpressionType();
                    if (cetSup.equals(ClassExpressionType.OBJECT_COMPLEMENT_OF)) { // A1 subclassof \neg D2
                        OWLClassExpression D2 = sup.getComplementNNF();
                        if (!isDisjoint(D1, D2)) {
                            continue;
                        }
                        ClassExpressionType cetD2 = D2.getClassExpressionType();
                        // ER1, ER2
                        if (D2.isNamed()) {
                            add2map(D1.toString(), D2.toString(), C2Cs);
                            continue;
                        }
                        if (cetD2.equals(ClassExpressionType.OBJECT_SOME_VALUES_FROM)) {
                            OWLObjectPropertyExpression r2 = ((OWLObjectSomeValuesFromImpl) D2).getProperty();
                            if (r2.isNamed()) {
                                add2map(D1.toString(), r2.toString(), C2ERs);
                                continue;
                            }
                            if (r2.isObjectPropertyExpression() && r2.getInverseProperty().isNamed()) {
                                add2map(D1.toString(), r2.toString(), C2ERInvs);
                            }
                        }
                    }
                }
                continue;
            }
            // \some R
            if (!cet.equals(ClassExpressionType.OBJECT_SOME_VALUES_FROM)) {
                continue;
            }
            OWLObjectPropertyExpression r1 = ((OWLObjectSomeValuesFromImpl) D1).getProperty();
            if (r1.isNamed()) {
                for (OWLClassExpression sup : sups) {
                    ClassExpressionType cetSup = sup.getClassExpressionType();
                    if (cetSup.equals(ClassExpressionType.OBJECT_COMPLEMENT_OF)) { // D1 subclassof \neg D2
                        OWLClassExpression D2 = sup.getComplementNNF();
                        ClassExpressionType cetD2 = D2.getClassExpressionType();
                        if (!isDisjoint(D1, D2)) {
                            continue;
                        }
                        // ER1, ER2
                        if (D2.isNamed()) {
                            add2map(r1.toString(), D2.toString(), domain_Pattern);
                            continue;
                        }
                        if (cetD2.equals(ClassExpressionType.OBJECT_SOME_VALUES_FROM)) {
                            OWLObjectPropertyExpression r2 = ((OWLObjectSomeValuesFromImpl) D2).getProperty();
                            if (r2.isNamed()) {
                                add2map(r1.toString(), r2.toString(), e1r1e2_e1r2e3);
                                continue;
                            }
                            if (r2.isObjectPropertyExpression() && r2.getInverseProperty().isNamed()) {
                                add2map(r1.toString(), r2.toString(), e1r1e2_e3r2e1);
                            }
                        }
                    }
                }
                continue;
            }
            // ER-
            if (r1.isObjectPropertyExpression() && r1.getInverseProperty().isNamed()) {
                for (OWLClassExpression sup : sups) {
                    ClassExpressionType cetSup = sup.getClassExpressionType();
                    if (cetSup.equals(ClassExpressionType.OBJECT_COMPLEMENT_OF)) { // D1 subclassof \neg D2
                        OWLClassExpression D2 = sup.getComplementNNF();
                        if (!isDisjoint(D1, D2)) {
                            continue;
                        }
                        // ER1, ER2
                        ClassExpressionType cetD2 = D2.getClassExpressionType();
                        if (D2.isNamed()) {
                            add2map(r1.getInverseProperty().toString(), D2.toString(), range_Pattern);
                            continue;
                        }
                        if (cetD2.equals(ClassExpressionType.OBJECT_SOME_VALUES_FROM)) {
                            OWLObjectPropertyExpression r2 = ((OWLObjectSomeValuesFromImpl) D2).getProperty();
                            if (r2.isNamed()) {
                                add2map(r1.toString(), r2.toString(), e2r1e1_e1r2e3);
                                continue;
                            }
                            if (r2.isObjectPropertyExpression() && r2.getInverseProperty().isNamed()) {
                                add2map(r1.toString(), r2.toString(), e2r1e1_e3r2e1);
                            }
                        }
                    }
                }
            }
        }
        writeMap2File("PatternNegDomain.txt", domain_Pattern);
        writeMap2File("PatternNegRange.txt", range_Pattern);
        writeMap2File("Pattern_e1r1e2_e1r2e3.txt", e1r1e2_e1r2e3);
        writeMap2File("Pattern_e1r1e2_e3r2e1.txt", e1r1e2_e3r2e1);
        writeMap2File("Pattern_e2r1e1_e1r2e3.txt", e2r1e1_e1r2e3);
        writeMap2File("Pattern_e2r1e1_e3r2e1.txt", e2r1e1_e3r2e1);
        writeMap2File("PatternTypeDisjointC.txt", C2Cs);
        writeMap2File("PatternTypeDisjointER.txt", C2ERs);
        writeMap2File("PatternTypeDisjointERInvs.txt", C2ERInvs);
    }

    public void generateFuncPattern() {
        if (_sub2Sups.size() == 0) {
            cache_subsumptions();
        }
        // 1. Func(r1)   (e1, r1, e2), (e1, r1, e3)
        // SubObjectPropertyOf(r1, r2)  r1 -> r2; eg: SubObjectPropertyOf( :hasWife :hasSpouse )
        // 2. Func(r1) and SubObjectPropertyOf(r2, r1)     (e1, r1, e2), (e1, r2, e3) or (e1, r2, e2), (e1, r2, e3)
        // 3. Func(r1) and SubObjectPropertyOf(r2-, r1)     (e1, r1, e2), (e3, r2, e1) or (e3, r2, e1), (e2, r2, e1)
        Set<String> func_e1r1e2_e1r1e3 = new HashSet<>();
        Map<String, Set<String>> func_e1r1e2e1r2e3_e1r2e2e1r2e3 = new HashMap<String, Set<String>>();
        Map<String, Set<String>> func_e1r1e2e3r2e1_e2r2e1e3r2e1 = new HashMap<String, Set<String>>();
        List<OWLObjectPropertyExpression> functional = new ArrayList<>();
        // 1. Func(r1)   (e1, r1, e2), (e1, r1, e3)
        for (OWLFunctionalObjectPropertyAxiom funcp : ont.getAxioms(AxiomType.FUNCTIONAL_OBJECT_PROPERTY)) {
            func_e1r1e2_e1r1e3.add(funcp.getProperty().toString());
            functional.add(funcp.getProperty());
        }
        for (OWLObjectPropertyExpression r1Exp : functional) {
            String r1 = r1Exp.toString();
            // 2. Func(r1) and SubObjectPropertyOf(r2, r1)     (e1, r1, e2), (e1, r2, e3) or (e1, r2, e2), (e1, r2, e3)
            if (Rsup2Rsubs.containsKey(r1Exp)) {
                Set<OWLObjectPropertyExpression> possible_r2exp = Rsup2Rsubs.get(r1Exp);
                Set<String> r2 = new HashSet<>();
                possible_r2exp.forEach(e -> r2.add(e.getNamedProperty().toString()));
                func_e1r1e2e1r2e3_e1r2e2e1r2e3.put(r1, r2);
            }
            // 3. Func(r1) and SubObjectPropertyOf(r2-, r1)     (e1, r1, e2), (e3, r2, e1) or (e3, r2, e1), (e2, r2, e1)
            if (Rsup2RIvsSubs.containsKey(r1Exp)) {
                Set<OWLObjectPropertyExpression> possible_r2exp = Rsup2RIvsSubs.get(r1Exp);
                Set<String> r2 = new HashSet<>();
                possible_r2exp.forEach(e -> r2.add(e.getNamedProperty().toString()));
                func_e1r1e2e3r2e1_e2r2e1e3r2e1.put(r1, r2);
            }
        }
        writeMap2File("PatternFunc_e1r1e2_e1r2e3_and_e1r2e2_e1r2e3.txt", func_e1r1e2e1r2e3_e1r2e2e1r2e3);
        writeMap2File("PatternFunc_e1r1e2_e3r2e1_and_e2r2e1_e3r2e1.txt", func_e1r1e2e3r2e1_e2r2e1e3r2e1);
        writeList2File("PatternFunc_e1r1e2_e1r1e3.txt", new ArrayList<>(func_e1r1e2_e1r1e3));
    }

}
