package ReasonerUtils;

import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.reasoner.OWLReasoner;

public interface IReasonerUtil{
    OWLOntology classify(OWLOntology ontology, OWLOntologyManager man);
    OWLOntology realize(OWLOntology ontology, OWLOntologyManager man);
}
