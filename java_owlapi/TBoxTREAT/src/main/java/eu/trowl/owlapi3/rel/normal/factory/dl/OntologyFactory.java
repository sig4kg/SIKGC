package eu.trowl.owlapi3.rel.normal.factory.dl;

import java.util.HashSet;
import java.util.Map.Entry;
import java.util.Set;

import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLLogicalAxiom;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLSubClassOfAxiom;

import eu.trowl.owlapi3.rel.normal.model.Basic;
import eu.trowl.owlapi3.rel.normal.model.Ontology;
import eu.trowl.owlapi3.rel.normal.model.Singleton;



/*** 
 * This class is the factory of the REL ontology.
 * It uses the builder to transform the input ontologies into an REL ontology
 * and prepares it for reasoning.
 * @author Yuan Ren
 * @version 2014-11-25:
 */
public class OntologyFactory{

	/*
	 * @version 2014-11-25:
	 * 1. added a new loadAxiom(...) method to load equivalent classes
	 */

	protected final OWLOntologyManager manager;
	protected final Set<OWLOntology> ontologies;
	protected OntologyBuilder builder;
	protected Ontology relOntology;

	public void createbuilder(){
		builder = new OntologyBuilder(ontologies,manager,relOntology);
	}

	public OntologyFactory(OWLOntology ontology,boolean bgp,boolean MetaOn,boolean disjoint)
	{
		this.manager = ontology.getOWLOntologyManager();
		this.ontologies = ontology.getImportsClosure();
		this.relOntology = new Ontology();
		this.relOntology.BGP = bgp;
		this.relOntology.MetaOn = MetaOn || (ontology.getClassesInSignature().size()<100);
		this.relOntology.disjoint = disjoint;
	}

	public Ontology createELOntology() {
		for(OWLOntology ontology:ontologies){
			for(OWLLogicalAxiom axiom:ontology.getLogicalAxioms())
				axiom.accept(builder);
		}
		builder.postBuildProcessing();
		return relOntology = builder.relOntology;
	}

	// duo-ontology classification code

	/**
	 * This method loads a temporary axiom for duo-ontology classification
	 * @param axiom: a temporary concept subsumption axiom
	 * @return An entry <lhs, rhs> where lhs \sub rhs is the approximation of axiom.
	 */
	public Entry<Basic, Basic> loadAxiom(OWLSubClassOfAxiom axiom) {
		// TODO Auto-generated method stub
		TemporalOntologyBuilder tempbuilder = new TemporalOntologyBuilder(ontologies, manager, relOntology, builder);
		return tempbuilder.loadTempAxiom(axiom);
	}

	/**
	 * This method loads a temporal equivalence axiom for duo-ontology classification
	 * @param c1 
	 * @param c2
	 * @return An entry<c2approx, c1approx> where the key and value are approximations of the input.
	 */
	public Entry<Basic, Basic> loadAxiom(OWLClassExpression c1, OWLClassExpression c2) {
		TemporalOntologyBuilder tempbuilder = new TemporalOntologyBuilder(ontologies, manager, relOntology, builder);
		tempbuilder.loadTempAxiom(manager.getOWLDataFactory().getOWLSubClassOfAxiom(c1, c2));
		return tempbuilder.loadTempAxiom(manager.getOWLDataFactory().getOWLSubClassOfAxiom(c2, c1));
	}

	public void clean() {
		builder.clean();
	}

	// NBox reasoning

	/**
	 * This method closes a concept cls with a set of individuals indis.
	 * @param cls
	 * @param indis
	 */
	public void close(OWLClassExpression cls, Set<OWLNamedIndividual> indis)
	{
		OWLDataFactory factory = manager.getOWLDataFactory();
		OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(cls, factory.getOWLObjectOneOf(indis));
		axiom.accept(builder);
		// NBox special
		HashSet<Singleton> individuals = new HashSet<Singleton>();
		for(OWLNamedIndividual indi:indis)
		{
			individuals.add((Singleton)this.relOntology.descriptions.get(relOntology.individualIDs.get(indi)));
		}
		//		for(Individual indi:this.elcontology.individuals.values())
		//		{
		//			if(indi.differentIndividuals.containsAll(individuals))
		//			{
		//				OWLClassAssertionAxiom indiaxiom = factory.getOWLClassAssertionAxiom(factory.getOWLObjectComplementOf(cls), factory.getOWLNamedIndividual(indi.uri));
		//				indiaxiom.accept(builder);
		//			}
		//		}
		for(Singleton indi:individuals)
		{
			for(Basic type:indi.subsumers)
			{
				if(type.complement != null)
				{
					type.complement.Ohat.add(indi.complement.entry);
				}
			}
			//			for(Individual diff:indi.differentIndividuals)
			//				diff.singleton.Ohat.add(indi.singleton.complement.entry);
		}
	}

	/**
	 * This method closes the property of subject with the objects specified.
	 * @param subject
	 * @param property
	 * @param objects
	 */
	public void close(OWLNamedIndividual subject, OWLObjectPropertyExpression property,
			Set<OWLNamedIndividual> objects) {
		// TODO Auto-generated method stub
		OWLDataFactory factory = manager.getOWLDataFactory();
		OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(factory.getOWLObjectSomeValuesFrom(property, factory.getOWLObjectOneOf(subject)), factory.getOWLObjectOneOf(objects));
		axiom.accept(builder);
	}

	/**
	 * This method closes the possible range of a property.
	 * @param property
	 * @param range
	 */
	public void close(OWLObjectPropertyExpression property,
			Set<OWLNamedIndividual> range) {
		// TODO Auto-generated method stub
		OWLDataFactory factory = manager.getOWLDataFactory();
		OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(factory.getOWLObjectSomeValuesFrom(property, factory.getOWLThing()), factory.getOWLObjectOneOf(range));
		axiom.accept(builder);

		// NBox special
		HashSet<Singleton> individuals = new HashSet<Singleton>();
		for(OWLNamedIndividual indi:range)
		{
			individuals.add((Singleton)this.relOntology.descriptions.get(relOntology.individualIDs.get(indi)));
		}
		//		for(Individual indi:this.elcontology.individuals.values())
		//		{
		//			if(indi.differentIndividuals.containsAll(individuals))
		//			{
		//				OWLClassAssertionAxiom indiaxiom = factory.getOWLClassAssertionAxiom(factory.getOWLObjectComplementOf(cls), factory.getOWLNamedIndividual(indi.uri));
		//				indiaxiom.accept(builder);
		//			}
		//		}
		for(Singleton indi:individuals)
		{
			for(Basic type:indi.subsumers)
			{
				if(type.complement != null)
				{
					type.complement.Ohat.addAll(indi.complement.Ohat);
				}
			}
			//			for(Individual diff:indi.differentIndividuals)
			//				diff.singleton.Ohat.addAll(indi.singleton.complement.Ohat);
		}
	}

	public void nBoxPostProcessing() {
		// TODO Auto-generated method stub
		builder.nBoxPostProcessing();
	}



}