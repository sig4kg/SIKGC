package eu.trowl.owlapi3.rel.normal.model;

import java.util.HashSet;

/***
 * REL internal representation of conjunction. 
 * @author Yuan Ren
 * @version 2012-05-18
 */
public class And extends Description {

	public HashSet<Description> operands = new HashSet<Description>();
	
	public And()
	{
		
	}
	public And(HashSet<Description> intersection)
	{
		operands = intersection;
	}
	@Override
	public boolean equals(Object obj) {
		// TODO Auto-generated method stub
		return super.equals(obj);
	}
	@Override
	public int hashCode() {
		// TODO Auto-generated method stub
		return super.hashCode();
	}
}
