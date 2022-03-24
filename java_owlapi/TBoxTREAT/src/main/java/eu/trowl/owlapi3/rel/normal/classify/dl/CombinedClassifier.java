package eu.trowl.owlapi3.rel.normal.classify.dl;

import java.util.HashSet;
import java.util.Map.Entry;
import java.util.Set;

import eu.trowl.owlapi3.rel.normal.model.Atomic;
import eu.trowl.owlapi3.rel.normal.model.Basic;
import eu.trowl.owlapi3.rel.normal.model.CardinAtomic;
import eu.trowl.owlapi3.rel.normal.model.CardinalityEntry;
import eu.trowl.owlapi3.rel.normal.model.Description;
import eu.trowl.owlapi3.rel.normal.model.Implies;
import eu.trowl.owlapi3.rel.normal.model.Ontology;
import eu.trowl.owlapi3.rel.normal.model.QueueEntry;
import eu.trowl.owlapi3.rel.normal.model.Role;
import eu.trowl.owlapi3.rel.normal.model.RoleConcept;
import eu.trowl.owlapi3.rel.normal.model.Singleton;
import eu.trowl.owlapi3.rel.normal.model.Some;

/***
 * This class is the classifier for combined TBox and ABox reasoning.
 * @author Yuan Ren
 * @version 2013-10-09
 */

public class CombinedClassifier{

	/*
	 * @version 2013-10-09
	 * 1. implement the disjunction resolution rule in addSubsumer();
	 * 2. implement the subsumption reverse propagation in addSubsumer(); 
	 * @version 2013-09-30
	 * 1. R11 enabled for smallT and smallA;
	 * 2. added ONLY link checking for A\sub \some r.B and A \sub B;
	 * @version 2013-07-16
	 * 1. introduce the topQueue;
	 * 2. check timeout of the reasoner;
	 * 3. when TBox already classified, we skip the TBox part and do ABox only;
	 * 4. use set for tempQueue and tempTopQueue. Directly refer to queue and topQueue;
	 * 5. if TBox reasoning only, process only the active Singletons in ABox();
	 * 6. replace ERestriction with Some;
	 * 7. when TBox only, we compute rel only for related roles; when ABox, we compute rel for directly asserted or related roles;
	 * 	7.a. i.e. when !ABox, all unrelated roles are skipped; when ABox, indirect unrelated roles are skipped;
	 * 8. cardinality test in addSubsumer_Duoe;
	 * 9. update the duo ontology classification based on the vanilla classification;
	 * 10. introduce TBox and ABox parameters into completion() and completion_duo();
	 * 11. only initialise() when TBox=true;
	 * 12. separate TBox and ABox postprocessing and only call them when TBox =True or ABox = True, respectively;
	 * @version 2013-06-12
	 * 1. update various places to return when the ontology is inconsistent;
	 * 2. update the addSubsumer() method to return inconsistency when \top\sub\bot;
	 * @version 2013-06-11
	 * 1. update the functionality checking condition
	 * @version 2013-05-20
	 * 1. fixed an infinite loop bug in process_new_edge
	 * has something to do with the r \sub {s,r}, s \sub {r,s}
	 * @version 2013-05-06
	 * 1. included functionality checking of relations (for FMA Constitutional particularly)
	 * @version 2013-04-07
	 * fixed a bug that causes nullpointerexception
	 * @version 2012-05-18
	 */

	public Ontology ontology;
	protected Atomic bot;
	protected Atomic top;

	// the queue of the top concept
	protected HashSet<Basic> topQueue = new HashSet<Basic>();

	// a flag to show if ABox reasoning is being performed
	private boolean ABox = false;

	/**
	 * This method perform the completion of the TBox and/or ABox
	 * @param TBox: a boolean parameter indicating if TBox needs to be classified
	 * @param ABox: a boolena parameter indicating if ABox needs to be realised 
	 */
	public void completion(boolean TBox, boolean ABox) {
		this.ABox = ABox;
		bot = (Atomic) ontology.descriptions.get(0);
		top = (Atomic) ontology.descriptions.get(1);

		// initialise the ontology when TBox reasoning is needed
		// this is usually the first time reasoning is performed
		if(TBox)
			initialize();

		// the termination variable of the loop
		boolean toprocess = true;

		// temporary queue for the current concept
		HashSet<Description> tempqueue;

		// temporary queue for the top concept
		HashSet<Basic> tempTopQueue;

		// the loop for the materialisation
		while(toprocess && ontology.consistency && !Thread.currentThread().isInterrupted())
		{
			// the loop for TBox classification
			while(TBox  && toprocess && ontology.consistency && !Thread.currentThread().isInterrupted())
			{
				toprocess = false;
				tempTopQueue = topQueue;
				topQueue = new HashSet<Basic>();

				// process all the basic concepts
				for(int i = 1;i < ontology.basicConceptNum;i ++)	// we don't process bot
				{
					Basic desc = (Basic)ontology.descriptions.get(i);

					// if unsatisfiable, skip;
					// if singleton, skip (will be done in ABox());
					// if not activated, skip;
					if(desc.subsumers.contains(bot) || !desc.active || (desc instanceof Singleton))
						continue;

					// the queue entries of the top concept should be processed by all satisfiable concepts
					desc.queue.addAll(tempTopQueue);

					// the loop for each basic concept
					while(!desc.subsumers.contains(bot) && desc.queue.size()>0 && !Thread.currentThread().isInterrupted())
					{
						tempqueue = desc.queue;
						desc.queue = new HashSet<Description>();

						// the loop for each queue entry
						for(Description x:tempqueue)
						{
							toprocess = complete(desc, x)?true:toprocess;
							if(!ontology.consistency)
								return;
							if(desc.subsumers.contains(bot))
								break;
						}
					}
				}

			}

			if(!ontology.consistency)
				return;

			// ABox realisation
			toprocess = false;
			toprocess = toprocess || ABox();

			// NBox reasoning
			if(ontology.NOnto)
				toprocess = toprocess || NBox();
			// end of NBox reasoning

		}
		if(!ontology.consistency)
			return;
		if(TBox)
			postprocessing();
		if(ABox)
			postprocessingABox();

	}


	/**
	 * This method initialise the ontology for reasoning 
	 */

	public void initialize() {

		// termination variable for role related rules
		boolean roleclosure = true;

		// initialise role hierarchies
		while(roleclosure)
		{
			roleclosure = false;
			for(int i = 0;i < ontology.roleNum;i ++)
			{
				Role r = ontology.roles.get(i);
				HashSet<Role> rSubsumers = new HashSet<Role>(r.subsumers);
				rSubsumers.remove(r);
				for(Role s:rSubsumers)
				{
					// R0
					roleclosure = r.subsumers.addAll(s.subsumers)? true:roleclosure;
					// R14
					if(r.inverse != null && s.inverse != null)
						roleclosure = r.inverse.subsumers.addAll(s.inverse.subsumers)?true:roleclosure;
					// I didn't implement rules using role complements as no ontology uses them
				}
				// R17
				for(Entry<Role, HashSet<Role>> entry:r.RightComposition.entrySet())
				{
					Role s = entry.getKey();
					if(s.inverse == null || r.inverse == null || s.inverse.equals(r))
						continue;
					HashSet<Role> ts = s.inverse.RightComposition.get(r.inverse);
					if(ts == null)
					{
						ts = new HashSet<Role>();
						s.inverse.RightComposition.put(r.inverse, ts);
					}
					for(Role t:entry.getValue())
					{
						roleclosure = ts.add(t.inverse)?true:roleclosure;
					}
				}

			}
		}

		// also initialise the subroles for each role
		for(int i = 0;i < ontology.roleNum;i ++)
		{
			Role r = ontology.roles.get(i);
			for(Role s:r.subsumers)
				s.subroles.add(r);
		}

		// initialise the basic concepts
		initializeBasics();

	}


	/**
	 * This method initialise the basic concepts for reasoning.
	 */
	protected void initializeBasics() {
		// TODO Auto-generated method stub
		// Basically, for each basic concept B, ->B should be in B.Ohat,
		// also, B and top should be in B.queue

		bot.Ohat.add(bot.entry);
		top.Ohat.add(top.entry);
		addAll2queue(top, top);
		for(int i = 2;i < ontology.basicConceptNum;i ++)
		{
			Basic desc = (Basic) ontology.descriptions.get(i);
			desc.Ohat.add(desc.entry);
			addAll2queue(desc, desc);
			addAll2queue(desc, top);
		}

		// we also initialise the tautology B \sub B for each basic concept B
		// this way we don't need to repeat in reasoning
		for(int i = 1;i < ontology.basicConceptNum;i ++)
		{
			Basic desc = (Basic) ontology.descriptions.get(i);

			desc.subsumers.add(desc);
		}
		bot.subsumers.add(bot);				
	}


	/**
	 * This method performs reasoning for a single concept.
	 * It goes through the queue entries of an inherited concept and performs reasoning accordingly.
	 * @param desc: the concept on which reasoning is performed.
	 * @param inherited: the concept whose queue entries should be inherited.
	 * @return True if new result is generated and False otherwise.
	 */
	protected boolean complete(Basic desc, Description inherited)
	{
		boolean toprocess = false;

		// we need to have a global copy for inherited
		// as well as a temporary buffer for inherited.Ohat
		// This is because new elements may be added into inherited.Ohat when executing the loop
		tempInherited = inherited;
		tempOhat = new HashSet<QueueEntry>();
		for(QueueEntry X:inherited.Ohat)
		{
			toprocess = process(desc,X)? true:toprocess;
			if(desc.subsumers.contains(bot))
				break;
		}
		inherited.Ohat.addAll(tempOhat);
		return toprocess;

	}

	// a global copy of inherited
	Description tempInherited;

	// a global temporary buffer for inherited.Ohat
	HashSet<QueueEntry> tempOhat;


	/**
	 * This method process a basic concept with a queue entry
	 * @param A: the basic concept being processed.
	 * @param X: the queue entry being processed.
	 * @return True if new result result is derived, False otherwise.
	 */
	public boolean process(Basic A, QueueEntry X)
	{
		boolean toprocess = false;
		if(X instanceof Implies)
		{
			Implies impliesX = (Implies) X;
			Basic B = impliesX.rhs;
			HashSet<Basic> SA = A.subsumers;
			HashSet<Basic> Bs = impliesX.lhs;
			if(! SA.contains(B))
			{
				// R1 and R2
				if(Bs == null || SA.containsAll(Bs))
				{
					toprocess = addSubsumer(A,B)?true:toprocess;
				}

				// R11, we apply it only for ontology with small TBox
				if(!ontology.largeA && !ontology.largeT)
					if(Bs != null && B.complement != null && A.subsumers.contains(B.complement))	// B is \bot
					{
						for(Basic candidate:Bs)
						{
							Set<Basic> newBs = new HashSet<Basic>(Bs);
							newBs.remove(candidate);
							Basic newsuper = candidate.complement;
							if(newsuper != null && SA.containsAll(newBs) && !SA.contains(newsuper))
							{
								toprocess = addSubsumer(A,newsuper)?true:toprocess;
							}
						}
					}
				// end of R11

			}
		}
		else	// X instanceof ERestriction
		{
			Some someX = (Some) X;
			Role r = someX.role;
			Basic B = (Basic) someX.concept;
			if(!r.Relations.containsKey(A) || !r.Relations.get(A).contains(B))
			{
				if(!B.subsumers.contains(bot))
					toprocess = process_new_edge(A,r,B)?true:toprocess;
				else	// R5
					toprocess = addSubsumer(A,bot)?true:toprocess;
				if(!ontology.consistency)
					return false;
			}
		}
		return toprocess;
	}


	/**
	 * This method tries to derive the subsumption relation between the two parameters
	 * @param A: the candidate sub-concept
	 * @param B: the canddidate super-concept
	 * @return True if the subsumption is derived, False otherwise
	 */
	protected boolean addSubsumer(Basic A, Basic B) {
		// TODO Auto-generated method stub

		if(A.subsumers.contains(B))
			return false;

		A.subsumers.add(B);
		if((A == top || A instanceof Singleton) && B == bot)
		{
			ontology.consistency = false;
			return false;
		}

		// R10
		Basic nB = B.complement;
		if(nB != null && A.complement != null)
		{
			Implies implies = (Implies) A.complement.entry;
			addAll2queue(nB,A.complement);
			nB.Ohat.add(implies);
		}
		else if(A.originalSubsumee != null)	
			// a special case for situation when B.complement or A.complement does not exists.
			// this may be incomplete though.
			for(Basic subsumee:A.originalSubsumee)
				if(!subsumee.subsumers.contains(B))
				{
					subsumee.Ohat.add(B.entry);
					addAll2queue(subsumee, B);
				}
		// a special case for NBox reasoning.
		// This may also be needed for non-NBox reasoning scenarios but may affect performance.
		if(ontology.NOnto && B instanceof Singleton && A.complement!=null)
			for(Singleton diff:((Singleton)B).differentIndividuals)
			{
				addAll2queue(diff,A.complement);
				diff.Ohat.add(A.complement.entry);
			}
		// end of R10

		// Check if A becomes unsatisfiable
		boolean unsat = false;
		if(B.subsumers.contains(bot) || A.subsumers.contains(nB))
			unsat = true;

		// When A is still satisfiable
		if(!unsat)
		{
			// A should inherit all queue entries of B
			addAll2queue(A,B);

			for(RoleConcept rc : A.predecessors)
			{
				Role r = rc.role;
				Basic Aprime = rc.concept;

				// Since we have A' \sub some r.A, A \sub B
				// We should also have A' \sub some r.B.
				// However we don't need such a rule for ordinary materialisation,
				// so this results will not be inferred.
				// In order to make sure the cardinality test works properly,
				// we need to call it here.
				r.cardinTest2(Aprime, A, B);

				// R4
				if(getexist(r,B) != null)
					addAll2queue(Aprime, getexist(r,B));

				if(B instanceof Singleton)
				{
					Singleton singleB = (Singleton) B;

					// One of the undocumented rule:
					// Inverse Functional Role Individuals
					// A \sub {b}, X\sub \some r.A, InverseFunctional(r), (x,b):R -> X\sub {x}
					if(r.inverse != null && r.inverse.functional)
					{
						if(r.inverse.Relations.get(singleB) != null)
							for(Basic bsc:r.inverse.Relations.get(singleB))
							{
								if(bsc instanceof Singleton)
								{
									Singleton indi = (Singleton) bsc;
									if(!Aprime.subsumers.contains(indi))
									{
										addAll2queue(Aprime,indi);
										Aprime.Ohat.add(indi.entry);
									}
								}
							}
					}

				}

			}

			// This is a variation of R4 with inverse relations between individuals:
			// If (a,a'):R and {a} \sub B, then a': \some R^-.B
			// We need this rule because we don't infer (a',a):R^- in reasoning.
			// Hence we cannot directly make use of the R4. We need this variation.
			// This is needed for for example, the BoC ontologies.
			if(ontology.chains)
				if(A instanceof Singleton)
				{
					for(Role R:ontology.roles.values())
					{
						if(R.inverse != null && getexist(R.inverse, B)!= null && R.Relations.get(A) != null)
							for(Basic Aprime:R.Relations.get(A))
								if(Aprime instanceof Singleton)
								{
									addAll2queue(Aprime, getexist(R.inverse,B));

								}
					}
				}

			// R13
			CardinalityEntry[] AEntries = A.cardins;
			CardinalityEntry[] BEntries = B.cardins;

			if(!(A instanceof Singleton) && !(B instanceof Singleton) && AEntries != null && BEntries != null)
			{
				int Ahead = AEntries.length - 1;
				int Bhead = BEntries.length - 1;
				for(int i = Ahead - 1;i >= 0;i --)
				{
					int j = Bhead - 1;
					for(;j >= 0;j --)
					{
						if(BEntries[j].n > AEntries[i].n)
							break;
					}
					if(j + 1 < Bhead)
					{
						Basic An = (Basic) AEntries[i].basen;
						Basic Bn = (Basic) BEntries[j+1].basen;
						Implies implies = Bn.entry;
						An.Ohat.add(implies);
						addAll2queue(An,Bn);
					}
					Bhead = j+1;
				}
			}
			// end of R13

			// One of the undocumented rule:
			// Disjunction Resolution Rule
			// Consider the following axioms:
			//			A \sub B \or C
			//			B \sub D
			//			C \sub D
			//		The 1st axiom will have the following approximation:
			//			A \sub X1
			//			cX1 = cB \and cC
			//		Hence we can infer that:
			//			cD \sub cB   (*)
			//			Similarly cD \sub cC (*)
			//			=>
			//			cD \sub cX1 (*)
			//			=>
			//			X1 \sub D
			//			=>
			//			A \sub D
			//		However, if cD is not approximated, then (*) will not be inferred. Hence A \sub D will not be inferred.
			//
			//		To address this issue, we have the following rule:
			//			A1 \sub B, …, An \sub B
			//			cA1 \and … \and cAn \sub cX
			//			=>
			//			X\sub B
			// In the following implementation, A is treated as one of the Ais.
			// And imply.rhs is the cX.
			if(ontology.disRes)
				if(A.complement != null)
					for(QueueEntry entry:A.complement.Ohat)
						if(entry instanceof Implies)
						{
							Implies imply = (Implies) entry;
							if(imply.rhs.complement != null && !imply.rhs.complement.subsumers.contains(B) && imply.lhs != null)
							{
								boolean proceed = true;
								for(Basic lhs:imply.lhs)
									if(lhs.complement == null || !lhs.complement.subsumers.contains(B))
									{
										proceed = false;
										break;
									}
								if(proceed)
								{
									addAll2queue(imply.rhs.complement, B);
									if(imply.rhs.complement == tempInherited)
										tempOhat.add(B.entry);
									else
										imply.rhs.complement.Ohat.add(B.entry);
								}
							}
						}
			// end of disjunction resolution rule
		}
		else	// When A becomes unsatisfiable
		{
			A.subsumers.add(bot);

			// update the queue and entries of Top.
			if(A.complement != null)
			{
				top.Ohat.add(A.complement.entry);
				addAll2queue(top, A.complement);
				topQueue.add(A.complement);
			}

			if(A instanceof Singleton)
			{
				ontology.consistency = false;
				return true;
			}

			// R5
			for(RoleConcept rc : A.predecessors)
			{
				Basic Aprime = rc.concept;
				addSubsumer(Aprime, bot);
				if(!ontology.consistency)
					return false;
			}
			for(Basic Aprime:A.reachableBy)
			{
				addSubsumer(Aprime,bot);
				if(!ontology.consistency)
					return false;
			}
		}

		return true;
	}


	/**
	 * This method tries to derive new subsumption between A and \some r.B
	 * @param A: The candidate sub-concept
	 * @param r: The role of the candidate super-concept
	 * @param B: The filler of the candidate super-concept
	 * @return True if the subsumption is indeed derived and Flase otherwise.
	 */
	protected boolean process_new_edge(Basic A, Role r, Basic B) {
		// TODO Auto-generated method stub

		boolean toprocess = false;
		if(A == null || B == null)
			return toprocess;
		if(ABox)	// We always derive A \sub \some r.B when it is for ABox reasoning
		{
			addrelation(A,r,B);
			toprocess = true;
		}
		else if(r.related)	// In TBox reasoning, we only derive A \sub \some r.B when r is related
		{
			B.active = true;	// we activate B when it is used as a filler in a derived axiom
			addrelation(A,r,B);
			toprocess = true;
		}
		for(Role s : r.subsumers)
		{
			// Note that the following rule is not applied:
			// A \sub \some r.B
			// r \sub s
			// =>
			// A \sub \some s.B
			// In the situation specified below.
			// The reason is to save space as the result is not necessary for reasoning. 
			// Basically, when r and r.inverse are not related, then A \sub \some r.B will be 
			// further processed only when it is in ABox reasoning and the super roles of r
			// will never be processed.
			if((!ABox || s!=r) && !s.related && (s.inverse == null ||!s.inverse.related ))
				continue;
			if(r != s)
			{
				B.active = true;
				addrelation(A,s,B);
				toprocess = true;
			}
			
			// R4
			for(Basic Bprime: B.subsumers)
			{

				if(getexist(s,Bprime) != null)
					addAll2queue(A,getexist(s,Bprime));
			}
			
			// The variation of R4 with inverse relations between individuals:
			// {A} \sub \some r.{B}
			// {A} \sub A;
			// r \sub s
			// =>
			// {B} \sub \some s^-.A
			if(A instanceof Singleton && B instanceof Singleton)
				if(s.inverse !=null)
				{
					for(Basic Aprime: A.subsumers)
						if(getexist(s.inverse,Aprime) != null)
							addAll2queue(B,getexist(s.inverse,Aprime));
					if(getexist(s.inverse,top)!=null)
						addAll2queue(B,getexist(s.inverse,top));
				}

			// This is a bit ad hoc part for large ontologies only.
			// It works for ontologies like FMA
			// One of the undocumented rule:
			// A \sub \some s.{b}
			// X \sub \some s.{a}
			// a != b
			// Functional(s)
			// =>
			// X \sub \neg A
			// Particularly, when X == A, we have A \sub \bot
			if((ontology.originalNamedConcepts.size() < 70000 || ontology.originalNamedConcepts.size() > 80000) && B instanceof Singleton && s.functional)
			{
				for(Singleton aprime:B.asSingleton().differentIndividuals)
				{
					for(RoleConcept rc:aprime.predecessors)
					{
						if(rc.role == s)
						{
							if(A == rc.concept)
							{
								addSubsumer(A, bot);
								if(!ontology.consistency)
									return false;
								return true;
							}
							else if(A.complement != null)
							{
								addAll2queue(rc.concept, A.complement);
								rc.concept.Ohat.add(A.complement.entry);
							}
						}
					}
				}
			}

			// NBox reasoning
			// A\sub \some R.{b}, InverseFunctional(R), (a,b):R -> A\sub {a}
			if(ontology.NOnto)
				if(s.inverse != null && s.inverse.functional && B instanceof Singleton)
				{
					if(s.inverse.Relations.containsKey(B))
						for(Basic a:s.inverse.Relations.get(B))
							if(a instanceof Singleton)
							{
								addAll2queue(A,a);
								A.Ohat.add(a.entry);
							}
					for(Basic a:s.Relations.keySet())
						if(a instanceof Singleton && s.Relations.get(a)!= null && s.Relations.get(a).contains(B))
						{
							addAll2queue(A,a);
							A.Ohat.add(a.entry);
						}
				}
			// end of NBox reasoning

			// R8
			HashSet<RoleConcept> rcs = new HashSet<RoleConcept>(A.predecessors);
			for(RoleConcept rc: rcs)
			{
				Role t = rc.role;
				Basic Aprime = rc.concept;
				HashSet<Role> set = t.RightComposition.get(s);
				if(set != null)
					for(Role u :set)
					{
						if( u.related && (!u.Relations.containsKey(Aprime) || !u.Relations.get(Aprime).contains(B)))
							process_new_edge(Aprime,u,B);
					}
			}
			for(Role t:s.RightComposition.keySet())
			{
				if(!t.related)
					continue;

				HashSet<Role> set = s.RightComposition.get(t);
				if(set != null)
				{
					for(Role u:set)
					{
						if(!u.related)
							continue;
						HashSet<Basic> bprimes = t.Relations.get(B);
						if(bprimes != null)
							for(Basic Bprime:t.Relations.get(B))
							{
								if(!u.Relations.containsKey(A) || !u.Relations.get(A).contains(Bprime))
									process_new_edge(A,u,Bprime);
							}
					}
				}
			}


			// A variation of R8 with inverse roles between individuals
			if(A instanceof Singleton && B instanceof Singleton)
			{
				for(Role it:ontology.roles.values())
				{
					Role t = it.inverse;
					if(t!=null && it.Relations.containsKey(B))
						for(Role tsup:t.subsumers)
							if(tsup.RightComposition.containsKey(s.inverse))
								for(Role u:tsup.RightComposition.get(s.inverse))
									if(u.inverse!=null)
										for(Basic Cprime:it.Relations.get(B))
											if(Cprime instanceof Singleton && u.inverse.Relations.containsKey(A) && !u.inverse.Relations.get(A).contains(Cprime))
												process_new_edge(A,u.inverse,Cprime);
				}
				for(RoleConcept rc: rcs)
				{
					Role t = rc.role;
					Basic Aprime = rc.concept;
					if(s.inverse!=null )
					{
						for(Role tsup:t.subsumers)
							if(tsup.inverse !=null)
								if(s.inverse.RightComposition.containsKey(tsup.inverse))
									for(Role u:s.inverse.RightComposition.get(tsup.inverse))
										if(u.related && u.inverse != null && (!u.inverse.Relations.containsKey(Aprime) || !u.inverse.Relations.get(Aprime).contains(B)))
											process_new_edge(Aprime,u.inverse,B);
					}
				}

			}

			// Further variation of R8 with inverse roles
			if(ontology.chains)
				if(A instanceof Singleton)
				{
					for(Role it:ontology.roles.values())
					{
						Role t = it.inverse;
						if(t!=null && t.RightComposition.containsKey(s) && it.Relations.get(A) != null)
						{
							for(Role u:t.RightComposition.get(s))
								for(Basic Aprime:it.Relations.get(A))
									if(Aprime instanceof Singleton && (!u.Relations.containsKey(Aprime) || !u.Relations.get(Aprime).contains(B)))
										process_new_edge(Aprime, u, B);
						}
					}

					if(B instanceof Singleton && s.inverse!=null)
					{
						for(RoleConcept RC:B.predecessors)
						{
							Role t = RC.role;
							Basic Bprime  = RC.concept;

							if(Bprime instanceof Singleton && t.RightComposition.containsKey(s.inverse))
								for(Role u:t.RightComposition.get(s.inverse))
									if(!u.Relations.containsKey(Bprime) || !u.Relations.get(Bprime).contains(A))
										process_new_edge(Bprime, u, A);
						}
					}
				}
		}
		// Even if A \sub \some r.B will not be actually derived,
		// A can still reach B.
		if(toprocess == false)
			B.reachableBy.add(A);
		return toprocess;
	}


	/**
	 * This method add the A \sub \some r.B to the ontology
	 * @param A
	 * @param r
	 * @param B
	 */
	private void addrelation(Basic A, Role r, Basic B) {
		// TODO Auto-generated method stub
		r.addrelation(A,B);
		B.addPredecessor(r, A);
		universalRestrictionRule(A,r);
	}

	/**
	 * This method implements the universal role restriction approximation rule.
	 * @param A
	 * @param r
	 */
	private void universalRestrictionRule(Basic A, Role r) {
		// One of the undocumented rule:
		// A \sub \some r.B
		// A \sub X
		// X \sub \only s.C
		// r \sub s
		// =>
		// A \sub \some r.C
		//  
		// In the following implementation, X.onlyLink will leads to \some s.\neg C.
		// Hence C will be X.onlyLine.concept.complement.

		// TODO Auto-generated method stub
		//		for(Basic X:A.subsumers)
		//			if(X.onlyLink!=null && r.subsumers.contains(X.onlyLink.role) && !r.Relations.get(A).contains(((Basic)X.onlyLink.concept).complement))
		//				process_new_edge(A,r,((Basic)X.onlyLink.concept).complement);
	}


	/**
	 * This method performs ABox reasoning
	 * @return True if new ABox reasoning result is derived and False otherwise.
	 */
	protected boolean ABox() {
		// TODO Auto-generated method stub
		boolean toprocess = false;
		for(int id:ontology.individualIDs.values())
		{
			Singleton indi = (Singleton) ontology.descriptions.get(id);
			if(!ABox && !indi.active)
				continue;
			if(ontology.consistency == false)
				break;
			if(indi.subsumers.contains(bot))
			{
				ontology.consistency = false;
				break;
			}

			// Classification of individuals
			// Basically, each individual should inherit all the queue entries of its orignal types.
			while(indi.queue.size() > 0)
			{
				HashSet<Description> tempindiqueue = indi.queue;
				indi.queue = new HashSet<Description>();
				for(Description classification:tempindiqueue)
				{
					toprocess = complete(indi,classification)?true:toprocess;
					if(indi.subsumers.contains(bot))
					{
						ontology.consistency = false;
						break;
					}
				}

				// This part tests satisfiability of cardinality restrictions of individuals
				// It was originally designed for the BoC ontologies.
				// It might be redundant to the new cardinality testing mechanisms.
				if(ontology.chains)
					for(Description desc: ontology.descriptions.values())
					{
						if(desc instanceof Some)
						{
							Some some = (Some)desc;
							if(some.concept instanceof CardinAtomic)
							{
								Role role = some.role;
								CardinAtomic card = (CardinAtomic) some.concept; 
								int num = 0;
								{
									HashSet<HashSet<Singleton>> differs = new HashSet<HashSet<Singleton>>();
									HashSet<Singleton> objs = new HashSet<Singleton>();
									if(role.Relations.containsKey(indi))
										for(Basic obj:role.Relations.get(indi))
										{
											if(obj instanceof Singleton && obj.subsumers.contains(card.base))
											{
												objs.add(obj.asSingleton());
											}
										}
									for(RoleConcept rc:indi.predecessors)
									{
										if(rc.role.subsumers.contains(role.inverse) && rc.concept instanceof Singleton  && rc.concept.subsumers.contains(card.base))
										{
											objs.add(rc.concept.asSingleton());
										}
									}
									for(Singleton obj:objs)
									{
										HashSet<Singleton> newdiffer = new HashSet<Singleton>();
										newdiffer.add(obj);
										differs.add(newdiffer);									
									}
									num = 1;
									for(Singleton obj:objs)
									{
										for(HashSet<Singleton> differ:differs)
										{
											if(obj.differentIndividuals.containsAll(differ))
											{
												differ.add(obj);
												if(differ.size()>num)
													num = differ.size();
												if(num >= card.minCardin)
													break;
											}
										}
										if(num >= card.minCardin)
											break;
									}
									if(num == card.minCardin)
									{
										for(QueueEntry entry:some.Ohat)
										{
											if(entry instanceof Implies)
											{
												Implies imp = (Implies) entry;
												if(!indi.subsumers.contains(imp.rhs))
												{			
													addSubsumer(indi,imp.rhs);
													addAll2queue(indi,imp.rhs);
												}
											}
										}
									}
								}
							}
						}
					}

			}
		}
		return toprocess;
	}


	/**
	 * This method performs NBox reasoning.
	 * @return True if new result is derived and False otherwise.
	 */
	private boolean NBox(){
		boolean toprocess = false;
		for(int i = 1;i < ontology.basicConceptNum;i ++)
		{
			Basic desc = (Basic)ontology.descriptions.get(i);
			if(desc.subsumers.contains(bot) || desc instanceof Singleton)
				continue;

			// We apply the following rule only when the ontology is closed.
			// A' \sub \some r.A, A \sub {a}, InverseFunctional(r) => A' \sub \some r.{a}.
			// It might be Okay to apply this rule even for non-closed ontology.
			for(RoleConcept rc:desc.predecessors)
			{
				Role r = rc.role;
				Basic Aprime = rc.concept;
				if(r.inverse != null && r.inverse.functional)
					for(Basic sub:desc.subsumers)
						if(sub instanceof Singleton && !r.Relations.get(Aprime).contains(sub))
							toprocess = process_new_edge(Aprime, r, sub)?true:toprocess;
			}
		}
		return toprocess;
	}


	/**
	 * This method performs post-processing of reasoning results, mainly for OWLAPI functionalities.
	 */
	protected void postprocessing() {
		// TODO Auto-generated method stub
		// Most for equivalence between concepts and roles
		// For the sake of OWLAPI, we focus on named concepts in the original ontology
		bot.equivalence.add(bot);
		for(Basic concept:ontology.originalNamedConcepts)
		{
			concept.equivalence.add(concept);
			if(concept.subsumers.contains(bot))
			{
				bot.equivalence.add(concept);
				concept.equivalence.add(bot);
				continue;
			}
			for(Basic subsumer:concept.subsumers)
				if(subsumer.original && subsumer.subsumers.contains(concept))
					concept.equivalence.add(subsumer);
		}
		for(Role role:ontology.roles.values())
		{
			role.equivalence.add(role);
			for(Role subsumer:role.subsumers)
				if(subsumer.subsumers.contains(role))
					role.equivalence.add(subsumer);
		}
	}

	/**
	 * This method performs post-processing of ABox reasoning
	 */
	protected void postprocessingABox(){
		// For the sake of OWLAPI functionality, we focus on named individuals in the original ontology.
		for(int id:ontology.individualIDs.values())
		{
			Singleton indi = (Singleton) ontology.descriptions.get(id);
			indi.equivalence.add(indi);
			for(Basic subsumer:indi.subsumers)
			{
				if(subsumer.original && subsumer instanceof Singleton)
					indi.equivalence.add((Singleton)subsumer);
			}
		}

		// When the ontology needs to be queried, we maintain subjects of each role.
		// Remember that in reasoning we don't maintain all the derivable (a,b):s relation.
		// In some cases, we have (a,b):r, and r \sub s, but (a,b):s is skipped.
		// Hence here we add a into s.subjects when a is a in r.subjects for a subrole r of s.
		// Similarly, when we have (b,a):r and r \sub s^-, we don't always infer (a,b):s.
		// Here we also add a into s.subjects.
		if(ontology.BGP)
			for(int id:ontology.individualIDs.values())
			{
				Singleton indi = (Singleton) ontology.descriptions.get(id);
				if(!indi.original)
					continue;
				for(Role s:ontology.roles.values())
				{
					for(Role r:s.subroles)
					{
						if(r.Relations.containsKey(indi))
							s.subjects.add(indi);
					}
					for(RoleConcept rc:indi.predecessors)
						if(rc.role.inverse != null && rc.role.inverse.subsumers.contains(s) && rc.concept instanceof Singleton)
							s.subjects.add(indi);
				}
			}
	}

	/**
	 * This method add a concept into another concepts queue
	 * @param desc: is the target concept whose queue needs to be extended.
	 * @param entry: is the entry concept that needs to be added.
	 */
	protected void addAll2queue(Basic desc, Description entry)
	{
		desc.queue.add(entry);
	}


	/**
	 * A utility method that retrieves an existential restriction object
	 * @param role
	 * @param concept
	 * @return \some role.concept of null if it does not exist.
	 */
	protected Some getexist(Role role, Basic concept) {
		// TODO Auto-generated method stub
		return role.somes.get(concept);
	}

	
	// From here on are the duo-ontology reasoning part of the reasoner.
	// In principle they should be similar to the above single-ontology reasoning part.
	// There are two major differences:
	// 1. When checking the subsumers, Ohat, predecessors, Cardinality entries and relations
	//    of concept and roles, this part needs to check both the permanent elements and temporal elements
	// 2. When adding new subsumers, Ohat, predecessors, cardinality entries and relations
	//    of concepts and roles, this part needs to add into only the temporal parts.
	
	public void completion_duo(boolean ABox) {
		// TODO Auto-generated method stub
		this.ABox = ABox;
		bot = (Atomic) ontology.descriptions.get(0);
		top = (Atomic) ontology.descriptions.get(1);
		initialize_duo();
		boolean toprocess = true;
		HashSet<Description> tempqueue;
		HashSet<Basic> tempTopQueue;
		while(toprocess && !Thread.currentThread().isInterrupted())
		{
			toprocess = false;
			tempTopQueue = topQueue;
			topQueue = new HashSet<Basic>();
			for(int i = 1;i < ontology.basicConceptNum;i ++)
			{
				Basic desc = (Basic)ontology.descriptions.get(i);
				if(desc.subsumers.contains(bot) || desc.tempSubsumers.contains(bot) || !desc.active || (desc instanceof Singleton))
					continue;
				desc.queue.addAll(tempTopQueue);
				while(!desc.subsumers.contains(bot) && !desc.tempSubsumers.contains(bot) && desc.queue.size()>0 && !Thread.currentThread().isInterrupted())
				{
					tempqueue = desc.queue;
					desc.queue = new HashSet<Description>();
					for(Description x:tempqueue)
					{
						for(QueueEntry entry:x.Ohat)
						{
							toprocess = process_duo(desc,entry)? true:toprocess;
							if(desc.tempSubsumers.contains(bot))
								break;
						}
						for(QueueEntry entry:x.tempOhat)
						{
							toprocess = process_duo(desc,entry)? true:toprocess;
							if(desc.tempSubsumers.contains(bot))
								break;
						}
					}
				}
			}

			toprocess = toprocess || ABox_duo();

		}
		postprocessing_duo();

	}


	private void initialize_duo() {
		// TODO Auto-generated method stub
		for(int i = 1;i < ontology.permBasicConceptNum;i ++)
		{
			Basic desc = (Basic) ontology.descriptions.get(i);
			for(Basic subsumer:desc.subsumers)
				if(subsumer.tempOhat.size()>0)
					addAll2queue(desc,subsumer);
			for(RoleConcept roleconcept:desc.predecessors)
			{
				Role role = roleconcept.role;
				Basic basic = roleconcept.concept;
				for(Basic subsumer:desc.subsumers)
				{
					if(role.somes.get(subsumer) != null && role.somes.get(subsumer).tempOhat.size()>0)
						addAll2queue(basic, role.somes.get(subsumer));
					if(subsumer.tempcardins != null)
						for(CardinalityEntry ca:subsumer.tempcardins)
							if(role.cardiAtomics.contains(ca.basen))
								role.tempCardinTest2(basic, desc, subsumer);
				}

			}
		}
		for(int i = ontology.permBasicConceptNum;i < ontology.basicConceptNum;i ++)
		{
			Basic desc = (Basic) ontology.descriptions.get(i);
			addAll2queue(desc, desc);
			addAll2queue(desc, top);
			desc.Ohat.add(desc.entry);
		}
	}


	public boolean process_duo(Basic A, QueueEntry X)
	{
		boolean toprocess = false;
		if(X instanceof Implies)
		{
			Implies newX = (Implies) X;
			Basic B = newX.rhs;
			HashSet<Basic> SA = new HashSet<Basic>();
			for(Basic subsumer:A.subsumers)
				SA.add(subsumer);
			SA.addAll(A.tempSubsumers);
			HashSet<Basic> Bs = newX.lhs;
			if(! SA.contains(B))
			{
				if(Bs == null || SA.containsAll(Bs))
				{
					toprocess = addSubsumer_duo(A,B)?true:toprocess;
				}
			}
		}
		else
		{
			Some newX = (Some) X;
			Role r = newX.role;
			Basic B = (Basic) newX.concept;
			if((!r.Relations.containsKey(A) || !r.Relations.get(A).contains(B)) && (!r.tempRelations.containsKey(A) || !r.tempRelations.get(A).contains(B)))
			{
				if(!B.subsumers.contains(bot))
					toprocess  = process_new_edge_duo(A,r,B)?true:toprocess;
				else
					toprocess = addSubsumer_duo(A,bot)?true:toprocess;
			}
		}
		return toprocess;
	}


	private boolean addSubsumer_duo(Basic A, Basic B) {
		// TODO Auto-generated method stub
		// TODO Auto-generated method stub
		if(A.tempSubsumers.contains(B))
			return false;
		A.tempSubsumers.add(B);

		Basic nB = B.complement;
		if(nB != null && A.complement != null)
		{
			Implies implies = (Implies) A.complement.entry;
			addAll2queue(nB,A.complement);
			nB.tempOhat.add(implies);
		}
		if(!B.subsumers.contains(bot) && !B.tempSubsumers.contains(bot) && !A.subsumers.contains(nB) && !A.tempSubsumers.contains(nB))	// when A is a subconcept of Perp, terminate the processing of Queue(A).
		{
			addAll2queue(A,B);
			HashSet<RoleConcept> leftconnection = new HashSet<RoleConcept>();
			leftconnection.addAll(A.predecessors);
			leftconnection.addAll(A.tempPredecessors);
			for(RoleConcept rc : leftconnection)
			{
				Role r = rc.role;
				Basic Aprime = rc.concept;
				r.cardinTest1(Aprime, A);
				if(getexist(r,B) != null)
				{
					addAll2queue(Aprime,getexist(r,B));
				}

				if(B instanceof Singleton)
				{
					Singleton singleB = (Singleton) B;

					// functional role individuals
					if(r.inverse != null && r.inverse.functional)
					{
						if(r.inverse.Relations.get(singleB) != null)
							for(Basic bsc:r.inverse.Relations.get(singleB))
							{
								if(bsc instanceof Singleton)
								{
									Singleton indi = (Singleton) bsc;
									if(!Aprime.subsumers.contains(indi) && !Aprime.tempSubsumers.contains(indi))
									{
										addAll2queue(Aprime,indi);
										Aprime.tempOhat.add(indi.entry);
									}
								}
							}
						if(r.inverse.tempRelations.get(singleB) != null)
							for(Basic bsc:r.inverse.tempRelations.get(singleB))
							{
								if(bsc instanceof Singleton)
								{
									Singleton indi = (Singleton) bsc;
									if(!Aprime.subsumers.contains(indi) && !Aprime.tempSubsumers.contains(indi))
									{
										addAll2queue(Aprime,indi);
										Aprime.tempOhat.add(indi.entry);
									}
								}
							}
					}

				}
			}

			if(ontology.chains)
				if(A instanceof Singleton)
				{
					for(Role R:ontology.roles.values())
					{
						if(R.inverse != null && getexist(R.inverse, B)!= null)
						{
							if(R.Relations.get(A) != null)
								for(Basic Aprime:R.Relations.get(A))
									if(Aprime instanceof Singleton)
									{
										addAll2queue(Aprime, getexist(R.inverse,B));

									}
							if(R.tempRelations.get(A) != null)
								for(Basic Aprime:R.tempRelations.get(A))
									if(Aprime instanceof Singleton)
									{
										addAll2queue(Aprime, getexist(R.inverse,B));

									}
						}
					}
				}

			CardinalityEntry[] AEntries = A.tempcardins;
			CardinalityEntry[] BEntries = B.tempcardins;

			if(AEntries != null && BEntries != null)
			{
				int Ahead = AEntries.length - 1;
				int Bhead = BEntries.length - 1;
				for(int i = Ahead - 1;i >= 0;i --)
				{
					int j = Bhead - 1;
					for(;j >= 0;j --)
					{
						if(BEntries[j].n > AEntries[i].n)
							break;
					}
					if(j + 1 < Bhead)
					{
						Basic An = (Basic) AEntries[i].basen;
						Basic Bn = (Basic) BEntries[j+1].basen;
						Implies implies = Bn.entry;
						An.tempOhat.add(implies);
						addAll2queue(An,Bn);
					}
					Bhead = j+1;
				}
			}

		}
		else
		{
			A.tempSubsumers.add(bot);

			if(A.complement != null)
			{
				top.tempOhat.add(A.complement.entry);
				top.queue.add(A.complement);
				topQueue.add(A.complement);
			}

			if(A instanceof Singleton)
			{
				ontology.consistency = false;
				return true;
			}

			HashSet<RoleConcept> leftconnection = new HashSet<RoleConcept>();
			leftconnection.addAll(A.predecessors);
			leftconnection.addAll(A.tempPredecessors);
			for(RoleConcept rc : leftconnection)
			{
				Basic Aprime = rc.concept;
				addSubsumer_duo(Aprime, bot);
			}
			for(Basic Aprime:A.reachableBy)
			{
				addSubsumer_duo(Aprime,bot);
			}

		}

		return true;

	}

	private boolean process_new_edge_duo(Basic A, Role r, Basic B) {
		// TODO Auto-generated method stub

		boolean toprocess = false;

		if(A == null || B == null)
			return toprocess;

		HashSet<Basic> bsubsumers = new HashSet<Basic>();
		bsubsumers.addAll(B.subsumers);
		bsubsumers.addAll(B.tempSubsumers);
		for(Role s : r.subsumers)
		{
			if(s!=r && !s.related && (s.inverse == null ||!s.inverse.related ))
				continue;


			s.addTempRelation(A,B);
			B.addTempPredecessor(s, A);
			for(Basic Bprime: bsubsumers)
			{
				if(getexist(s,Bprime) != null)
				{
					addAll2queue(A,getexist(s,Bprime));
				}
			}

			if(ontology.chains)
				if(A instanceof Singleton && B instanceof Singleton)
				{
					for(Basic Aprime:A.subsumers)
						if(s.inverse!= null && getexist(s.inverse,Aprime) !=null)
							addAll2queue(B,getexist(s.inverse,Aprime));
					for(Basic Aprime:A.tempSubsumers)
						if(s.inverse!= null && getexist(s.inverse,Aprime) !=null)
							addAll2queue(B,getexist(s.inverse,Aprime));

				}

			HashSet<RoleConcept> leftconnection = new HashSet<RoleConcept>();
			leftconnection.addAll(A.predecessors);
			leftconnection.addAll(A.tempPredecessors);
			for(RoleConcept rc : leftconnection)
			{
				Role t = rc.role;
				Basic Aprime = rc.concept;
				HashSet<Role> set = t.RightComposition.get(s);
				if(set != null)
					for(Role u :set)
					{
						if((!u.Relations.containsKey(Aprime) || !u.Relations.get(Aprime).contains(B)) && !u.tempRelations.containsKey(Aprime) || !u.tempRelations.get(Aprime).contains(B))
							process_new_edge_duo(Aprime,u,B);
					}
			}
			for(Role t:s.RightComposition.keySet())
			{
				if(!t.related)
					continue;

				HashSet<Role> set = s.RightComposition.get(t);
				if(set != null)
				{
					for(Role u:set)
					{
						if(!u.related)
							continue;
						HashSet<Basic> bprimes = new HashSet<Basic>();
						if(t.Relations.get(B) != null)
							bprimes.addAll(t.Relations.get(B));
						if(t.tempRelations.get(B) != null)
							bprimes.addAll(t.tempRelations.get(B));
						if(bprimes != null)
							for(Basic Bprime:bprimes)
							{
								if((!u.Relations.containsKey(A) || !u.Relations.get(A).contains(Bprime)) && (!u.tempRelations.containsKey(A) || !u.tempRelations.get(A).contains(Bprime)))
									process_new_edge_duo(A,u,Bprime);
							}
					}
				}
			}
			if(ontology.chains)
				if(A instanceof Singleton)
				{
					for(Role it:ontology.roles.values())
					{
						Role t = it.inverse;
						if(t!=null && t.RightComposition.containsKey(s) && (it.Relations.get(A) != null || it.tempRelations.get(A) != null))
						{
							for(Role u:t.RightComposition.get(s))
							{
								for(Basic Aprime:it.Relations.get(A))
									if(Aprime instanceof Singleton && (!u.Relations.containsKey(Aprime) || !u.Relations.get(Aprime).contains(B)) && (!u.tempRelations.containsKey(Aprime) || !u.tempRelations.get(Aprime).contains(B)))
										process_new_edge_duo(Aprime, u, B);
								for(Basic Aprime:it.tempRelations.get(A))
									if(Aprime instanceof Singleton && (!u.Relations.containsKey(Aprime) || !u.Relations.get(Aprime).contains(B)) && (!u.tempRelations.containsKey(Aprime) || !u.tempRelations.get(Aprime).contains(B)))
										process_new_edge_duo(Aprime, u, B);
							}
						}
					}

					if(B instanceof Singleton && s.inverse!=null)
					{
						HashSet<RoleConcept> rcs = new HashSet<RoleConcept>(B.predecessors);
						rcs.addAll(B.tempPredecessors);
						for(RoleConcept RC:rcs)
						{
							Role t = RC.role;
							Basic Bprime  = RC.concept;

							if(Bprime instanceof Singleton && t.RightComposition.containsKey(s.inverse))
								for(Role u:t.RightComposition.get(s.inverse))
									if((!u.Relations.containsKey(Bprime) || !u.Relations.get(Bprime).contains(A))&&(!u.tempRelations.containsKey(Bprime) || !u.tempRelations.get(Bprime).contains(A)))
										process_new_edge_duo(Bprime, u, A);
						}
					}
				}

		}
		return toprocess;


	}

	private boolean ABox_duo() {
		// TODO Auto-generated method stub
		boolean toprocess = false;
		for(int id:ontology.individualIDs.values())
		{
			Singleton indi = (Singleton) ontology.descriptions.get(id);
			if(!ABox && !indi.active)
				continue;
			if(ontology.consistency == false)
				break;
			if(indi.subsumers.contains(bot) || indi.tempSubsumers.contains(bot))
			{
				ontology.consistency = false;
				break;
			}

			while(indi.queue.size() > 0)
			{
				HashSet<Description> tempindiqueue = new HashSet<Description>(indi.queue);
				indi.queue = new HashSet<Description>();
				for(Description classification:tempindiqueue)
				{
					for(QueueEntry X:classification.Ohat)
					{
						toprocess = process_duo(indi,X)? true:toprocess;
						if(indi.tempSubsumers.contains(bot))
						{
							ontology.consistency = false;
							break;
						}
					}

					for(QueueEntry X:classification.tempOhat)
					{
						toprocess = process_duo(indi,X)? true:toprocess;
						if(indi.tempSubsumers.contains(bot))
						{
							ontology.consistency = false;
							break;
						}
					}
				}

			}
		}
		return toprocess;
	}


	private void postprocessing_duo() {
		// TODO Auto-generated method stub
		for(Basic concept:ontology.originalNamedConcepts)
		{
			if(concept.tempSubsumers.contains(bot))
				;
			else
				concept.tempSubsumers.addAll(top.tempSubsumers);
		}
	}



}
