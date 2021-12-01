import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLSubClassOfAxiom;

import java.util.*;


public class SubClassOfRedundant {
    public final Map<OWLClassExpression, Set<OWLSubClassOfAxiom>> _sub2Axioms = new HashMap<OWLClassExpression, Set<OWLSubClassOfAxiom>>();
    public Collection<OWLSubClassOfAxiom> _allAxioms = null;

    public SubClassOfRedundant(Collection<OWLSubClassOfAxiom> axioms) {
        _allAxioms = axioms;
        for (OWLSubClassOfAxiom ax : axioms) {
            OWLClassExpression sub = ax.getSubClass();
            if (_sub2Axioms.containsKey(sub)) {
                _sub2Axioms.get(sub).add(ax);
            } else {
                Set<OWLSubClassOfAxiom> tmpAxioms = new HashSet<OWLSubClassOfAxiom>();
                tmpAxioms.add(ax);
                _sub2Axioms.put(sub, tmpAxioms);
            }
        }
    }

    public List<OWLSubClassOfAxiom> findRedundants() {
        List<OWLSubClassOfAxiom> toDelete = new ArrayList<OWLSubClassOfAxiom>();
        for (OWLSubClassOfAxiom ax : _allAxioms) {
            OWLClassExpression sub = ax.getSubClass();
            OWLClassExpression sup = ax.getSuperClass();
            Set<OWLSubClassOfAxiom> checked = new HashSet<OWLSubClassOfAxiom>();
            Pair hasPath = existPath(sub, sup, checked);
            if (hasPath.indirect) {
                _sub2Axioms.get(sub).remove(ax);
                toDelete.add(ax);
            }
        }
        return toDelete;
    }

    public class Pair {
        public Boolean direct;
        public Boolean indirect;

        public Pair(Boolean first, Boolean second) {
            this.direct = first;
            this.indirect = second;
        }
    }

    private Pair existPath(OWLClassExpression sub, OWLClassExpression sup, Set<OWLSubClassOfAxiom> hasChecked) {
        if (!_sub2Axioms.containsKey(sub)) {
            return new Pair(Boolean.FALSE, Boolean.FALSE);
        }
        Set<OWLSubClassOfAxiom> axes = _sub2Axioms.get(sub);
        Boolean hasDirect = Boolean.FALSE;
        Boolean hasIndirect = Boolean.FALSE;
        OWLSubClassOfAxiom directAxiom = null;
        for (OWLSubClassOfAxiom ax : axes) {
            if (hasChecked.contains(ax)) {
                continue;
            }
            OWLClassExpression asup = ax.getSuperClass();
            if (asup == sup) {
                hasDirect = Boolean.TRUE;
                directAxiom = ax;
            }
            hasChecked.add(ax);
            Pair recursive = existPath(asup, sup, hasChecked);
            if (asup != sub && (recursive.indirect || recursive.direct)) {
                hasIndirect = Boolean.TRUE;
            }

        }
//        if (hasDirect && hasIndirect) {
//            axes.remove(directAxiom);
//        }
        Pair result = new Pair(hasDirect, hasIndirect);
        return result;
    }
}