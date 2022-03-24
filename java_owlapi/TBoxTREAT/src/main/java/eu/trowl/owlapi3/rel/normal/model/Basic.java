package eu.trowl.owlapi3.rel.normal.model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import org.semanticweb.owlapi.model.IRI;


/***
 * REL internal representation of atomic concepts and singleton nominal concepts. 
 * @author Yuan Ren
 * @version 2013-10-09
 */
public class Basic extends Description {
	/*
	 * @version 2013-10-09:
	 * 1. add originalSubsumee to maintain original sub-classes;
	 * @version 2013-09-18:
	 * 1. add onlyLink to confirm ONLY approximation;
	 * @version 2013-07-11
	 * 1. add activition flag so that concepts are activatable for reasoning;
	 * 2. add reverseReach so that unsatisfiablility can be reverse-propagated;
	 * @version 2013-01-31
	 * 1. add method for duo-ontology classification
	 * @version 2012-05-18
	 */

	public IRI uri = null;

	// The queue entry ->this.
	public Implies entry;
	public Basic complement = null;

	// The minimal cardinality value of a concept.
	// If a concept is satisfiable, its minCardin is by default 1.
	// If a concept is a CardinAtomic, its minCardin can be > 1.
	// If a concept is unsatisfiable, this variable is not applicable.
	public int minCardin = 1;
	public HashSet<Basic> subsumers = new HashSet<Basic>();
	public HashSet<Basic> tempSubsumers = new HashSet<Basic>();
	public HashSet<Basic> equivalence = new HashSet<Basic>();

	// The set of concepts that should be inherited.
	public HashSet<Description> queue = new HashSet<Description>();

	// If A \sub \some R.B, then <R,A> is a predecessor of B.
	public HashSet<RoleConcept> predecessors = new HashSet<RoleConcept>();
	public HashSet<RoleConcept> tempPredecessors = new HashSet<RoleConcept>();

	// Maintains the occurrence of minCardinality restriction with the current concept as filler.
	public CardinalityEntry[] cardins = null;
	public CardinalityEntry[] tempcardins = null;

	// Whether the concept is an original one from the input ontologies.
	public boolean original = true;

	// Whenther the concept is activated in reasoning
	public boolean active = true;

	// Set of concepts from which the current concept is reachable.
	public HashSet<Basic> reachableBy = new HashSet<Basic>();

	// If the current concept is the approx(\only R.C)
	// onlyLink will point to \some approx(R).approx(\neg C)
	public Some onlyLink = null;

	public HashSet<Basic> originalSubsumee = null;

	// The following two are used for cardinality test.
	// See Role for more details.
	// In <\some R.B, list>, list contains all subconcepts Bi of B s.t. this \sub \some R.Bi can be derived.
	public HashMap<Some, ArrayList<Basic>> fillerSubConcepts = new HashMap<Some, ArrayList<Basic>>();
	// In <\some R.B, n>, n is the total number of minimal cardinality of the Bis in the above list.
	public HashMap<Some, Integer> totalCardinality = new HashMap<Some, Integer>();

	public void addPredecessor(Role s, Basic a) {
		// TODO Auto-generated method stub
		RoleConcept rc = new RoleConcept(s,a);
		predecessors.add(rc);
	}

	public void addTempPredecessor(Role s, Basic a) {
		// TODO Auto-generated method stub
		RoleConcept rc = new RoleConcept(s,a);
		tempPredecessors.add(rc);
	}

	public Singleton asSingleton(){
		return (Singleton)this;
	}

}
