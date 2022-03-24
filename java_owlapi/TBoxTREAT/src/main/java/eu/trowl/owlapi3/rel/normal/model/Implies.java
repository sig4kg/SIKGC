package eu.trowl.owlapi3.rel.normal.model;

import java.util.HashSet;



/***
 * This class is the queue entries of form B1,B2,...,Bn -> C.
 * When process A with B1,B2,...,Bn -> C, it means that: 
 * If A is a subconcept of B1, B2, ..., Bn, then A is a subconcept of C.
 * When n=0, it indicates that A is a subconcept of C.
 * @author Yuan Ren
 * @version 2012-05-18
 */
public class Implies implements QueueEntry {

	public HashSet<Basic> lhs = new HashSet<Basic>();
	public Basic rhs = null;
	public int id;
	
	@Override
	public int hashCode() {
		return id;
	}
}
