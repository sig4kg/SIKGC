package eu.trowl.owlapi3.rel.normal.model;

import org.semanticweb.owlapi.model.OWLClass;


/***
 * REL interanl representation of Atomic concept. 
 * @author Yuan Ren
 * @version 2012-08-19:
 */
public class Atomic extends Basic{
/*
 * @version 2012-08-19:
 * 1. add instances for OWL-BGP use
 * @version 2012-05-18
 */
	

	@Override
	public String toString() {
		// TODO Auto-generated method stub
		if(uri == null)
			return "ApproxC"+id;
		else
		return uri.toString();
	}
	
	public Atomic()
	{
	}
	
	public Atomic(OWLClass concept)
	{
		uri = concept.getIRI();
	}
	
	
}
