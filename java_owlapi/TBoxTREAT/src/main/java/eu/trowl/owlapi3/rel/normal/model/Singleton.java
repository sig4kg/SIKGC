package eu.trowl.owlapi3.rel.normal.model;

import java.util.HashSet;

import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLNamedIndividual;


/***
 * REL internal representation of singleton concepts 
 * @author Yuan Ren
 * @version 2013-07-11
 */
public class Singleton extends Basic {
	/*
	 * @version 2013-07-11
	 * 1. always active=false and changed to true
	 * if ABox reasoning is required;
	 * @version 2012-05-18
	 */

	public HashSet<Singleton> differentIndividuals = new HashSet<Singleton>();

	public Singleton(){
		active = false;
	}

	public Singleton(OWLIndividual individual)
	{
		if(individual instanceof OWLNamedIndividual)
			uri = individual.asOWLNamedIndividual().getIRI();
		active = false;
	}


	@Override
	public String toString() {
		// TODO Auto-generated method stub
		if(uri == null)
			return "ApproxI"+id;
		else
			return uri.toString();
	}
}
