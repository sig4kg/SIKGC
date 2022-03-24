package eu.trowl.owlapi3.rel.normal.model;



/** 
 * @author Yuan Ren
 * @version 2012-05-18
 */
public class RoleConcept {
	
	public RoleConcept()
	{
		this(null,null);
	}

	public RoleConcept(Role role, Basic concept) {
		super();
		this.role = role;
		this.concept = concept;
	}
	public Role role;
	public Basic concept;
	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + concept.id;
		result = prime * result + role.id;
		return result;
	}
}
