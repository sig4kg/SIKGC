package eu.trowl.owlapi3.rel.normal.model;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLObjectProperty;

import eu.trowl.owlapi3.rel.util.RELReasonerConfiguration;


/***
 * REL internal representation of a role.
 * @author Yuan Ren
 * @version 2015-01-16: 
 */
public class Role {
	/*
	 * @version 2015-01-16:
	 * 1. add null detection for target in the cardinTestSimple methods;
	 * @version 2013-07-27: 
	 * 1. add support to cardinality test;
	 * @version 2013-01-31: 
	 * 1. add method for duo-ontology classification
	 * @version 2012-08-19: 
	 * 1. add subjects for OWL-BGP use
	 * @version 2012-05-18
	 */
	public int id = -1;
	public IRI uri = null;

	// Whether the role is original in the input ontologies
	public boolean original = true;

	// A role is related if it or its super role appears on the LHS of some original axiom
	// Check the CIKM TMS paper for more details.
	public boolean related = false;

	// This maintains the subsumptions of the form A \sub \some r.B
	// The above axiom will have r.Relations.get(A).contains(B) 
	public HashMap<Basic, HashSet<Basic>> Relations = new HashMap<Basic, HashSet<Basic>>();
	public HashMap<Basic, HashSet<Basic>> tempRelations = new HashMap<Basic, HashSet<Basic>>();

	// This maintains the number of different objects for a certain subject
	// Assuming there are A \sub \some r.B1, A  \sub \some r.B2, ....
	// This maintains the number of different instances of B1, B2, ... for each instance of A.
	// This is not an accurate measure but an upper bound of the minimal number.
	// It is needed to trigger cardinality test.
	private HashMap<Basic, Integer> RelationSize = new HashMap<Basic, Integer>();

	//	public HashSet<Basic> Self = new HashSet<Basic>();

	public HashSet<Role> subsumers = new HashSet<Role>();
	public HashSet<Role> equivalence = new HashSet<Role>();
	public HashSet<Role> subroles = new HashSet<Role>();

	public Role inverse = null;
	public boolean functional = false;
	public boolean reflexive = false;
	//	public boolean transitive = false;

	// This maintains axiom of form r o s \sub t
	// The above axiom will have r.RightComposition.get(s).contains(t)
	public HashMap<Role, HashSet<Role>> RightComposition = new HashMap<Role, HashSet<Role>>();

	// This maintains concepts of form \some r.A
	// This concept will have r.somes.get(A) = \some r.A
	public HashMap<Basic, Some> somes = new HashMap<Basic, Some>();

	public HashSet<Role> disjoints = new HashSet<Role>();

	//	public boolean sat = true;

	// OWL-BGP use, indicating corresponding subjects
	public HashSet<Singleton> subjects = new HashSet<Singleton>();

	// cardinality only
	public HashSet<CardinAtomic> cardiAtomics = new HashSet<CardinAtomic>();

	/**
	 * This method adds an axiom "A \sub \some this.B"
	 * @param A
	 * @param B
	 */
	public void addrelation(Basic A, Basic B) {
		// TODO Auto-generated method stub
		HashSet<Basic> list = Relations.get(A);

		// we also need to update the size of the relation
		int size;

		if(list == null)
		{
			list = new HashSet<Basic>();
			Relations.put(A, list);

			// if a has not been used as a subject before, the current size = 0 
			size = 0;
		}
		else
			size = RelationSize.get(A);
		list.add(B);

		// update the size
		if(B instanceof CardinAtomic)
			size+=((CardinAtomic)B).minCardin;
		else
			size+=1;

		RelationSize.put(A, size);

		// when a new relation is added, perform cardinality test.
		cardinTest1(A,B);
	}

	/**
	 * This method performs cardinality test when A \sub \some this.B is recently derived.
	 * The test is passed iff there is a cardinality restriction >=n this.X in the ontology, s.t.
	 * A \sub \some this.B1, ..., Bm
	 * B1, ..., Bm are disjoint with each other
	 * B1, ..., Bm are subconcepts of X
	 * The total number of minimal instances in B1, ..., Bm >= n.
	 * In this case, we will derive A \sub >=n this.X.
	 * @param A
	 * @param B
	 * @return True if the test is passed, False otherwise.
	 */
	public boolean cardinTest1(Basic A, Basic B){
		boolean toprocess = false;
		for(CardinAtomic cardiAtomic:cardiAtomics)
		{
			Atomic X = cardiAtomic.base;
			int threshold = cardiAtomic.minCardin;
			Some target = somes.get(cardiAtomic);
			// we only perform test with limited cardinality value
			if(target != null && threshold <= RELReasonerConfiguration.cardinThreshold)
				if(B.subsumers.contains(X) && Relations.get(A) != null && !A.subsumers.contains(target) && !A.queue.contains(target))
				{
					// In order to avoid repeated test, we maintain all the tested sub-concept of X
					// in A.fillerSubConcepts.
					ArrayList<Basic> fillerSubConcepts = A.fillerSubConcepts.get(target);
					if(fillerSubConcepts == null)
					{
						fillerSubConcepts = new ArrayList<Basic>();
						A.fillerSubConcepts.put(target, fillerSubConcepts);
						A.totalCardinality.put(target, 0);
					}
					// Similarly, the total number of this-objects of type X for any instance of A
					// is maintained in A.totalCardinality
					int size = A.totalCardinality.get(target);
					fillerSubConcepts.add(B);
					size+=B.minCardin;
					A.totalCardinality.put(target, size);

					// We recursively combine different possible sub-concepts of X and test:
					// 1. if they are mutually disjoint from each other;
					// 2. if their total number of cardinalities of each sub-concepts exceed the threshold
					ArrayList<Basic> comb = new ArrayList<Basic>();
					if(size >= threshold && combTest(fillerSubConcepts, 0, threshold, size, comb))
						toprocess = A.queue.add(target)?true:toprocess;
				}
		}
		return toprocess;	
	}

	/**
	 * This method performs cardinality test when B \sub filler can be derived,
	 * and A \sub \some this.B has been tested.
	 * If the test is passed, we can also derive A \sub >=n this.filler.
	 * @param A
	 * @param B
	 * @param filler
	 * @return True if the test is passed, False otherwise.
	 */
	public boolean cardinTest2(Basic A, Basic B, Basic filler){
		boolean toprocess = false;
		for(CardinAtomic cardiAtomic:cardiAtomics)
		{
			Atomic X = cardiAtomic.base;
			int threshold = cardiAtomic.minCardin;
			Some target = somes.get(cardiAtomic);
			if(target != null && threshold <= RELReasonerConfiguration.cardinThreshold && X == filler)
				if(B.subsumers.contains(X) && Relations.get(A) != null && !A.subsumers.contains(target) && !A.queue.contains(target))
				{
					ArrayList<Basic> fillerSubConcepts = A.fillerSubConcepts.get(target);

					// Now that I think about this, I think 
					// B should have already been added into A.fillerSubConcepts. 
					// And B.minCardin should have already been added into A.totalCardinality. 
					// So the following might not be needed.
					// Need further test.
					if(fillerSubConcepts == null)
					{
						fillerSubConcepts = new ArrayList<Basic>();
						A.fillerSubConcepts.put(target, fillerSubConcepts);
						A.totalCardinality.put(target, 0);
					}
					int size = A.totalCardinality.get(target);
					fillerSubConcepts.add(B);
					size+=B.minCardin;
					A.totalCardinality.put(target, size);
					// The above part might not be needed.


					ArrayList<Basic> comb = new ArrayList<Basic>();
					if(size >= threshold && combTest(fillerSubConcepts, 0, threshold, size, comb))
						toprocess = A.queue.add(target)?true:toprocess;
				}
		}

		return toprocess;	
	}

	/**
	 * This method recursively constructs a sub-set comb of fillerSubConcepts from startid
	 * with numLeft elements and test if they are mutually disjoint, 
	 * and if their cardinalities sum up to target.  
	 * @param fillerSubConcepts
	 * @param startid
	 * @param target
	 * @param cardinalityLeft
	 * @param comb
	 * @return True if the sub-set can be found, False otherwise.
	 */
	boolean combTest(ArrayList<Basic> fillerSubConcepts, int startid, int target, int cardinalityLeft, ArrayList<Basic> comb)
	{
		// This method employs a typical backtracking algorithm
		// comb is the current partial solution
		// startid is the starting index for the next element to add into comb
		// target is the cardinality to achieve with new elements
		// cardinalityLeft is the total cardinality of un-examined elements

		// the examination starts from element with index startid 
		for(int i = startid;i < fillerSubConcepts.size();i++)
		{
			// when an element is examined, its cardinality is removed from cardinalityLeft
			cardinalityLeft-=fillerSubConcepts.get(i).minCardin;
			// if the candidate is disjoin with existing elements in comb
			if(disjointnessTest(comb, fillerSubConcepts.get(i)))
			{
				// if the target can be achieved by the candidate, we found a comb
				if(target <=fillerSubConcepts.get(i).minCardin)
					return true;
				// otherwise, we add the candidate into the comb,
				// and look for next element from the next index
				// also the target needs to be updated
				comb.add(fillerSubConcepts.get(i));
				if(combTest(fillerSubConcepts, i+1,target-fillerSubConcepts.get(i).minCardin,cardinalityLeft, comb))
					return true;
				comb.remove(fillerSubConcepts.get(i));
			}
			if(cardinalityLeft < target)
				break;
		}
		return false;
	}

	/**
	 * This method tests if candidate is disjoint with all elements in comb
	 * @param comb
	 * @param candidate
	 * @return True if candidates is disjoint with all elements in comb, False otherwise.
	 */
	boolean disjointnessTest(ArrayList<Basic> comb, Basic candidate){
		for(Basic bsc1:comb)
			if(bsc1 instanceof Singleton && candidate instanceof Singleton)
			{
				if(!bsc1.asSingleton().differentIndividuals.contains(candidate))
					return false;
			}
			else if(candidate.complement == null ||(candidate.complement != null && !bsc1.subsumers.contains(candidate.complement)))
				if(bsc1.complement == null || (bsc1.complement != null && !candidate.subsumers.contains(bsc1.complement)))
					return false;
		return true;
	}

	// Duo-ontology classification variations of the above methods
	// Might need more testing
	public void addTempRelation(Basic A, Basic B) {
		// TODO Auto-generated method stub
		if(tempRelations.get(A) != null)
			tempRelations.get(A).add(B);
		else
		{
			HashSet<Basic> newa = new HashSet<Basic>();
			newa.add(B);
			tempRelations.put(A, newa);
		}
	}
	public boolean tempCardinTest2(Basic a, Basic b, Basic B) {
		// TODO Auto-generated method stub
		boolean toprocess = false;
		for(CardinAtomic cardiAtomic:cardiAtomics)
		{
			Atomic atomic = cardiAtomic.base;
			int len = cardiAtomic.minCardin;
			Some target = somes.get(cardiAtomic);
			if(target != null && len <= RELReasonerConfiguration.cardinThreshold && atomic == B)
				if((b.subsumers.contains(atomic) || b.tempSubsumers.contains(atomic)) && (Relations.get(a) != null || tempRelations.get(a) != null) && !a.subsumers.contains(target) && !a.tempSubsumers.contains(target) && !a.queue.contains(target))
				{
					{
						ArrayList<Basic> completeList = a.fillerSubConcepts.get(target);
						if(completeList == null)
						{
							completeList = new ArrayList<Basic>();
							a.fillerSubConcepts.put(target, completeList);
							a.totalCardinality.put(target, 0);
						}
						int size = a.totalCardinality.get(target);
						completeList.add(b);
						size+=b.minCardin;
						a.totalCardinality.put(target, size);
						ArrayList<Basic> comb = new ArrayList<Basic>();
						if(size >= len && combTest(completeList, 0, len, size, comb))
							toprocess = a.queue.add(target)?true:toprocess;
					}
				}
		}

		return toprocess;	

	}

	// End Duo-ontology classification


	public Role(int key)
	{
		id = key;
		subsumers.add(this);
	}
	public Role(OWLObjectProperty role, int key)
	{
		this(key);
		this.uri = role.getIRI();
	}

	@Override
	public int hashCode() {
		return id;
	}

	@Override
	public String toString() {
		// TODO Auto-generated method stub
		if(uri == null)
			return "ApproxR"+id;
		else
			return uri.toString();
	}

}
