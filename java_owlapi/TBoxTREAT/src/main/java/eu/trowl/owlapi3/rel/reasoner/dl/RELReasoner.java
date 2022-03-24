package eu.trowl.owlapi3.rel.reasoner.dl;

import java.util.HashSet;
import java.util.Map.Entry;
import java.util.Set;

import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLAnnotation;
import org.semanticweb.owlapi.model.OWLAnnotationProperty;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLLiteral;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLSubClassOfAxiom;
import org.semanticweb.owlapi.reasoner.FreshEntitiesException;
import org.semanticweb.owlapi.reasoner.InconsistentOntologyException;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.ReasonerInterruptedException;
import org.semanticweb.owlapi.reasoner.TimeOutException;
import org.semanticweb.owlapi.reasoner.impl.OWLClassNode;
import org.semanticweb.owlapi.reasoner.impl.OWLClassNodeSet;

import eu.trowl.owlapi3.rel.normal.classify.dl.CombinedClassifier;
import eu.trowl.owlapi3.rel.normal.factory.dl.OntologyFactory;
import eu.trowl.owlapi3.rel.normal.model.Atomic;
import eu.trowl.owlapi3.rel.normal.model.Basic;
import eu.trowl.owlapi3.rel.normal.model.Description;
import eu.trowl.owlapi3.rel.normal.model.RoleConcept;

/***
 * REL reasoner for DL ontologies. 
 * @author Yuan Ren
 * @version 2013-07-17:
 */
public class RELReasoner extends eu.trowl.owlapi3.rel.reasoner.el.RELReasoner{
	/*
	 * @version 2013-07-17:
	 * 1. revise close() to call precomputeInferences() instead of classify();
	 * 2. add pre-computation to getDisjointClasses(0 and close();
	 * @version 2013-01-28:
	 * 1. included OWL-DBC related methods;
	 * 2. updated OWL-DBC related methods to change Individual to Singleton;
	 * 3. include TrOWL-BGP related methods;
	 * 4. update as an extension of EL reasoner;
	 * @version 2012-08-19
	 * @version 2012-05-18
	 */
	/**
	 * Constructor
	 * @param manager: input ontology manager
	 * @param ontology: input ontology
	 * @param bgp: whether the ontology will be used for BGP query answering
	 * @param MetaOn: whether the ontology contains meta-modelling
	 * @param disjoint: whether the ontology wants to initilaise disjointness between sets 
	 */
	public RELReasoner(OWLOntologyManager manager, OWLOntology ontology, boolean bgp, boolean MetaOn, boolean disjoint) {
		super(manager, ontology, bgp, MetaOn, disjoint);
	}

	public void loadOntology()
	{
		OWLAnnotationProperty annotation = factory.getOWLAnnotationProperty(IRI.create("http://TrOWL.eu/REL#NBox"));
		Set<OWLClassExpression> closedConcepts = new HashSet<OWLClassExpression>();
		Set<OWLObjectPropertyExpression> closedRoles = new HashSet<OWLObjectPropertyExpression>();

		// close concepts
		for(OWLClass cls:ontology.getClassesInSignature())
		{
			for(OWLAnnotation anno: ontology.getAnnotations(annotation))
			{
				if (anno.getValue() instanceof OWLLiteral) {
					{
						OWLLiteral val = (OWLLiteral) anno.getValue();
						if(val.getLiteral().equals("close"))
							closedConcepts.add(cls);
					}
				}
			}
		}

		// close roles
		for(OWLObjectProperty cls:ontology.getObjectPropertiesInSignature())
		{
			for(OWLAnnotation anno:ontology.getAnnotations(annotation))
			{
				if (anno.getValue() instanceof OWLLiteral) {
					{
						OWLLiteral val = (OWLLiteral) anno.getValue();
						if(val.getLiteral().equals("close"))
							closedRoles.add(cls);
					}
				}
			}
		}



		elcfactory = new OntologyFactory(ontology,bgp,MetaOn,disjointness);
		elcfactory.createbuilder();
		this.relOntology = elcfactory.createELOntology();	
		if(closedConcepts.size()>0 || closedRoles.size()>0)
			close(closedConcepts, closedRoles);
	}

	@Override
	public NodeSet<OWLClass> getDisjointClasses(OWLClassExpression concept)
			throws ReasonerInterruptedException, TimeOutException,
			FreshEntitiesException, InconsistentOntologyException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.CLASS_HIERARCHY);
		OWLClassNodeSet	disjoints = new OWLClassNodeSet();
		Description desc = getDescription(concept);
		Atomic bot = (Atomic) relOntology.descriptions.get(0);

		// If concept X has not already been approximated as a named concept in REL
		// Introduce a name for this concept with an extra axiom tempC \sub X
		// Then applyg duo-ontology classification and look for disjoint classes of tempC.
		boolean duo = false;
		if(desc == null || !(desc instanceof Atomic))
		{
			// apply duo-ontology classification approach
			duo = true;
			// add an additional axiom tempC \sub X
			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempC"));
			OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(tempclass, concept);
			Entry<Basic, Basic> entry = elcfactory.loadAxiom(axiom);

			// incrementally classify the new ontology
			CombinedClassifier classifier = new CombinedClassifier();
			classifier.ontology = relOntology;
			classifier.completion_duo(relOntology.aBox_Classified);
			desc = (Atomic) entry.getKey();
		}		
		Atomic atom = (Atomic)desc;
		HashSet<Basic> subsumers = new HashSet<Basic>();
		if(atom.equivalence.contains(bot))
			return satisfiableClasses;
		else
		{
			for(Basic sub:atom.subsumers)
			{
				if(sub.complement.original && !subsumers.contains(sub.complement))
					subsumers.addAll(sub.complement.equivalence);
			}					
			for(Basic sub:atom.tempSubsumers)
			{
				if(sub.complement.original && !subsumers.contains(sub.complement))
					subsumers.addAll(sub.complement.equivalence);
			}					
		}

		while(subsumers.size()>0)
		{
			Basic sub = subsumers.iterator().next();
			subsumers.removeAll(sub.equivalence);
			OWLClassNode ancestor = new OWLClassNode();
			for(Basic eq:sub.equivalence)
				if(eq instanceof Atomic && ((Atomic)eq).original)
					ancestor.add(factory.getOWLClass(((Atomic)eq).uri));							
			if(ancestor.getSize() > 0)
				disjoints.addNode(ancestor);
		}

		// clean the classifier, factory, ontology, etc for duo-ontology classification.
		if(duo)
			elcfactory.clean();

		return disjoints;
	}

	/**
	 * This method performs NBox reasoning with closed class and property expressions.
	 * @param classes: the class expressions to be closed.
	 * @param properties: the object property expressions to be closed.
	 */
	public void close(Set<OWLClassExpression> classes, Set<OWLObjectPropertyExpression> properties)
	{
		// first perform a full materialisation
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.aBox_Classified)
			precomputeInferences(InferenceType.CLASS_ASSERTIONS);
		relOntology.NOnto = true;

		// then use the derived instances to close the concepts and roles
		for(OWLClassExpression cls:classes)
		{
			Set<OWLNamedIndividual> indis = getIndividuals(cls).getFlattened();
			(elcfactory).close(cls, indis);
		}

		// note that close a role will also close its inverse
		HashSet<OWLObjectPropertyExpression> invers = new HashSet<OWLObjectPropertyExpression>();
		for(OWLObjectPropertyExpression role:properties)
			invers.add(role.getInverseProperty());
		properties.addAll(invers);

		for(OWLObjectPropertyExpression property:properties)
		{
			// domains are closed as the ranges of invers properties;
			Set<OWLNamedIndividual> range = new HashSet<OWLNamedIndividual>();
			for(OWLNamedIndividual indi:ontology.getIndividualsInSignature())
			{
				Set<OWLNamedIndividual> indis = getObjectPropertyValues(indi, property).getFlattened();
				(elcfactory).close(indi, property, indis);
				range.addAll(indis);
			}
			(elcfactory).close(property, range);
		}

		(elcfactory).nBoxPostProcessing();

		// at last perform another round of materialisation
		relOntology.tBox_Classified = false;
		relOntology.aBox_Classified = false;
		precomputeInferences();
	}

	public HashSet<OWLClass> gerPredecessors(OWLClass cls) {
		// TODO Auto-generated method stub
		HashSet<OWLClass> clss = new HashSet<OWLClass>();
		Atomic atomic = (Atomic) getDescription(cls);
		for(RoleConcept rc:atomic.predecessors)
		{
			clss.add(factory.getOWLClass(rc.concept.uri));
		}
		return clss;
	}


}
