package eu.trowl.owlapi3.rel.normal.model;



/*** 
 * @author Yuan Ren
 * @version 2012-05-18
 */
public class CardinalityEntry {
	public int n;
	public Atomic basen;
	
	public CardinalityEntry(Atomic base, int n) {
		super();
		this.basen = base;
		this.n = n;
	}

}
