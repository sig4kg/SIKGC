package TBoxScanner;

import org.semanticweb.owlapi.model.*;

import java.io.*;
import java.util.*;

import uk.ac.manchester.cs.owl.owlapi.OWLObjectSomeValuesFromImpl;


public class PatternDLLite extends BasePattern implements IPattern {
    public final Map<OWLClassExpression, Set<OWLClassExpression>> _ERSups = new HashMap<>();
    public final Map<OWLClassExpression, Set<OWLClassExpression>> _ERInvsSups = new HashMap<>();
    public final Map<OWLClassExpression, Set<OWLClassExpression>> _CSups = new HashMap<>();
    public final Map<OWLClassExpression, Set<OWLClassExpression>> _D2Sups = new HashMap<>();
    public final Map<OWLClassExpression, Set<OWLClassExpression>> _D2DisjointC = new HashMap<>();
    public final Map<OWLClassExpression, Set<OWLClassExpression>> _D2DisjointER = new HashMap<OWLClassExpression, Set<OWLClassExpression>>();
    public final Map<OWLClassExpression, Set<OWLClassExpression>> _D2DisjointEInversR = new HashMap<OWLClassExpression, Set<OWLClassExpression>>();
    Map<OWLObjectPropertyExpression, Set<OWLObjectPropertyExpression>> Rsup2Rsubs = new HashMap<>();
    Map<OWLObjectPropertyExpression, Set<OWLObjectPropertyExpression>> Rsup2RIvsSubs = new HashMap<>();

    public void generatePattern() {
        cache_subsumptions();
        cache_disjointness();
        generateOPPattern();
        generateFuncPattern();
        generateTypePattern();
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

    private Set<OWLClassExpression> getDisjointClassExpressions(OWLClassExpression D) {
        Set<OWLClassExpression> disjointD = new HashSet<>();
        if (_D2Sups.containsKey(D)) {
            for (OWLClassExpression sup : _D2Sups.get(D)) {
                disjointD.add(sup.getComplementNNF());
            }
        }
        return disjointD;
    }

    private void cache_disjointness() {
        // cache all disjointness
        for (OWLClassExpression D : ont.getNestedClassExpressions()) {
            // getDisjointClasses() only get named classes
            Set<OWLClassExpression> Disjoints = getDisjointClassExpressions(D);
            for (OWLClassExpression dis : Disjoints) {
                if (dis.isNamed()) {
                    add2map(D, dis, _D2DisjointC);
                    continue;
                }
                ClassExpressionType cet = dis.getClassExpressionType();
                if (cet.equals(ClassExpressionType.OBJECT_COMPLEMENT_OF)) {
                    continue;
                }
                if (cet.equals(ClassExpressionType.OBJECT_SOME_VALUES_FROM)) {
                    OWLObjectPropertyExpression dis_some_p = ((OWLObjectSomeValuesFromImpl) dis).getProperty();
                    if (dis_some_p.isNamed()) {
                        add2map(D, dis, _D2DisjointER);
                    } else {
                        //ERInv
                        if (dis_some_p.isObjectPropertyExpression() && dis_some_p.getInverseProperty().isNamed()) {
                            add2map(D, dis, _D2DisjointEInversR);
                        }
                    }
                }
            }
        }
    }

    private void cache_subsumptions() {
        //cache all ER and ER- subsumptions
        Collection<OWLSubClassOfAxiom> axioms = this.ont.getAxioms(AxiomType.SUBCLASS_OF);
        for (OWLSubClassOfAxiom ax : axioms) {
            OWLClassExpression sub = ax.getSubClass();
            OWLClassExpression sup = ax.getSuperClass();
            add2map(sub, sup, _D2Sups);
            if (sub.isNamed()) {
                add2map(sub, sup, _CSups);
            }
            // do not cache \neg C
            ClassExpressionType cet = sub.getClassExpressionType();
            if (cet.equals(ClassExpressionType.OBJECT_COMPLEMENT_OF)) {
                continue;
            }
            if (cet.equals(ClassExpressionType.OBJECT_SOME_VALUES_FROM)) {
                OWLObjectPropertyExpression p = ((OWLObjectSomeValuesFromImpl) sub).getProperty();
                // ER
                if (p.isNamed()) {
                    add2map(sub, sup, _ERSups);
                } else {
                    //ERInv
                    if (p.isObjectPropertyExpression() && p.getInverseProperty().isNamed()) {
                        add2map(sub, sup, _ERInvsSups);
                    }
                }
            }
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

    private void cache_subsumptions2() {
        //cache all ER and ER- subsumptions
        Collection<OWLSubClassOfAxiom> axioms = this.ont.getAxioms(AxiomType.SUBCLASS_OF);
        for (OWLSubClassOfAxiom ax : axioms) {
            OWLClassExpression sub = ax.getSubClass();
            OWLClassExpression sup = ax.getSuperClass();
            add2map(sub, sup, _D2Sups);
            if (sub.isNamed()) {
                add2map(sub, sup, _CSups);
            }
            // do not cache \neg C
            ClassExpressionType cet = sub.getClassExpressionType();
            if (cet.equals(ClassExpressionType.OBJECT_COMPLEMENT_OF)) {
                continue;
            }
            if (cet.equals(ClassExpressionType.OBJECT_SOME_VALUES_FROM)) {
                OWLObjectPropertyExpression p = ((OWLObjectSomeValuesFromImpl) sub).getProperty();
                // ER
                if (p.isNamed()) {
                    add2map(sub, sup, _ERSups);
                } else {
                    //ERInv
                    if (p.isObjectPropertyExpression() && p.getInverseProperty().isNamed()) {
                        add2map(sub, sup, _ERInvsSups);
                    }
                }
            }
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

    public void generateOPPattern() {
        if (_ERSups.size() == 0) {
            cache_subsumptions();
            cache_disjointness();
        }
        // consider \some R subclassof D, D= C|\some Rx|\some Rx-
        // and \some R- subclassof D, D= C|\some Rx|\some Rx-
        Map<String, Set<String>> domain_Pattern = new HashMap<>();
        Map<String, Set<String>> e1r1e2_e1r2e3 = new HashMap<>();
        Map<String, Set<String>> e1r1e2_e3r2e1 = new HashMap<>();
        for (OWLClassExpression ER : _ERSups.keySet()) {
            String r = ((OWLObjectSomeValuesFromImpl) ER).getProperty().toString();
            Set<OWLClassExpression> sups = _ERSups.get(ER);
            for (OWLClassExpression D : sups) {
                if (_D2DisjointC.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_C = _D2DisjointC.get(D);
                    for (OWLClassExpression element : disjoint_C) {
                        add2map(r, element.toString(), domain_Pattern);
                    }
                }
                if (_D2DisjointER.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_ER2 = _D2DisjointER.get(D);
                    for (OWLClassExpression element : disjoint_ER2) {
                        add2map(r, ((OWLObjectSomeValuesFromImpl) element).getProperty().toString(), e1r1e2_e1r2e3);
                    }
                }
                if (_D2DisjointEInversR.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_ER2invers = _D2DisjointEInversR.get(D);
                    for (OWLClassExpression element : disjoint_ER2invers) {
                        add2map(r, ((OWLObjectSomeValuesFromImpl) element).getProperty().getNamedProperty().toString(), e1r1e2_e3r2e1);
                    }
                }

            }
        }
        Map<String, Set<String>> range_Pattern = new HashMap<>();
        Map<String, Set<String>> e2r1e1_e1r2e3 = new HashMap<>();
        Map<String, Set<String>> e2r1e1_e3r2e1 = new HashMap<>();
        for (OWLClassExpression ERInvs : _ERInvsSups.keySet()) {
            String r = ((OWLObjectSomeValuesFromImpl) ERInvs).getProperty().getNamedProperty().toString();
            Set<OWLClassExpression> sups = _ERInvsSups.get(ERInvs);
            for (OWLClassExpression D : sups) {
                if (_D2DisjointC.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_C = _D2DisjointC.get(D);
                    for (OWLClassExpression element : disjoint_C) {
                        add2map(r, element.toString(), range_Pattern);
                    }
                }
                if (_D2DisjointER.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_ER2 = _D2DisjointER.get(D);
                    for (OWLClassExpression element : disjoint_ER2) {
                        add2map(r, ((OWLObjectSomeValuesFromImpl) element).getProperty().toString(), e2r1e1_e1r2e3);
                    }
                }
                if (_D2DisjointEInversR.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_ER2invers = _D2DisjointEInversR.get(D);
                    for (OWLClassExpression element : disjoint_ER2invers) {
                        add2map(r, ((OWLObjectSomeValuesFromImpl) element).getProperty().getNamedProperty().toString(), e2r1e1_e3r2e1);
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
    }

    public void generateOPPattern2() {
        if (_ERSups.size() == 0) {
            cache_subsumptions();
        }
        // consider \some R subclassof D, D= C|\some Rx|\some Rx-
        // and \some R- subclassof D, D= C|\some Rx|\some Rx-
        Map<String, Set<String>> domain_Pattern = new HashMap<>();
        Map<String, Set<String>> e1r1e2_e1r2e3 = new HashMap<>();
        Map<String, Set<String>> e1r1e2_e3r2e1 = new HashMap<>();
        for (OWLClassExpression ER : _ERSups.keySet()) {
            String r = ((OWLObjectSomeValuesFromImpl) ER).getProperty().toString();
            Set<OWLClassExpression> sups = _ERSups.get(ER);

        }
        Map<String, Set<String>> range_Pattern = new HashMap<>();
        Map<String, Set<String>> e2r1e1_e1r2e3 = new HashMap<>();
        Map<String, Set<String>> e2r1e1_e3r2e1 = new HashMap<>();
        for (OWLClassExpression ERInvs : _ERInvsSups.keySet()) {
            String r = ((OWLObjectSomeValuesFromImpl) ERInvs).getProperty().getNamedProperty().toString();
            Set<OWLClassExpression> sups = _ERInvsSups.get(ERInvs);
            for (OWLClassExpression D : sups) {
                if (_D2DisjointC.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_C = _D2DisjointC.get(D);
                    for (OWLClassExpression element : disjoint_C) {
                        add2map(r, element.toString(), range_Pattern);
                    }
                }
                if (_D2DisjointER.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_ER2 = _D2DisjointER.get(D);
                    for (OWLClassExpression element : disjoint_ER2) {
                        add2map(r, ((OWLObjectSomeValuesFromImpl) element).getProperty().toString(), e2r1e1_e1r2e3);
                    }
                }
                if (_D2DisjointEInversR.containsKey(D)) {
                    Set<OWLClassExpression> disjoint_ER2invers = _D2DisjointEInversR.get(D);
                    for (OWLClassExpression element : disjoint_ER2invers) {
                        add2map(r, ((OWLObjectSomeValuesFromImpl) element).getProperty().getNamedProperty().toString(), e2r1e1_e3r2e1);
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
    }

    public void generateFuncPattern() {
        if (_ERSups.size() == 0) {
            cache_subsumptions();
            cache_disjointness();
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

    public void generateTypePattern() {
        if (_ERSups.size() == 0) {
            cache_subsumptions();
            cache_disjointness();
        }
        Map<String, Set<String>> C2Cs = new HashMap<>();
        Map<String, Set<String>> C2ERs = new HashMap<>();
        Map<String, Set<String>> C2ERInvs = new HashMap<>();
        for (OWLClassExpression cls : ont.getClassesInSignature()) {
            if (!cls.isNamed()) {
                continue;
            }
            String cls_str = cls.toString();
            if (_D2DisjointC.containsKey(cls)) {
                Set<OWLClassExpression> disjointC = _D2DisjointC.get(cls);
                for (OWLClassExpression disC : disjointC) {
                    add2map(cls_str, disC.toString(), C2Cs);
                }
            }
            if (_D2DisjointER.containsKey(cls)) {
                Set<OWLClassExpression> disjointER = _D2DisjointER.get(cls);
                for (OWLClassExpression D_ER : disjointER) {
                    String D_R_str = ((OWLObjectSomeValuesFromImpl) D_ER).getProperty().toString();
                    add2map(cls_str, D_R_str, C2ERs);
                }
            }
            if (_D2DisjointEInversR.containsKey(cls)) {
                Set<OWLClassExpression> disjointERInvs = _D2DisjointEInversR.get(cls);
                for (OWLClassExpression D_ERInvs : disjointERInvs) {
                    String D_R_str = ((OWLObjectSomeValuesFromImpl) D_ERInvs).getProperty().getNamedProperty().toString();
                    add2map(cls_str, D_R_str, C2ERInvs);
                }
            }
        }
        writeMap2File("PatternTypeDisjointC.txt", C2Cs);
        writeMap2File("PatternTypeDisjointER.txt", C2ERs);
        writeMap2File("PatternTypeDisjointERInvs.txt", C2ERInvs);
    }

}
