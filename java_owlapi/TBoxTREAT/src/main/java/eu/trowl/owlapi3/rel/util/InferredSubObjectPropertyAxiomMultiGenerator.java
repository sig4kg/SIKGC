package eu.trowl.owlapi3.rel.util;
import static org.semanticweb.owlapi.util.OWLAPIPreconditions.checkNotNull;
import java.util.Set;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;
import org.semanticweb.owlapi.model.OWLSubObjectPropertyOfAxiom;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.search.EntitySearcher;
import org.semanticweb.owlapi.util.InferredObjectPropertyAxiomGenerator;

/**
 * @author Matthew Horridge, The University Of Manchester, Bio-Health Informatics Group
 * @since 2.1.0
 */
public class InferredSubObjectPropertyAxiomMultiGenerator
        extends InferredObjectPropertyAxiomGenerator<OWLSubObjectPropertyOfAxiom> {

    @Override
    protected void addAxioms(OWLObjectProperty entity, OWLReasoner reasoner,
                          OWLDataFactory dataFactory, Set<OWLSubObjectPropertyOfAxiom> result,
                          Set<OWLObjectPropertyExpression> nonSimpleProperties) {
        checkNotNull(dataFactory, "dataFactory cannot be null");
        checkNotNull(reasoner, "reasoner cannot be null");
        checkNotNull(result, "result cannot be null");
        checkNotNull(entity, "entity cannot be null");
        reasoner.getSuperObjectProperties(entity, false).entities().forEach(
                p -> addIfSimple(p, entity, dataFactory, result, nonSimpleProperties, reasoner));
    }

    protected void addIfSimple(OWLObjectPropertyExpression p, OWLObjectProperty entity,
                               OWLDataFactory dataFactory, Set<OWLSubObjectPropertyOfAxiom> result,
                               Set<OWLObjectPropertyExpression> nonSimpleProperties, OWLReasoner reasoner) {
        boolean nonSimple = false;
        boolean inverse = false;
        if (!simple(nonSimpleProperties, entity)) {
            nonSimple = true;
        }
        if (p.isAnonymous()
                && EntitySearcher.isTransitive(p.getInverseProperty(), reasoner.getRootOntology())) {
            inverse = true;
        }
        if (!(nonSimple && inverse)) {
            // having both non simple properties and inverses in an subproperty axiom may cause
            // exceptions later on
            result.add(dataFactory.getOWLSubObjectPropertyOfAxiom(entity, p));
        }
    }

    @Override
    public String getLabel() {
        return "Sub object properties";
    }
}
