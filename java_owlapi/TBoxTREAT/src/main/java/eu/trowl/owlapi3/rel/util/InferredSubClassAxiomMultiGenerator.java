package eu.trowl.owlapi3.rel.util;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLSubClassOfAxiom;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.util.InferredClassAxiomGenerator;
import java.util.Set;

import static org.semanticweb.owlapi.util.OWLAPIPreconditions.checkNotNull;
/**
 * @author Sylvia Wang, 20220413
 */
public class InferredSubClassAxiomMultiGenerator extends
        InferredClassAxiomGenerator<OWLSubClassOfAxiom> {

    @Override
    protected void addAxioms(OWLClass entity, OWLReasoner reasoner, OWLDataFactory dataFactory,
                             Set<OWLSubClassOfAxiom> result) {
        checkNotNull(dataFactory, "dataFactory cannot be null");
        checkNotNull(reasoner, "reasoner cannot be null");
        checkNotNull(result, "result cannot be null");
        checkNotNull(entity, "entity cannot be null");
        if (reasoner.isSatisfiable(entity)) {
            // set to false, so indirect results are included
            reasoner.getSuperClasses(entity, false).entities()
                    .forEach(sup -> result.add(dataFactory.getOWLSubClassOfAxiom(entity, sup)));
        } else {
            result.add(dataFactory.getOWLSubClassOfAxiom(entity, dataFactory.getOWLNothing()));
        }
    }

    @Override
    public String getLabel() {
        return "Subclasses";
    }
}
