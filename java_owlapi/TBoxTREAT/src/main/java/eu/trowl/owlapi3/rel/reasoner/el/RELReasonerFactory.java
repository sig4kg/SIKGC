package eu.trowl.owlapi3.rel.reasoner.el;

import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.reasoner.IllegalConfigurationException;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerConfiguration;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;

import eu.trowl.owlapi3.rel.reasoner.dl.RELReasoner;
import eu.trowl.owlapi3.rel.util.RELChangeBroadcastStrategy;


/***
 * REL reasoner factory for EL ontologies 
 * @author Yuan Ren
 * @version 2012-05-18
 */
public class RELReasonerFactory implements OWLReasonerFactory{

	public String getReasonerName() {
		// TODO Auto-generated method stub
		return "REL";
	}

	@Override
	public RELReasoner createReasoner(OWLOntology ontology) {
		// TODO Auto-generated method stub
		RELReasoner reasoner = new RELReasoner(ontology.getOWLOntologyManager(), ontology, bgp, MetaOn,disjoint);
		reasoner.manager.addOntologyChangeListener(reasoner, new RELChangeBroadcastStrategy());
		return reasoner;
	}

	@Override
	public RELReasoner createNonBufferingReasoner(OWLOntology arg0) {
		// TODO Auto-generated method stub
		RELReasoner reasoner = createReasoner(arg0);
		reasoner.bufferred = false;
		return reasoner;
	}

	@Override
	public OWLReasoner createNonBufferingReasoner(OWLOntology arg0,
			OWLReasonerConfiguration arg1) throws IllegalConfigurationException {
		// TODO Auto-generated method stub
		System.out.println("REL does not support OWLReasonerConfiguration yet.");
		return createReasoner(arg0);	
	}


	@Override
	public OWLReasoner createReasoner(OWLOntology arg0,
			OWLReasonerConfiguration arg1) throws IllegalConfigurationException {
		// TODO Auto-generated method stub
		System.out.println("REL does not support OWLReasonerConfiguration yet.");
		return createReasoner(arg0);	
	}

	private boolean bgp = false;
	public void setBGP(boolean bgp)
	{
		this.bgp = bgp;
	}
	private boolean MetaOn = false;
	public void setMetaOn(boolean MetaOn)
	{
		this.MetaOn = MetaOn;
	}
	private boolean disjoint = false;
	public void setDisjoint(boolean disjoint)
	{
		this.disjoint = disjoint;
	}

}
