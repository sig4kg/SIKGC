package eu.trowl.owlapi3.rel.normal.model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;

/*** 
 * The REL internal representation of an ontology. 
 * @author Yuan Ren
 * @version 2013-07-11
 */
public class Ontology {
	/*
	 * @version 2013-07-11
	 * 1. remove simpleExistEntries because now ExistEntries 
	 * use same datatype as Some, and can be maintained in each role;
	 * 2. change allConcepts to be Atomic because they can
	 * 3. separate tBox_Classified and aBox_Classified;
	 * 4. introduce ABox as the flag of ABox reasoning;
	 * only be atomic;
	 * @version 2012-05-18
	 */

	public int basicConceptNum = 0;
	public int permBasicConceptNum = 0;
	public int roleNum = 0;

	// whether the TBox is large
	public boolean largeT = false;

	// whether the ABox is large
	public boolean largeA = false;

	// whether apply disjunction resultion
	public boolean disRes = false;

	// whether the ontology contains non-transitive role chains
	public boolean chains = false;

	// whether the ontology applies NBox
	public boolean NOnto = false;

	// whether the ontology is used for query answering
	public boolean BGP = false;

	// whether the ontology contains meta-modelling
	public boolean MetaOn = false;

	// whether the ontology applies disjointness between mutually exclusive sets
	public boolean disjoint = false;

	// profile types
	public enum Profile {OWL_2_DL, OWL_2_EL, OWL_2_QL, OWL_2_RL};
	// language profile
	public Profile profile = Profile.OWL_2_DL;

	public HashMap<OWLClassExpression, Integer> classIDs = new HashMap<OWLClassExpression, Integer>();
	public HashMap<Integer, Description> descriptions = new HashMap<Integer, Description>();

	public HashMap<OWLObjectPropertyExpression, Integer> roleIDs = new HashMap<OWLObjectPropertyExpression, Integer>();
	public HashMap<Integer, Role> roles = new HashMap<Integer, Role>();

	public HashMap<OWLIndividual, Integer> individualIDs = new HashMap<OWLIndividual, Integer>();

	public HashSet<Atomic> originalNamedConcepts = new HashSet<Atomic>();

	public boolean consistency = true;

	public boolean tBox_Classified = false;
	public boolean aBox_Classified = false;

	//	public void write(BufferedWriter bw) {
	//		// TODO Auto-generated method stub
	//		Atomic bot = (Atomic) descriptions.get(0);
	//		try {
	//			bw.write("classes as follows:\n");
	//			for(int i = 1;i<classNum;i++)
	//			{
	//				if(descriptions.get(i) instanceof Singleton)
	//					continue;
	//				Atomic concept = (Atomic) descriptions.get(i);
	//				if(!concept.original)
	//					continue;
	//				bw.write(i+" "+concept.uri.getFragment()+": S(");
	//				if(concept.subsumers.contains(bot))
	//				{
	//					bw.write("Nothing, ");
	//					for(Basic subsumer:allconcepts)
	//					{
	//						if(subsumer instanceof Atomic && subsumer.original)
	//						{
	//							bw.write(((Atomic)subsumer).uri.getFragment()+", ");
	//						}
	//					}
	//				}
	//				else
	//				{
	//				for(Basic subsumer:concept.subsumers)
	//				{
	//					if(subsumer instanceof Atomic && subsumer.original)
	//					{
	//						bw.write(((Atomic)subsumer).uri.getFragment()+", ");
	//					}
	//					
	//				}
	//				}
	//				bw.write(")\n");
	//			}
	//			bw.write("\n");
	//			bw.write("roles as follows:\n");
	//			for(int i = 0;i<roleNum;i++)
	//			{
	//				Role role = roles.get(i);
	//				if(!role.original)
	//					continue;
	//				bw.write(i+" "+role.uri.getFragment()+": S(");
	//				for(Role subsumer:role.subsumers)
	//				{
	//					if(subsumer.original)
	//					{
	//						bw.write(subsumer.uri.getFragment()+", ");
	//					}
	//				}
	//				bw.write(")\n"+" R(");
	//				for(Entry<Basic, HashSet<Basic>> relation:role.Relations.entrySet())
	//				{
	//					Basic classA = relation.getKey();
	//					if(!classA.original || classA instanceof Singleton)
	//						continue;
	//					for(Basic classB:relation.getValue())
	//					{
	//						if(classB.original && classB instanceof Atomic)
	//							bw.write("("+((Atomic)classA).uri.getFragment()+", "+((Atomic)classB).uri.getFragment()+"), ");
	//					}
	//				}
	//				bw.write(")\n");
	//			}
	//			bw.write("\n");
	//		} catch (IOException e) {
	//			// TODO Auto-generated catch block
	//			e.printStackTrace();
	//		}
	//	}

	// A native method to count the number of atomic subsumptions without using OWLAPI 
	public int countsubsumers() {
		// TODO Auto-generated method stub
		int num = 0;
		Atomic bot = (Atomic) descriptions.get(0);
		int allnum = 0;
		allnum = originalNamedConcepts.size()+1;

		for(int i = 1;i<basicConceptNum;i++)
		{
			Basic concept = (Basic) descriptions.get(i);
			if(!concept.original || concept instanceof Singleton)
				continue;
			if(concept.subsumers.contains(bot))
			{
				num+=allnum;
				continue;
			}
			for(Basic subsumer:concept.subsumers)
				if(subsumer.original && subsumer instanceof Atomic)
					num++;
		}
		System.out.println(num);
		return num;

	}


	// A native method to print the unsatisfiable concepts without using OWLAPI
	public void getunsatisfiableconcepts()
	{
		int num = 0;
		Atomic bot = (Atomic) descriptions.get(0);
		ArrayList<IRI> unsatisfiables = new ArrayList<IRI>();
		for(int i = 2;i<basicConceptNum;i++)
		{
			Atomic concept = (Atomic) descriptions.get(i);
			if(!concept.original)
				continue;
			if(concept.subsumers.contains(bot))
			{
				num++;
				unsatisfiables.add(concept.uri);
			}
		}
		System.out.println("There are "+num+" unsatisfiable concepts");
		for(IRI uri:unsatisfiables)
			System.out.println(uri.getFragment());
	}

}
