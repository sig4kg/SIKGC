package eu.trowl.owlapi3.rel.reasoner.dl;

import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.reasoner.IllegalConfigurationException;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerConfiguration;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;

import eu.trowl.owlapi3.rel.util.RELChangeBroadcastStrategy;


/***
 * REL reasoner factory for DL ontologies. 
 * @author Yuan Ren
 * @version 2013-04-07
 */
public class RELReasonerFactory implements OWLReasonerFactory{
	/*
	 * @version 2013-04-07
	 * 1. update to support (non-)buffered reasoner
	 * @version 2013-01-28
	 * 1. update as extension of EL reasoner factory
	 * @version 2012-05-18
	 */
	public String getReasonerName() {
		// TODO Auto-generated method stub
		return "REL";
	}

	@Override
	public RELReasoner createReasoner(OWLOntology ontology) {
		// TODO Auto-generated method stub
		RELReasoner reasoner = new RELReasoner(ontology.getOWLOntologyManager(), ontology, bgp, MetaOn, disjoint);
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
		RELReasoner reasoner = createReasoner(arg0);
		reasoner.bufferred = false;
		//		System.out.println("REL does not support OWLReasonerConfiguration yet.");
		return reasoner;	
	}


	@Override
	public OWLReasoner createReasoner(OWLOntology arg0,
			OWLReasonerConfiguration arg1) throws IllegalConfigurationException {
		// TODO Auto-generated method stub
		RELReasoner reasoner = createReasoner(arg0);
		reasoner.bufferred = true;
		//		System.out.println("REL does not support OWLReasonerConfiguration yet.");
		return reasoner;	
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
