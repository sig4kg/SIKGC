package eu.trowl.owlapi3.rel.normal.model;

import java.util.HashSet;

/***
 * REL internal representation of concept expression.
 * @author Yuan Ren
 * @version 2012-05-18
 */
public class Description {
	public int id = -1;

	// The initial set of queue entries that have to be processed.
	// When a concept C inherits concept D, C needs to process all D.Ohat entries.
	public HashSet<QueueEntry> Ohat = new HashSet<QueueEntry>();
	public HashSet<QueueEntry> tempOhat = new HashSet<QueueEntry>();

	@Override
	public int hashCode() {
		return id;
	}

}
