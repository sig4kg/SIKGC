package eu.trowl.owlapi3.rel.normal.factory.dl;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map.Entry;
import java.util.Set;

import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLSubClassOfAxiom;

import eu.trowl.owlapi3.rel.normal.model.Atomic;
import eu.trowl.owlapi3.rel.normal.model.Basic;
import eu.trowl.owlapi3.rel.normal.model.CardinAtomic;
import eu.trowl.owlapi3.rel.normal.model.CardinalityEntry;
import eu.trowl.owlapi3.rel.normal.model.Description;
import eu.trowl.owlapi3.rel.normal.model.Implies;
import eu.trowl.owlapi3.rel.normal.model.Ontology;
import eu.trowl.owlapi3.rel.normal.model.Role;
import eu.trowl.owlapi3.rel.normal.model.Some;
import eu.trowl.owlapi3.rel.util.RELReasonerConfiguration;


/***
 * This class prepares a permanent ontology with temporary axioms for duo-ontology classification. 
 * @author Yuan Ren
 * @version 2014-11-24
 */
public class TemporalOntologyBuilder extends OntologyBuilder {

	/*
	 * @version 2014-11-24
	 * 1. updated the OrderingCardinality() method with the updateNewCards(...) to update
	 * new cardinality atomics whose basic concepts occurred in the original ontology.
	 * @version 2013-07-11
	 * 1. update initialise(Basic, Role, Basic) to replace ERestriction with Some;
	 * @version 2013-01-31
	 * 1. updated for TrOWL v1.1 release
	 * @version 2012-05-18
	 * @param ontologies
	 * @param manager
	 * @param ELContology
	 * @param builder
	 */

	/**
	 * This method constructs the temporal ontology builder.
	 * @param ontologies: the input ontologies.
	 * @param manager: the manager of the input.
	 * @param RELOntology: the approximated ontology. 
	 * @param builder: the permanent builder.
	 */
	public TemporalOntologyBuilder(Set<OWLOntology> ontologies, OWLOntologyManager manager, Ontology RELOntology, OntologyBuilder builder) {

		factory = manager.getOWLDataFactory();
		relOntology = RELOntology;

		classIDs = relOntology.classIDs;
		propertyIDs = relOntology.roleIDs;
		individualIDs = relOntology.individualIDs;
		descriptions = relOntology.descriptions;
		roles = relOntology.roles;
		originalNamedConcepts = relOntology.originalNamedConcepts;


		basicID = builder.basicID;
		nonBasicID = builder.nonBasicID;
		roleID = builder.roleID;
		implyID = builder.implyID;
		classIDs = builder.classIDs;
		propertyIDs = builder.propertyIDs;
		individualIDs = builder.individualIDs;
		descriptions = builder.descriptions;
		roles = builder.roles;

		for(Entry<Atomic, HashMap<Integer, Atomic>> cardinentry:builder.CardinalityTable.entrySet())
		{
			HashMap<Integer, Atomic> cardins = new HashMap<Integer, Atomic>();
			for(Entry<Integer, Atomic> entry:cardinentry.getValue().entrySet())
				cardins.put(entry.getKey(), entry.getValue());
			this.CardinalityTable.put(cardinentry.getKey(), cardins);
		}
		RELOntology.basicConceptNum = basicID;
		bot = (Atomic) descriptions.get(0);
		top = (Atomic) descriptions.get(1);
	}

	/**
	 * This method load a temporary concept subsumption axiom for duo-ontology classification
	 * @param axiom: a temporary concept subsumption axiom
	 * @return An entry <lhs, rhs> where lhs \sub rhs is the approximation of axiom.
	 */
	public Entry<Basic, Basic> loadTempAxiom(OWLSubClassOfAxiom axiom) {
		// TODO Auto-generated method stub

		OWLClass thing = factory.getOWLThing();
		OWLClass nothing = factory.getOWLNothing();
		OWLClass namedindividual = factory.getOWLClass(IRI.create("http://www.w3.org/2002/07/owl#NamedIndividual"));

		for(OWLClass concept:axiom.getClassesInSignature())
		{
			if(concept.equals(thing) || concept.equals(nothing) || concept.equals(namedindividual) || relOntology.classIDs.get(concept)!=null)
				continue;
			Atomic newconcept = new Atomic(concept);
			newconcept.id = basicID++;
			newconcept.original = false;
			classIDs.put(concept, newconcept.id);
			descriptions.put(newconcept.id, newconcept);
			imply(newconcept);
			newconcept.equivalence.add(newconcept);

			// negation for all the atomics
			if(!relOntology.largeT)
			{
				Atomic nA = new Atomic();
				nA.id = basicID++;
				nA.original = false;
				classIDs.put(factory.getOWLObjectComplementOf(concept), nA.id);
				descriptions.put(nA.id, nA);
				imply(nA);
				nA.equivalence.add(nA);
				newconcept.complement = nA;
				nA.complement = newconcept;
			}
		}

		OWLClassExpression lhs = axiom.getSubClass();
		OWLClassExpression rhs = axiom.getSuperClass();
		Description NC = approx(getNNF(lhs));
		Description ND = approx(getNNF(rhs));
		normalise(NC,ND);

		HashMap<Basic, Basic> newentry = new HashMap<Basic,Basic>();
		Basic LHS = bot, RHS = top;
		if(NC instanceof Basic)
			LHS = (Basic)NC;
		if(ND instanceof Basic)
			RHS = (Basic)ND;
		newentry.put(LHS, RHS);

		postBuildProcessing();

		return newentry.entrySet().iterator().next();
	}

	// The following initialisation methods are almost the same as the ones in OntologyBuilder.
	// The only difference is that they initialise with the tempOhat instead of Ohat.
	protected void initialise(Basic lhs, Basic rhs)
	{
		lhs.tempOhat.add(rhs.entry);
	}

	protected void initialise(HashSet<Basic> lhs, Basic rhs)
	{
		if(lhs.size() == 1)
		{
			Implies imply = rhs.entry;
			lhs.iterator().next().tempOhat.add(imply);
		}
		else
		{
			for (Basic desc : lhs)
			{
				Implies implies = new Implies();
				implies.rhs = rhs;
				for (Basic company : lhs)
				{
					if(!company.equals(desc))
						implies.lhs.add(company);
				}					
				implies.id = implyID++;
				desc.tempOhat.add(implies);
			}
		}
	}

	protected void initialise(Basic A, Role role, Basic B)
	{
		Some exists = role.somes.get(B);
		if(exists == null)
		{
			exists = new Some(role,B);
			exists.id = nonBasicID--;
			role.somes.put(B, exists);
		}
		A.tempOhat.add(exists);
	}

	protected void initialise(Role role, Basic A, Basic B)
	{
		Some some = relOntology.roles.get(role.id).somes.get(A);
		if(some == null)
		{
			some = new Some(role, A);
			some.id = nonBasicID;
			nonBasicID--;
			descriptions.put(some.id, some);
			relOntology.roles.get(role.id).somes.put(A, some);			
		}
		some.tempOhat.add(B.entry);
		if(!relOntology.largeT && !relOntology.largeA)
		{
			if(A instanceof CardinAtomic && ((CardinAtomic)A).minCardin <= RELReasonerConfiguration.cardinThreshold)
				role.cardiAtomics.add((CardinAtomic) A);
		}
	}
	public void postBuildProcessing() {
		// TODO Auto-generated method stub
		// Here we need to update the cardinalities as the temporary axiom may contain one.

		for(Entry<Atomic, HashMap<Integer, Atomic>> entry:CardinalityTable.entrySet())
		{
			Atomic filler = entry.getKey();
			HashMap<Integer, Atomic> cardins = entry.getValue();
			CardinalityEntry[] number = new CardinalityEntry[cardins.size()];
			int size = 0;
			for(int n:cardins.keySet())
			{
				int i,j;
				for(i = 0;i < size;i++)
				{
					if(number[i].n < n)
						break;
				}
				for(j = size;j>i;j--)
				{
					number[j] = number[j-1];
				}
				CardinalityEntry newentry = new CardinalityEntry(cardins.get(n), n);
				number[i] = newentry;
				size++;
				updateNewCardinalities(filler, newentry);
			}
			filler.tempcardins = number;
			for(int i = 0;i<size-1;i++)
			{
				normalise(number[i].basen, number[i+1].basen);
			}
		}

		relOntology.basicConceptNum = basicID;
		relOntology.roleNum = roleID;
	}

	private void updateNewCardinalities(Basic filler, CardinalityEntry newentry){
		boolean update = false;
		if(filler.cardins == null)
			update = true;
		else
		{
			boolean found = false;
			for(CardinalityEntry oldentry:filler.cardins)
			{
				if(oldentry.n == newentry.n)
				{
					found = true;
					break;
				}
			}
			update = !found;
		}
		if (update)
			for(Basic superconcept: filler.subsumers)
			{
				if(superconcept.cardins != null)
				{
					int first = 0;
					while(superconcept.cardins[first].n > newentry.n)
						first ++;
					if(first < superconcept.cardins.length)
						normalise(newentry.basen,superconcept.cardins[first].basen);
				}
			}
	}
}
