package eu.trowl.owlapi3.rel.normal.model;

/***
 * REL internal representation of existential restriction 
 * @author Yuan Ren
 * @version 2013-07-11
 */
public class Some extends Description implements QueueEntry {
/*
 * @version 2013-07-11
 * 1. implements QueueEntry so that can be used
 * as ExistRestriction entries
 * @version 2012-05-18
 */
	public Role role;
	public Description concept;
	
	public Some()
	{
		
	}
	
	public Some(Role role, Description concept){
		this.role = role;
		this.concept = concept;
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
