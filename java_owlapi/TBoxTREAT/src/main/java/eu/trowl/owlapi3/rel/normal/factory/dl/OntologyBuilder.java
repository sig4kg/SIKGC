package eu.trowl.owlapi3.rel.normal.factory.dl;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassAssertionAxiom;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataAllValuesFrom;
import org.semanticweb.owlapi.model.OWLDataComplementOf;
import org.semanticweb.owlapi.model.OWLDataExactCardinality;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLDataHasValue;
import org.semanticweb.owlapi.model.OWLDataIntersectionOf;
import org.semanticweb.owlapi.model.OWLDataMaxCardinality;
import org.semanticweb.owlapi.model.OWLDataMinCardinality;
import org.semanticweb.owlapi.model.OWLDataOneOf;
import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLDataPropertyAssertionAxiom;
import org.semanticweb.owlapi.model.OWLDataPropertyDomainAxiom;
import org.semanticweb.owlapi.model.OWLDataPropertyExpression;
import org.semanticweb.owlapi.model.OWLDataPropertyRangeAxiom;
import org.semanticweb.owlapi.model.OWLDataRange;
import org.semanticweb.owlapi.model.OWLDataSomeValuesFrom;
import org.semanticweb.owlapi.model.OWLDataUnionOf;
import org.semanticweb.owlapi.model.OWLDatatype;
import org.semanticweb.owlapi.model.OWLDatatypeRestriction;
import org.semanticweb.owlapi.model.OWLDifferentIndividualsAxiom;
import org.semanticweb.owlapi.model.OWLDisjointClassesAxiom;
import org.semanticweb.owlapi.model.OWLDisjointObjectPropertiesAxiom;
import org.semanticweb.owlapi.model.OWLEquivalentClassesAxiom;
import org.semanticweb.owlapi.model.OWLEquivalentDataPropertiesAxiom;
import org.semanticweb.owlapi.model.OWLEquivalentObjectPropertiesAxiom;
import org.semanticweb.owlapi.model.OWLFacetRestriction;
import org.semanticweb.owlapi.model.OWLFunctionalDataPropertyAxiom;
import org.semanticweb.owlapi.model.OWLFunctionalObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLInverseFunctionalObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLInverseObjectPropertiesAxiom;
import org.semanticweb.owlapi.model.OWLLiteral;
import org.semanticweb.owlapi.model.OWLLogicalAxiom;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectAllValuesFrom;
import org.semanticweb.owlapi.model.OWLObjectComplementOf;
import org.semanticweb.owlapi.model.OWLObjectExactCardinality;
import org.semanticweb.owlapi.model.OWLObjectHasValue;
import org.semanticweb.owlapi.model.OWLObjectIntersectionOf;
import org.semanticweb.owlapi.model.OWLObjectInverseOf;
import org.semanticweb.owlapi.model.OWLObjectMaxCardinality;
import org.semanticweb.owlapi.model.OWLObjectMinCardinality;
import org.semanticweb.owlapi.model.OWLObjectOneOf;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLObjectPropertyAssertionAxiom;
import org.semanticweb.owlapi.model.OWLObjectPropertyDomainAxiom;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;
import org.semanticweb.owlapi.model.OWLObjectPropertyRangeAxiom;
import org.semanticweb.owlapi.model.OWLObjectSomeValuesFrom;
import org.semanticweb.owlapi.model.OWLObjectUnionOf;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLReflexiveObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLSameIndividualAxiom;
import org.semanticweb.owlapi.model.OWLSubClassOfAxiom;
import org.semanticweb.owlapi.model.OWLSubDataPropertyOfAxiom;
import org.semanticweb.owlapi.model.OWLSubObjectPropertyOfAxiom;
import org.semanticweb.owlapi.model.OWLSubPropertyChainOfAxiom;
import org.semanticweb.owlapi.model.OWLSymmetricObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLTransitiveObjectPropertyAxiom;

import eu.trowl.owlapi3.rel.normal.model.And;
import eu.trowl.owlapi3.rel.normal.model.Atomic;
import eu.trowl.owlapi3.rel.normal.model.Basic;
import eu.trowl.owlapi3.rel.normal.model.CardinAtomic;
import eu.trowl.owlapi3.rel.normal.model.CardinalityEntry;
import eu.trowl.owlapi3.rel.normal.model.Description;
import eu.trowl.owlapi3.rel.normal.model.Implies;
import eu.trowl.owlapi3.rel.normal.model.Ontology;
import eu.trowl.owlapi3.rel.normal.model.Ontology.Profile;
import eu.trowl.owlapi3.rel.normal.model.QueueEntry;
import eu.trowl.owlapi3.rel.normal.model.Role;
import eu.trowl.owlapi3.rel.normal.model.Singleton;
import eu.trowl.owlapi3.rel.normal.model.Some;
import eu.trowl.owlapi3.rel.util.RELReasonerConfiguration;


/***
 * This class is the builder of the REL reasoner.
 * It construct the internal representation of the ontology from the input OWLOntology object.
 * @author Yuan Ren
 * @version 2014-03-13
 */
public class OntologyBuilder extends OWL2DLAxiomVisitor {
	/*
	 * @version 2014-03-13
	 * 1. add additional condition in name initialisation to remove redundant names
	 * @version 2013-10-09
	 * 1. add nominal to cardinality restriction transformation (all2cardin);
	 * 2. add disjunctSubsumption to make sure subsumptions involving
	 * disjuctions can be propagated;
	 * 3. add original subsumees in approximate() method;
	 * 4. add existential disjunction resolution in approximate(), together
	 * with (3);
	 * 5. add approximation to anonymous individuals;
	 * @version 2013-09-30
	 * 1. role.related added to ONLY approximation;
	 * 2. revised getNNF(\neg {a,b,c...})
	 * @version 2013-09-29
	 * 1. all2some enabled for all ontologies! need to find out when it does not pay-off!
	 * @version 2013-09-18
	 * 1. add datatype disjointness support;
	 * @version 2013-08-04
	 * 1. Add float datatype support;
	 * 2. Change cardinality atomic support condition to cardin <= 3;
	 * @version 2013-07-11
	 * 1. Change AllConcepts to be Atomic;
	 * 2. Add role.some updates when approximating Some;
	 * 3. change ERestrictions to Somes;
	 * 4. add additional auto-configuration trigger for set disjointness and set union;
	 * 5. separating individual singleton and data value singletons in getIndividual();
	 * 6. add normalised some into role.somes;
	 * 7. update initialise(Basic, Role, Basic);
	 * 8. remove the simpleExistEntries clean in clean();
	 * 9. always add new some into role.somes when created;
	 * @version 2013-06-26
	 * 1. IRIs for approximated objects are removed;
	 * 2. inverse relations for datatypes are removed;
	 * 3. fixed a bug on superfalous role id in role chain;
	 * @version 2013-06-12
	 * 1. add condition on constant inequivalence to deal with large number of data values;
	 * @version 2013-05-21
	 * 1. added MetaOn support to convert \some r.A \sub B => A \sub \forall r^-.B; enabled when MetaOn = true;
	 * 2. added disjoint support to set disjointness, enabled when disjoint = true  and there is diffIndis;
	 * 3. added union support to convert \some r.(A \or B) => \some r.A \or \some r.B; enabled when disjoint = true;
	 * @version 2012-05-18
	 */


	protected Set<OWLOntology> ontologies;	// input ontologies

	protected Ontology relOntology;	// internal ontology

	public HashMap<OWLClassExpression, Integer> classIDs;
	public HashMap<Integer, Description> descriptions;
	protected HashSet<Atomic> originalNamedConcepts;	// internal objects of all original name concepts
	protected HashMap<Atomic, HashMap<Integer, Atomic>> CardinalityTable = new HashMap<Atomic, HashMap<Integer, Atomic>>();
	protected HashMap<Basic, HashSet<Singleton>> setConcepts = new HashMap<Basic, HashSet<Singleton>>();	
	protected HashSet<OWLObjectSomeValuesFrom> nominalFillerMins = new HashSet<OWLObjectSomeValuesFrom>();
	private final Map<Description, Atomic> normalisationNames = new HashMap<Description, Atomic>();
	protected int basicID = 0;
	protected int nonBasicID = -2;
	protected int implyID;

	public HashMap<OWLObjectPropertyExpression, Integer> propertyIDs;
	public HashMap<Integer, Role> roles;
	private HashMap<ArrayList<Role>, Role> chainNames = new HashMap<ArrayList<Role>, Role>();
	HashSet<Role> chainRoles = new HashSet<Role>();
	protected int roleID = 0;

	int chain = 0;
	int trans = 0;

	protected static final String INDI_PREFIX = "RELAPPROX#RELAPPROXI";
	protected HashMap<OWLIndividual, Integer> individualIDs;
	protected HashSet<OWLIndividual> constants = new HashSet<OWLIndividual>();


	public Atomic top = null;
	public Atomic bot = null;

	public OWLDataFactory factory = null;

	boolean containDiffIndisAxiom = false;

	public OntologyBuilder(){
		super(true);
	
	}


	/**
	 * This method constructs the ontology builder.
	 * @param ontologies: the input ontologies.
	 * @param manager: the manager of the input ontologies.
	 * @param RELOntology: the internal representation of the ontologies.
	 */
	public OntologyBuilder(Set<OWLOntology> ontologies, OWLOntologyManager manager, Ontology RELOntology) {
		// TODO Auto-generated constructor stub
		super(true);

		this.ontologies = ontologies;
		factory = manager.getOWLDataFactory();

		relOntology = RELOntology;
		classIDs = relOntology.classIDs;
		descriptions = relOntology.descriptions;
		originalNamedConcepts = relOntology.originalNamedConcepts;
		propertyIDs = relOntology.roleIDs;
		roles = relOntology.roles;

		OWLClass thing = factory.getOWLThing();
		OWLClass nothing = factory.getOWLNothing();

		top = new Atomic(thing);
		top.id = 1;
		top.original = true;
		bot = new Atomic(nothing);
		bot.id = 0;
		bot.original = true;

		addClassID(nothing, 0);
		addClassID(thing, 1);
		originalNamedConcepts.add(top);

		basicID = 2;

		descriptions.put(0, bot);
		imply(bot);
		descriptions.put(1, top);
		imply(top);

		initialise();
	}


	/**
	 * This method provides the internal representation of an OWLClassExpression.
	 * Approximation and normalisation are performed accordingly during the process.
	 * If the concept has already been approximated, it will return the previously result.
	 * @param concept: the input OWLClassExpression.
	 * @return the internal representation of the input OWLClassExpression.
	 */
	protected Description approx(OWLClassExpression concept) {
		// TODO Auto-generated method stub
		// Note that in the current system, datatypes are also treated as class expressions.

		Description approx = null;

		if(classIDs.get(concept) != null)
			approx = descriptions.get(classIDs.get(concept));
		else if(concept instanceof OWLObjectComplementOf)
		{
			OWLObjectComplementOf comp = (OWLObjectComplementOf) concept;
			OWLClassExpression des = comp.getOperand();
			// in NNF only Basic has Complement
			Basic compApprox = (Basic) approx(des);

			approx = compApprox.complement;
			if(approx == null)
			{
				Atomic atomic = new Atomic();
				atomic.id = basicID++;
				atomic.original = false;
				addClassID(concept, atomic.id);
				descriptions.put(atomic.id, atomic);
				imply(atomic);
				atomic.complement = compApprox;
				compApprox.complement = atomic;
				approx = atomic;
			}
		}
		else if(concept instanceof OWLObjectIntersectionOf)
		{
			OWLObjectIntersectionOf intersection = (OWLObjectIntersectionOf) concept;
			HashSet<Description> conjunctApproxs = new HashSet<Description>();
			for(OWLClassExpression des : intersection.getOperands())
				conjunctApproxs.add(approx(des));
			approx = new And(conjunctApproxs);
			approx.id = nonBasicID--;
			addClassID(concept, approx.id);
			descriptions.put(approx.id, approx);
		}
		else if(concept instanceof OWLObjectUnionOf)
		{
			// union will be approximated as an atomic concept
			Atomic atomic = new Atomic();
			atomic.id = basicID++;
			atomic.original = false;
			addClassID(concept, atomic.id);
			descriptions.put(atomic.id, atomic);
			imply(atomic);

			// We first need to approximate the complement of the union.
			// Since the approximation of the complement is likely to be an intersection,
			// we also need to assign an atomic name to the approximation,
			// and then establish the complement relations between the two atomic concepts.
			OWLObjectUnionOf union = (OWLObjectUnionOf) concept;
			OWLClassExpression comp = getNNF(factory.getOWLObjectComplementOf(union));
			Description compApprox = approx(comp);

			Atomic compAtomic = new Atomic();
			compAtomic.id = basicID++;
			compAtomic.original = false;
			addClassID(comp, compAtomic.id);
			descriptions.put(compAtomic.id, compAtomic);
			imply(compAtomic);
			normalise(compAtomic, compApprox);
			normalise(compApprox, compAtomic);

			atomic.complement = compAtomic;
			compAtomic.complement = atomic;

			approx = atomic;

			// Disjunct subsumption approximation:
			// If A = approx(B1 \or B2 \or ... \or Bn),
			// then approx(Bi) \sub A
			// We do this here because it is not necessarily inferrable with REL
			// Especially when not all the complements of basic concepts are generated.
			for(OWLClassExpression exp:union.getOperands())
				normalise(approx(exp),atomic);
		}
		else if(concept instanceof OWLObjectSomeValuesFrom)
		{
			OWLObjectSomeValuesFrom some = (OWLObjectSomeValuesFrom) concept;
			OWLObjectPropertyExpression property = some.getProperty();
			Role role = approx(property);
			Some someApprox = new Some(role, approx(some.getFiller()));
			approx = someApprox;
			approx.id = nonBasicID--;
			if(someApprox.concept instanceof Basic)
				someApprox.role.somes.put((Basic) someApprox.concept, someApprox);
			addClassID(concept, approx.id);
			descriptions.put(approx.id, approx);
		}
		else if(concept instanceof OWLObjectAllValuesFrom)
		{
			// universal restriction will be approximated as an atomic concept
			Atomic atomic = new Atomic();
			atomic.id = basicID++;
			atomic.original = false;
			addClassID(concept, atomic.id);
			descriptions.put(atomic.id, atomic);
			imply(atomic);

			// We first need to approximate the complement of a universal restriction
			OWLObjectAllValuesFrom all = (OWLObjectAllValuesFrom) concept;
			OWLClassExpression complement = getNNF(factory.getOWLObjectComplementOf(all));

			// Then we assign an atomic name to the approximation,
			// and establish the complement realtion between the atomic concepts.

			Atomic complementAtomic = new Atomic();
			complementAtomic.id = basicID++;
			complementAtomic.original = false;
			imply(complementAtomic);

			// This is needed when we want to make sure the filler is approximated as a named concept.
			approx(all.getFiller());
			Some complementApprox = (Some) approx(complement);
			addClassID(complement, complementAtomic.id);
			descriptions.put(complementAtomic.id, complementAtomic);

			normalise(complementAtomic, complementApprox);
			normalise(complementApprox, complementAtomic);
			complementApprox.role.related = true;

			if(complementApprox.concept instanceof Basic)
				complementApprox.role.somes.put((Basic) complementApprox.concept,complementApprox);

			atomic.complement = complementAtomic;
			complementAtomic.complement = atomic;
			approx = atomic;

			atomic.onlyLink = complementApprox;

			// for BGP, add further approximation of ontology:
			// If X = \forall r.{a}
			// and a:C in the ontology
			// then X \sub <=1 r.C
			if(relOntology.BGP)
				if(all.getFiller() instanceof OWLObjectOneOf)
				{
					OWLObjectOneOf oneof = (OWLObjectOneOf) all.getFiller();
					if(oneof.getIndividuals().size() == 1)
					{
						OWLIndividual indi = oneof.getIndividuals().iterator().next();
						// modified by Sylvia Wang
						// for(OWLClassExpression cls:indi.getTypes(ontologies))
						for(OWLClassExpression cls:indi.getNestedClassExpressions())
						{
							OWLObjectMaxCardinality card = factory.getOWLObjectMaxCardinality(1, all.getProperty(), cls);
							Description cardesc = approx(card);
							normalise(approx, cardesc);
							normalise(cardesc, approx);
						}
					}
				}


			//from universal restriction to existential restriction
			// X = \forall r.C
			// =>
			// \exists r^-.approx(X) \sub C
			Role invr = approx(all.getProperty()).inverse;
			if(invr != null)
			{
				Some some = invr.somes.get(atomic);
				if(some == null)
				{
					some = new Some(invr, atomic);
					some.id = nonBasicID;
					nonBasicID--;
					descriptions.put(some.id, some);
					invr.somes.put(atomic, some);			
				}
				some.role.related = true;
				normalise(some, approx(all.getFiller()));
			}

			// from universal restriction to cardinality restriction
			// This is a special case for the BGP approximation shown above
			if(all.getFiller() instanceof OWLObjectOneOf)
			{
				OWLObjectOneOf oneof = (OWLObjectOneOf) all.getFiller();
				normalise (approx, approx(factory.getOWLObjectMaxCardinality(oneof.getIndividuals().size(), all.getProperty(),factory.getOWLThing())));
			}
		}

		else if(concept instanceof OWLObjectMinCardinality)
		{
			OWLObjectMinCardinality min = (OWLObjectMinCardinality) concept;
			int n = min.getCardinality();
			OWLObjectPropertyExpression property = min.getProperty();
			Role role = approx(property);
			OWLClassExpression filler = min.getFiller();
			if(filler instanceof OWLObjectOneOf)
				nominalFillerMins.add(factory.getOWLObjectSomeValuesFrom(property, filler));
			Description fillerApprox = approx(filler);
			if(!(fillerApprox instanceof Atomic))
			{
				OWLClassExpression fillerComplement = getNNF(factory.getOWLObjectComplementOf(filler));
				Atomic fillerComplementApprox = (Atomic) approx(fillerComplement);
				fillerApprox = fillerComplementApprox.complement;
			}
			Atomic fillerAtomic = (Atomic) fillerApprox;
			
			// we actually approximate >=n R.C with \some R. C_n
			// The approximated filler C_n is an CardinAtomic
			// In order to make sure for each C and each n we have a unique C_n
			// We maintain them in the CardinalityTable
			// Particularly, CardinalityTable.get(A).get(n) will be A_n.
			// Note that when n = 1, A_n = A.
			if(CardinalityTable.get(fillerAtomic) == null)
			{
				HashMap<Integer, Atomic> fillerapproxentry = new HashMap<Integer, Atomic>();
				fillerapproxentry.put(1, fillerAtomic);
				CardinalityTable.put(fillerAtomic, fillerapproxentry);
			}
			Atomic fillerCardinAtomic = CardinalityTable.get(fillerAtomic).get(n);
			if(fillerCardinAtomic == null)
			{
				CardinAtomic newcardinfiller = new CardinAtomic();
				newcardinfiller.id = basicID++;
				newcardinfiller.original = false;
				newcardinfiller.base = fillerAtomic;
				newcardinfiller.minCardin = n;
				fillerCardinAtomic = newcardinfiller;
				CardinalityTable.get(fillerAtomic).put(n, fillerCardinAtomic);
				descriptions.put(fillerCardinAtomic.id, fillerCardinAtomic);
				imply(fillerCardinAtomic);		
			}
			approx = new Some(role,fillerCardinAtomic);
			approx.id = nonBasicID--;
			if(fillerCardinAtomic instanceof Basic)
				role.somes.put(fillerCardinAtomic, (Some) approx);
			addClassID(concept, approx.id);
			descriptions.put(approx.id, approx);
		}
		else if(concept instanceof OWLObjectMaxCardinality)
		{
			// Similar as before, we approximate max cardinality restriction with a atomic concept
			// And we approx its complement with an atomic concept as well
			
			Atomic atomic = new Atomic();
			atomic.id = basicID++;
			atomic.original = false;
			addClassID(concept, atomic.id);
			descriptions.put(atomic.id, atomic);
			imply(atomic);

			OWLObjectMaxCardinality max = (OWLObjectMaxCardinality) concept;
			OWLClassExpression complement = getNNF(factory.getOWLObjectComplementOf(max));
			Some complementapprox = (Some) approx(complement);
			
			Atomic complementAtomic = new Atomic();
			complementAtomic.id = basicID++;
			complementAtomic.original = false;
			addClassID(complement, complementAtomic.id);
			descriptions.put(complementAtomic.id, complementAtomic);
			imply(complementAtomic);
			
			if(complementapprox.concept instanceof Basic)
				complementapprox.role.somes.put((Basic) complementapprox.concept,complementapprox);

			atomic.complement = complementAtomic;
			complementAtomic.complement = atomic;


			normalise(complementAtomic,complementapprox);
			normalise(complementapprox,complementAtomic);

			approx = atomic;
		}

		else if(concept instanceof OWLObjectOneOf)
		{
			// We approximate OWLObjectOneOf as a union of singleton concepts
			OWLObjectOneOf oneof = (OWLObjectOneOf)concept;
			Set<OWLIndividual> indis= oneof.getIndividuals();
			Set<OWLObjectOneOf> concepts = new HashSet<OWLObjectOneOf>();
			HashSet<Singleton> singletons = new HashSet<Singleton>();
			for(OWLIndividual individual:indis)
			{
				OWLObjectOneOf singleton = factory.getOWLObjectOneOf(individual);
				concepts.add(singleton);
				singletons.add(approx(individual));
			}
			if(indis.size() == 0)
				approx = bot;
			else if(indis.size() == 1)
			{
				OWLObjectOneOf singleton = concepts.iterator().next();
				approx = approx(singleton.getIndividuals().iterator().next());
			}
			else
			{
				OWLObjectUnionOf union = factory.getOWLObjectUnionOf(concepts);
				approx = approx(union);
			}
			
			// We also map the approximation to the set of its singleton elements
			if(approx != bot)
				setConcepts.put((Basic) approx, singletons);
		}
		else
		{
			// for any other type of concepts, we simply approximate with a named concept
			Atomic atomic = new Atomic();
			atomic.id = basicID++;
			atomic.original = false;
			addClassID(concept, atomic.id);
			descriptions.put(atomic.id, atomic);
			imply(atomic);
			approx = atomic;
		}

		// For small ontology, we also approximate the complement of a concept
		// If it has not aready been approximated
		if(!relOntology.largeT && approx instanceof Basic)
		{
			Basic basic = (Basic) approx;
			if(basic.complement == null)
			{
				// double
				Atomic nNCA = new Atomic();
				nNCA.id = basicID++;
				nNCA.original = false;
				addClassID(factory.getOWLObjectComplementOf(concept), nNCA.id);
				descriptions.put(nNCA.id, nNCA);
				imply(nNCA);

				basic.complement = nNCA;
				nNCA.complement = basic;
			}

		}
		return approx;
	}

	/**
	 * This method provides the internal representation of an OWLObjectPropertyExpression.
	 * Approximation and normalisation are performed accordingly during the procedure.
	 * For each property expression, a unique internal representation will be produced.
	 * @param property: the input object property expression.
	 * @return the internal representation of the input expression.
	 */
	protected Role approx(OWLObjectPropertyExpression property){

		Role approx = null;
		if(propertyIDs.get(property)!=null)
			approx = roles.get(propertyIDs.get(property));
		else if(property instanceof OWLObjectProperty)
		{
			OWLObjectProperty atomicrole = (OWLObjectProperty) property;
			approx = new Role(atomicrole, roleID++);
			propertyIDs.put(property, approx.id);
			roles.put(approx.id, approx);
		} 
		else if(property instanceof OWLObjectInverseOf) {
			OWLObjectInverseOf inverse = (OWLObjectInverseOf) property;
			Role inverseApprox = approx(inverse.getInverse());
			approx = inverseApprox.inverse;
			if(approx == null)
			{
				approx = new Role(roleID++);
				approx.original = false;
				propertyIDs.put(property, approx.id);
				roles.put(approx.id, approx);
	
				approx.inverse = inverseApprox;
				inverseApprox.inverse = approx;
			}
		}
		return approx;
	}

	/**
	 * This method provides the internal representation of an OWLDataPropertyExpression.
	 * Approximation and normalisation are performed accordingly during the procedure.
	 * For each property expression, a unique internal representation will be produced.
	 * @param property: the input data property expression.
	 * @return the internal representation of the input expression.
	 */
	protected Role approx(OWLDataPropertyExpression property)
	{
		// Note that in the current system, datatype property expressions are treated as 
		// object property expressions.

		Role RN = null;
		if(property instanceof OWLDataProperty)
		{
			OWLObjectProperty oproperty = factory.getOWLObjectProperty(((OWLDataProperty) property).getIRI());
			RN = roles.get(propertyIDs.get(oproperty));
		}
		return RN;
	
	}


	/**
	 * This method provides the internal representation of an OWLIndividual.
	 * Approximation and normalisation are performed accordingly during the procedure.
	 * For each individual, a unique internal representation will be produced.
	 * @param individual: the individual that will be approximated.
	 * @return
	 */
	protected Singleton approx(OWLIndividual individual){
		
		// Note that in the current system, data values are treated as individuals.
		// Also, we use singleton {a} to represent an individual a.
		// So that individuals are treated as concepts.
		// And ABox axioms are treated as TBox axioms.

		Singleton approx = null;
		if(individualIDs.get(individual)!=null)
			approx = (Singleton) descriptions.get(individualIDs.get(individual));
		else
		{
			approx = new Singleton(individual);
			
			// for some reason we consider non-float data value as non-basic concepts.
			// All other individuals/data values are treated as basic concepts.
			// A non-basic concept will never be used as a subject in reasoning.
			if(floats.containsValue(individual))
				approx.id = basicID++;
			else if(constants.contains(individual))
			{
				approx.id = nonBasicID--;
				approx.subsumers.add(top);
			}
			else
			{
				approx.id = basicID++;
			}
			approx.original = false;
			imply(approx);
			individualIDs.put(individual, approx.id);
			descriptions.put(approx.id, approx);
		}
		return approx;
	}

	/**
	 * This method performs some post-processing after the ontology has been approximated.
	 */
	protected void postBuildProcessing() {
		// TODO Auto-generated method stub
		
		// One of the undocumented rules.
		// Only applicable when the ontology does not have a large ABox
		// If A \sub <=1 r.C
		// A \sub \some r.B
		// B \sub C
		// =>
		// A \sub \only r.B
		if(!relOntology.largeA)
		{
			ArrayList<OWLClassExpression> copies = new ArrayList<OWLClassExpression>(classIDs.keySet());

			for(OWLClassExpression desc:copies)
			{
				if(desc instanceof OWLObjectMaxCardinality)
				{
					OWLObjectMaxCardinality max = (OWLObjectMaxCardinality) desc;
					if(max.getCardinality() == 1)
					{
						Basic Y = (Basic) approx(max);
						Role r = approx(max.getProperty());
						Basic C = (Basic) approx(max.getFiller());
						for(int id = 1;id<basicID;id++)
						{
							Description desc2 = descriptions.get(id);
							if(originalNamedConcepts.contains(desc2) || desc2 instanceof Singleton)
							{
								Basic A = (Basic) desc2;
								if(A.Ohat.contains(Y.entry) || top.Ohat.contains(Y.entry))
								{
									HashSet<Description> descs = new HashSet<Description>();
									for(QueueEntry entry:A.Ohat)
									{
										if(entry instanceof Some)
										{
											Some RB = (Some)entry;
											if(RB.role == r && RB.concept != C && (RB.concept.Ohat.contains(C.entry) || C.id == 1))
											{
												if(RB.concept instanceof Singleton)
												{
													OWLIndividual indi = factory.getOWLNamedIndividual(((Singleton)RB.concept).uri);
													descs.add(approx(getNNF(factory.getOWLObjectAllValuesFrom(factory.getOWLObjectProperty(r.uri), factory.getOWLObjectOneOf(indi)))));
												}
												else
													for(OWLClassExpression Bdesc:classIDs.keySet())
													{
														if(classIDs.get(Bdesc) == RB.concept.id)
														{
															descs.add(approx(getNNF(factory.getOWLObjectAllValuesFrom(factory.getOWLObjectProperty(r.uri), Bdesc))));
															break;
														}
													}
											}
										}
									}
									for(Description Xs:descs)
										normalise(A, Xs);
								}
							}
						}
					}

				}
			}
		}

		// Check if the ontology contains non-transitive role-chains
		if(chain > trans)
		{
			relOntology.chains = true;
			for(Role role:chainRoles)
				role.related = true;
		}

		// This part estalishes the subsumptions between cardinality atomics of the same concept.
		// More precisely, if C_n \sub C_m if n >= m.
		for(Entry<Atomic, HashMap<Integer, Atomic>> entry:CardinalityTable.entrySet())
		{
			Atomic filler = entry.getKey();
			HashMap<Integer, Atomic> cardins = entry.getValue();
			CardinalityEntry[] number = new CardinalityEntry[cardins.size()];
			int size = 0;
			for(int n:cardins.keySet())
			{
				int i,j;
				for(i = 0;i < size;i++)
				{
					if(number[i].n < n)
						break;
				}
				for(j = size;j>i;j--)
				{
					number[j] = number[j-1];
				}
				CardinalityEntry newentry = new CardinalityEntry(cardins.get(n), n);
				number[i] = newentry;
				size++;
			}
			filler.cardins = number;
			for(int i = 0;i<size-1;i++)
			{
				normalise(number[i].basen, number[i+1].basen);
			}
		}

		// all constants are different individuals
		if(constants.size() > 0 && constants.size() < 1000)
		{
			OWLDifferentIndividualsAxiom axiom = factory.getOWLDifferentIndividualsAxiom(constants);
			visit(axiom);
		}

		// initialise types of float constant values
		for(Entry<Float, OWLIndividual> entry:floats.entrySet())
		{
			float value = entry.getKey();
			Singleton indi = approx(entry.getValue());
			initialise(indi, (Basic) approx(factory.getOWLClass(IRI.create("http://www.w3.org/2001/XMLSchema#float"))));
			for(float range:minExclusives.keySet())
				if(range<value)
					initialise(indi,(Basic) approx(minExclusives.get(range)));
			for(float range:minInclusives.keySet())
				if(range <= value)
					initialise(indi,(Basic) approx(minInclusives.get(range)));
			for(float range:maxExclusives.keySet())
				if(range > value)
					initialise(indi,(Basic) approx(maxExclusives.get(range)));
			for(float range:maxInclusives.keySet())
				if(range >= value)
					initialise(indi,(Basic) approx(maxInclusives.get(range)));
		}

		// initialise subsumption and disjointness between intervals
		for(float M:maxExclusives.keySet())
		{
			for(float N:maxExclusives.keySet())
				if(M <= N)
					normalise(approx(maxExclusives.get(M)),approx(maxExclusives.get(N)));
			for(float N:maxInclusives.keySet())
				if(M <= N)
					normalise(approx(maxExclusives.get(M)),approx(maxInclusives.get(N)));
			for(float N:minExclusives.keySet())
				if(M <= N)
					visit(factory.getOWLDisjointClassesAxiom(maxExclusives.get(M), minExclusives.get(N)));
			for(float N:minInclusives.keySet())
				if(M <= N)
					visit(factory.getOWLDisjointClassesAxiom(maxExclusives.get(M), minInclusives.get(N)));
		}
		for(float M:maxInclusives.keySet())
		{
			for(float N:maxInclusives.keySet())
				if(M <= N)
					normalise(approx(maxInclusives.get(M)),approx(maxInclusives.get(N)));
			for(float N:maxExclusives.keySet())
				if(M < N)
					normalise(approx(maxInclusives.get(M)),approx(maxExclusives.get(N)));
			for(float N:minExclusives.keySet())
				if(M <= N)
					visit(factory.getOWLDisjointClassesAxiom(maxInclusives.get(M), minExclusives.get(N)));
			for(float N:minInclusives.keySet())
				if(M < N)
					visit(factory.getOWLDisjointClassesAxiom(maxInclusives.get(M), minInclusives.get(N)));
		}
		for(float N:minInclusives.keySet())
		{
			for(float M:minInclusives.keySet())
				if(M <= N)
					normalise(approx(minInclusives.get(N)),approx(minInclusives.get(M)));
			for(float M:minExclusives.keySet())
				if(M < N)
					normalise(approx(minInclusives.get(N)),approx(minExclusives.get(M)));
		}
		for(float N:minExclusives.keySet())
		{
			for(float M:minInclusives.keySet())
				if(M <= N)
					normalise(approx(minExclusives.get(N)),approx(minInclusives.get(M)));
			for(float M:minExclusives.keySet())
				if(M <= N)
					normalise(approx(minExclusives.get(N)),approx(minExclusives.get(M)));
		}

		// initialise disjointness between set concepts
		if(containDiffIndisAxiom && (relOntology.disjoint|| relOntology.originalNamedConcepts.size() > 85000))
		{
			ArrayList<Basic> keys = new ArrayList<Basic>(setConcepts.keySet());

			for(int i = 0;i<keys.size()-1;i++)
			{
				Basic key1 = keys.get(i);
				for(int j=i+1;j<keys.size();j++)
				{
					Basic key2 = keys.get(j);
					// comparesets

					boolean dis = true;
					for(Singleton indi1:setConcepts.get(key1))
					{
						if(!indi1.differentIndividuals.containsAll(setConcepts.get(key2)))
						{
							dis = false;
							break;
						}
					}

					if(dis)
					{
						if(key2.complement != null)
							normalise(key1,key2.complement);
						if(key1.complement != null)
							normalise(key2,key1.complement);
					}
				}
			}
		}

		// deal with set unions.
		// The basic idea is:
		// \some r.{a,b,...} \sub \some r.{a} \or \some r.{b} \or ...
		// We apply this when all the \some r.{a}, \some r.{b}, ... occur in the ontology.
		if(relOntology.disjoint || relOntology.originalNamedConcepts.size() > 85000)
		{

			for(OWLObjectSomeValuesFrom some: nominalFillerMins)
			{
				OWLObjectPropertyExpression prop =some.getProperty();
				Set<OWLIndividual> nomi = ((OWLObjectOneOf) some.getFiller()).getIndividuals();

				boolean union = true;

				HashSet<OWLObjectSomeValuesFrom> newsomes = new HashSet<OWLObjectSomeValuesFrom>();

				for(OWLIndividual indi:nomi)
				{
					OWLObjectSomeValuesFrom newsome = factory.getOWLObjectSomeValuesFrom(prop, factory.getOWLObjectOneOf(indi));
					if(classIDs.containsKey(newsome))
						newsomes.add(newsome);
					else
					{
						union = false;
						break;
					}
				}
				if(union)
				{
					OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(some, factory.getOWLObjectUnionOf(newsomes));
					visit(axiom);
				}
			}
		}

		// initialise role reflexiveness
		// If Reflexive(r)
		// \some r.\top \sub A
		// then \top \sub A
		for(Role role:relOntology.roles.values())
		{
			if(role.reflexive || (role.inverse != null && role.inverse.reflexive))
			{
				if(role.somes.get(top) != null)
					for(QueueEntry entry:role.somes.get(top).Ohat)
					{
						if(entry instanceof Implies)
						{
							Implies imply = (Implies) entry;
							if(imply.lhs == null)
								normalise(top,imply.rhs);
						}
					}
			}
		}

		// Initialise disjointness of datatypes
		if(constants.size()<1000)
		{
			dataDisjointness(factory.getOWLClass(IRI.create("http://www.w3.org/2001/XMLSchema#string")),factory.getOWLClass(IRI.create("http://www.w3.org/2001/XMLSchema#long")));
			dataDisjointness(factory.getOWLClass(IRI.create("http://www.w3.org/2001/XMLSchema#string")),factory.getOWLClass(IRI.create("http://www.w3.org/2001/XMLSchema#int")));
			//        dataDisjointness(factory.getOWLClass(IRI.create("http://www.w3.org/2001/XMLSchema#string")),factory.getOWLClass(IRI.create("http://www.w3.org/2000/01/rdf-schema#Literal")));
		}

		// another important task, initialise the value of concept number, role number, etc.
		relOntology.basicConceptNum = basicID;
		relOntology.permBasicConceptNum = basicID;
		relOntology.roleNum = roleID;

	}

	/**
	 * This method set the disjointness between two data types.
	 * This two datatypes have been approximated as OWLClasses.
	 * @param A
	 * @param B
	 */
	protected void dataDisjointness(OWLClass A, OWLClass B) {
		// TODO Auto-generated method stub

		visit(factory.getOWLDisjointClassesAxiom(A,B));
		Atomic type1 = (Atomic) approx(A);
		Atomic type2 = (Atomic) approx(B);
		Basic ct1 = (Basic) approx(factory.getOWLObjectComplementOf(A));
		Basic ct2 = (Basic) approx(factory.getOWLObjectComplementOf(B));
		type1.subsumers.add(ct2);
		type2.subsumers.add(ct1);
		for(OWLIndividual indi:constants)
		{
			Singleton single = approx(indi);
			if(single.subsumers.contains(type1))
			{
				single.subsumers.add(ct2);
				if(single.complement!=null)
					type2.subsumers.add(single.complement);
			}
			if(single.subsumers.contains(type2))
			{
				single.subsumers.add(ct1);
				if(single.complement!=null)
					type1.subsumers.add(single.complement);
			}
		}
	}

	/**
	 * This method performs the transformation of the input ontologies.
	 */
	protected void initialise()
	{
		int totalT = 0;
		int totalA = 0;
		int totalAx = 0;

		for(OWLOntology ontology:ontologies)
		{
			totalT += ontology.getClassesInSignature().size();
			totalA += ontology.getIndividualsInSignature().size();
			totalAx += ontology.getLogicalAxiomCount();
		}
		if(relOntology.profile == Profile.OWL_2_EL || totalT > RELReasonerConfiguration.largeTThreshold)
			relOntology.largeT = true;
		if(relOntology.profile == Profile.OWL_2_EL || totalA > RELReasonerConfiguration.largeAThreshold)
			relOntology.largeA = true;

		relOntology.disRes = RELReasonerConfiguration.applyDisRes(totalT,totalA,totalAx);
		individualIDs = relOntology.individualIDs;

		top.complement = bot;
		bot.complement = top;
		
		OWLClass thing = factory.getOWLThing();
		OWLClass nothing = factory.getOWLNothing();
		OWLClass namedindividual = factory.getOWLClass(IRI.create("http://www.w3.org/2002/07/owl#NamedIndividual"));

		for(OWLOntology ontology:ontologies){
			// approximate all the atomic concepts
			for(OWLClass concept:ontology.getClassesInSignature())
			{
				if(concept.equals(thing) || concept.equals(nothing) || concept.equals(namedindividual) || classIDs.containsKey(concept))
					continue;
				Atomic newconcept = new Atomic(concept);
				newconcept.id = basicID++;
				addClassID(concept, newconcept.id);
				descriptions.put(newconcept.id, newconcept);
				imply(newconcept);
				originalNamedConcepts.add(newconcept);

				// negation for all the atomics
				if(!relOntology.largeT)
				{
					Atomic nA = new Atomic();
					nA.id = basicID++;
					nA.original = false;
					addClassID(factory.getOWLObjectComplementOf(concept), nA.id);
					descriptions.put(nA.id, nA);
					imply(nA);

					newconcept.complement = nA;
					nA.complement = newconcept;
				}

			}


			// approximate all the roles
			for(OWLObjectProperty role:ontology.getObjectPropertiesInSignature())
			{

				if(propertyIDs.containsKey(role))
					continue;

				Role newrole = new Role(role,roleID++);
				propertyIDs.put(role, newrole.id);
				roles.put(newrole.id, newrole);

				// inverse for all the roles
				{
					Role inv = new Role(roleID++);
					inv.original = false;
					propertyIDs.put(role.getInverseProperty(), inv.id);
					roles.put(inv.id, inv);

					newrole.inverse = inv;
					inv.inverse = newrole;
				}

			}

			for(OWLDataProperty drole:ontology.getDataPropertiesInSignature())
			{
				OWLObjectProperty role = factory.getOWLObjectProperty(drole.getIRI());
				if(propertyIDs.containsKey(role))
					continue;
				Role newrole = new Role(role,roleID++);
				newrole.original = false;
				propertyIDs.put(role, newrole.id);
				roles.put(newrole.id, newrole);
			}

			// approximate all the individuals
			for(OWLNamedIndividual individual:ontology.getIndividualsInSignature())
			{
				if(individualIDs.containsKey(individual))
					continue;
				Singleton newindividual = new Singleton(individual);
				newindividual.id = basicID++;
				imply(newindividual);
				individualIDs.put(individual, newindividual.id);
				descriptions.put(newindividual.id, newindividual);
			}
		}
	}

	/**
	 * This method provides the atomic concept approximation of a complex description.
	 * It if has not been created, it will be created by this method and returned.
	 * @param desc
	 * @return the atomic concept description of desc
	 */
	protected Atomic getAtomicConcept(Description desc) {
		Atomic A = normalisationNames.get(desc);
		if(A == null)
		{
			A = new Atomic();
			A.id = basicID++;
			A.original = false;
			descriptions.put(A.id, A);
			normalisationNames.put(desc, A);
			imply(A);
	
			// complement
			if(!relOntology.largeT)
			{
				Atomic Acomp = new Atomic();
				Acomp.id = basicID++;
				Acomp.original = false;
				descriptions.put(Acomp.id, Acomp);
				imply(Acomp);
	
				A.complement = Acomp;
				Acomp.complement = A;
			}
		}
		return A;
	}

	/**
	 * This method normalise an role chain axiom
	 * @param lhs: the list of roles of the lhs of the axiom
	 * @param rhs: the role on the rhs of the axiom
	 */
	private void normaliseRoleChain(ArrayList<Role> lhs, Role rhs){
	
		chainRoles.add(rhs);
		chainRoles.add(rhs.inverse);
		if(lhs.size() > 2)
		{
			// Remove last item from chain.
			Role roleR2 = lhs.remove(lhs.size() - 1);
	
			// Add named property for chain.
			Role roleR1 = getChainName(lhs);
	
			HashSet<Role> superroles = roleR1.RightComposition.get(roleR2);
			if(superroles == null)
			{
				superroles = new HashSet<Role>();
				roleR1.RightComposition.put(roleR2, superroles);
			}
			superroles.add(rhs);
			normaliseRoleChain(lhs, roleR1);
		}
		else{
			Role roleR1 = lhs.get(0);
			Role roleR2 = lhs.get(1);
			chainRoles.add(roleR1);
			chainRoles.add(roleR1.inverse);
			chainRoles.add(roleR2);
			chainRoles.add(roleR2.inverse);
			HashSet<Role> superroles = roleR1.RightComposition.get(roleR2);
			if(superroles == null)
			{
				superroles = new HashSet<Role>();
				roleR1.RightComposition.put(roleR2, superroles);
			}
			superroles.add(rhs);
		}
	}


	/**
	 * This method gets the name of a role chain
	 * @param chain
	 * @return the name of chain
	 */
	private Role getChainName(ArrayList<Role> chain)
	{
		Role name = chainNames.get(chain);
		if(name == null)
		{
			name = new Role(roleID++);
			name.original = false;
			chainNames.put(chain, name);
			roles.put(name.id, name);
			{
				Role inv = new Role(roleID++);
				inv.original = false;
				roles.put(inv.id, inv);
				name.inverse = inv;
				inv.inverse = name;
			}
		}
		return name;
	}


	// From here on we implement the methods that approximate different axioms
	// Most of the methods are quite straight-forward.
	// Notes are added for methods need attention.
	
	@Override
	public void visit(OWLFunctionalObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		// For functional role R, we approximate into two axioms:
		// i.	>=2 R.\top \sub \bot
		// ii.	\top \sub <=1 R.\top
		OWLObjectPropertyExpression property = axiom.getProperty();
		Description lhs = approx(factory.getOWLObjectMinCardinality(2, property, factory.getOWLThing()));
		approx(property).functional = true;
		normalise(lhs,bot);
		Description rhs = approx(factory.getOWLObjectMaxCardinality(1, property, factory.getOWLThing()));
		normalise(top, rhs);
	}

	@Override
	public void visit(OWLSymmetricObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		// We approximate a symmetric role R as:
		// R \equiv R^-
		OWLObjectPropertyExpression property = axiom.getProperty();
		OWLObjectPropertyExpression inve = property.getInverseProperty();
		visit(factory.getOWLEquivalentObjectPropertiesAxiom(property,inve));

	}

	@Override
	public void visit(OWLFunctionalDataPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		OWLDataPropertyExpression property = axiom.getProperty();
		Description lhs = approx(factory.getOWLObjectMinCardinality(2, factory.getOWLObjectProperty(property.asOWLDataProperty().getIRI()), factory.getOWLThing()));
		approx(property).functional = true;
		normalise(lhs,bot);

	}

	@Override
	public void visit(OWLInverseFunctionalObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		OWLObjectPropertyExpression property = axiom.getProperty();
		Description lhs = approx(factory.getOWLObjectMinCardinality(2, property.getInverseProperty(), factory.getOWLThing()));
		approx(property.getInverseProperty()).functional = true;		
		normalise(lhs,bot);
	}

	@Override
	public void visit(OWLObjectPropertyAssertionAxiom axiom) {
		OWLIndividual sub = axiom.getSubject();
		OWLIndividual obj = axiom.getObject();		
		Singleton subject = approx(sub);
		Singleton object = approx(obj);
		OWLObjectPropertyExpression property = axiom.getProperty();
		Role role = approx(property);
		initialise(subject, role, object);

	}

	@Override
	public void visit(OWLDataPropertyAssertionAxiom axiom) {
		// TODO Auto-generated method stub
		OWLIndividual sub = axiom.getSubject();
		
		// Note that we treat data value as individual
		OWLIndividual obj = factory.getOWLNamedIndividual(IRI.create(INDI_PREFIX+axiom.getObject().getLiteral()));		

		// It will be added into the constant set and float individual set accordingly
		constants.add(obj);
		if(axiom.getObject().isFloat())
			floats.put(axiom.getObject().parseFloat(), obj);

		Singleton subject = approx(sub);
		Singleton object = approx(obj);
		OWLDataPropertyExpression property = axiom.getProperty();
		Role role = approx(property);
		initialise(subject, role, object);

	}

	@Override
	public void visit(OWLClassAssertionAxiom axiom) {
		// TODO Auto-generated method stub
		Singleton indi = approx(axiom.getIndividual());
		Description classification = approx(getNNF(axiom.getClassExpression()));
		normalise(indi,classification);
	}

	@Override
	public void visit(OWLDifferentIndividualsAxiom axiom) {
		// TODO Auto-generated method stub
		containDiffIndisAxiom = true;
		Set<OWLIndividual> individuals = axiom.getIndividuals();

		for(OWLIndividual individual1:individuals)
		{
			Singleton indi1 = approx(individual1);
			for(OWLIndividual individual2:individuals)
			{
				if(individual1.equals(individual2))
					continue;
				Singleton indi2 = approx(individual2);
				indi1.differentIndividuals.add(indi2);
				indi2.differentIndividuals.add(indi1);
			}
		}
	}

	@Override
	public void visit(OWLSameIndividualAxiom axiom) {
		// TODO Auto-generated method stub
		Set<OWLIndividual> individuals = axiom.getIndividuals();

		for(OWLIndividual individual1:individuals)
		{
			Singleton indi1 = approx(individual1);
			for(OWLIndividual individual2:individuals)
			{
				if(individual1.equals(individual2))
					continue;
				Singleton indi2 = approx(individual2);
				normalise(indi1,indi2);
				normalise(indi2,indi1);
			}
		}
	}

	@Override
	public void visit(OWLInverseObjectPropertiesAxiom axiom) {
		// TODO Auto-generated method stub
		Role role1 = approx(axiom.getFirstProperty());
		Role role2 = approx(axiom.getSecondProperty());
		role1.subsumers.add(role2.inverse);
		role2.subsumers.add(role1.inverse);
		role1.inverse.subsumers.add(role2);
		role2.inverse.subsumers.add(role1);
	}

	@Override
	public void visit(OWLObjectPropertyRangeAxiom axiom) {
		// TODO Auto-generated method stub
		// for axiom Range(R) = C, we also have two approximations:
		// \some R.\neg C \sub \bot
		// \some R^-.\top \sub C
		OWLClassExpression range = axiom.getRange();
		OWLObjectPropertyExpression property = axiom.getProperty();
		approx(property).related = true;
		OWLClassExpression some = factory.getOWLObjectSomeValuesFrom(property, factory.getOWLObjectComplementOf(range));
		normalise(approx(getNNF(some)), bot);
		OWLClassExpression exist = factory.getOWLObjectSomeValuesFrom(property.getInverseProperty(), factory.getOWLThing());
		normalise(approx(getNNF(exist)), approx(getNNF(range)));
		Role inverse=approx(property.getInverseProperty());
		if(inverse != null)
			inverse.related = true;
	}

	@Override
	public void visit(OWLSubObjectPropertyOfAxiom axiom) {
		approx(axiom.getSubProperty()).subsumers.add(approx(axiom.getSuperProperty()));
	}

	@Override
	public void visit(OWLSubDataPropertyOfAxiom axiom) {
		// TODO Auto-generated method stub
		approx(axiom.getSubProperty()).subsumers.add(approx(axiom.getSuperProperty()));
	}

	@Override
	public void visit(OWLSubPropertyChainOfAxiom axiom) {
		chain += 1;
		ArrayList<Role> lhs = new ArrayList<Role>();
		for(OWLObjectPropertyExpression role:axiom.getPropertyChain())
		{
			Role p = approx(role);
			p.related = true;
			lhs.add(p);
		}
		Role rhs = approx(axiom.getSuperProperty());
		normaliseRoleChain(lhs, rhs);
	}

	@Override
	public void visit(OWLObjectPropertyDomainAxiom axiom) {
		// TODO Auto-generated method stub
		OWLClassExpression exist = factory.getOWLObjectSomeValuesFrom(axiom.getProperty(), factory.getOWLThing());
		Description lhs = approx(getNNF(exist));
		approx(axiom.getProperty()).related = true;
		Description rhs = approx(getNNF(axiom.getDomain()));
		normalise(lhs, rhs);
	}

	@Override
	public void visit(OWLDataPropertyDomainAxiom axiom) {
		// TODO Auto-generated method stub
		OWLClassExpression exist = factory.getOWLObjectSomeValuesFrom(factory.getOWLObjectProperty(axiom.getProperty().asOWLDataProperty().getIRI()), factory.getOWLThing());
		approx(axiom.getProperty()).related = true;
		Description lhs = approx(getNNF(exist));
		Description rhs = approx(getNNF(axiom.getDomain()));
		normalise(lhs, rhs);

	}

	@Override
	public void visit(OWLDataPropertyRangeAxiom axiom) {
		// TODO Auto-generated method stub
		OWLDataRange range = axiom.getRange();
		OWLDataPropertyExpression property = axiom.getProperty();
		approx(property).related = true;
		OWLClassExpression some = factory.getOWLDataSomeValuesFrom(property, factory.getOWLDataComplementOf(range));
		normalise(approx(getNNF(some)), bot);

	}

	@Override
	public void visit(OWLEquivalentClassesAxiom axiom) {
		// TODO Auto-generated method stub
		for (OWLClassExpression c : axiom.getClassExpressions()) {
			for(OWLObjectProperty prop:c.getObjectPropertiesInSignature())
				approx(prop).related = true;
			for (OWLClassExpression d : axiom.getClassExpressions()) {
				if(c.equals(d))
					continue;
				Description dApprox = approx(getNNF(d));
				if(c instanceof OWLObjectUnionOf)
				{
					// Here if we have C1 \or C2 \or ... \sub D
					// We directly approximate as Ci \sub D for all Ci
					for(OWLClassExpression ci:c.asDisjunctSet())
					{
						normalise(approx(getNNF(ci)),dApprox);
						// only when we need to deal with meta modelling ontology
						// for Jek's work
						if(relOntology.MetaOn && ci instanceof OWLObjectSomeValuesFrom)
						{
							OWLObjectSomeValuesFrom some = (OWLObjectSomeValuesFrom) ci;
							OWLObjectPropertyExpression prop = some.getProperty();
							//							if(prop instanceof OWLObjectProperty && prop.asOWLObjectProperty().getIRI().getFragment().equals("p_type"))
							approximate(some.getFiller(), factory.getOWLObjectAllValuesFrom(prop.getInverseProperty(), d));
						}
					}
				}
				else{
					Description cApprox = approx(getNNF(c));
					normalise(cApprox, dApprox);
					// only when we need to deal with meta modelling ontology
					// for Jek's work
					if(relOntology.MetaOn && getNNF(c) instanceof OWLObjectSomeValuesFrom)
					{
						OWLObjectSomeValuesFrom some = (OWLObjectSomeValuesFrom) getNNF(c);
						OWLObjectPropertyExpression prop = some.getProperty();
						//					if(prop instanceof OWLObjectProperty && prop.asOWLObjectProperty().getIRI().getFragment().equals("p_type"))
						approximate(some.getFiller(), factory.getOWLObjectAllValuesFrom(prop.getInverseProperty(), d));
					}
				}
			}
		}   	

	}

	// equivalent property 
	@Override
	public void visit(OWLEquivalentObjectPropertiesAxiom axiom) {
		// RW2: property equivalence.
		for (OWLObjectPropertyExpression r : axiom.getProperties()) {
			for (OWLObjectPropertyExpression s : axiom.getProperties()) {
				if(r.equals(s))
					continue;
				Role roler = approx(r);
				Role roles = approx(s);
				roler.subsumers.add(roles);
			}
		}
	}

	@Override
	public void visit(OWLEquivalentDataPropertiesAxiom axiom) {
		// TODO Auto-generated method stub
		for (OWLDataPropertyExpression r : axiom.getProperties()) {
			for (OWLDataPropertyExpression s : axiom.getProperties()) {
				if(r.equals(s))
					continue;
				Role roler = approx(r);
				Role roles = approx(s);
				roler.subsumers.add(roles);
			}
		}

	}

	// transitive property
	@Override
	public void visit(OWLTransitiveObjectPropertyAxiom axiom) {
		// RW3: transitive using role composition.
		trans += 1;
		OWLSubPropertyChainOfAxiom rewritten = factory.getOWLSubPropertyChainOfAxiom(Arrays.asList(axiom.getProperty(), axiom.getProperty()), axiom.getProperty());
		visit(rewritten);
	}

	@Override
	public void visit(OWLDisjointClassesAxiom axiom) {
		// TODO Auto-generated method stub

		// We can re-write concept disjointness with two different ways
		// for example, if Disjoint(C1, C2, ..., Cn), we can have:
		// 1. Ci \and Cj \sub \bot for different i, j
		// 2. Ci \sub \neg Cj for different i, j
		// The option 2 requires approximation of \neg Cj so we only apply it when TBox is small.
		// The option 1 is applied when TBox is large.
		
		if(relOntology.largeT)
		{
			Set<OWLClassExpression> cs = new HashSet<OWLClassExpression>();
			for(OWLClassExpression ci:axiom.getClassExpressions())
			{
				for(OWLClassExpression cj:cs)
				{
					OWLObjectIntersectionOf inter = factory.getOWLObjectIntersectionOf(ci,cj);
					OWLLogicalAxiom ax = factory.getOWLSubClassOfAxiom(inter, factory.getOWLNothing());
					ax.accept(this);
				}
				cs.add(ci);
			}
		}
		else
		{
			// samll and with query
			Set<Basic> basics = new HashSet<Basic>();
			for(OWLClassExpression ci:axiom.getClassExpressions())
			{
				Description ciApprox = approx(getNNF(ci));
				Basic ciBasic;
				if(ciApprox instanceof Basic)
					ciBasic = (Basic)ciApprox;
				else
					ciBasic = getAtomicConcept(ciApprox);
				for(Basic cjBasic:basics)
				{
					cjBasic.Ohat.add(getA2Bot(ciBasic));
					ciBasic.Ohat.add(getA2Bot(cjBasic));
					if(cjBasic.complement != null)
					{
						normalise(ciBasic,cjBasic.complement);
					}
				}
				basics.add(ciBasic);
			}
		}

	}

	@Override
	public void visit(OWLDisjointObjectPropertiesAxiom axiom) {
		// TODO Auto-generated method stub
		Set<Role> roles = new HashSet<Role>();
		for(OWLObjectPropertyExpression prop1:axiom.getProperties())
		{
			Role role1 = approx(prop1);
			for(Role role:roles)
			{
				role.disjoints.add(role1);
				role1.disjoints.add(role);
			}
			roles.add(role1);
		}

	}

	public void visit(OWLSubClassOfAxiom axiom) {
		OWLClassExpression sub = axiom.getSubClass();
		for(OWLObjectProperty prop:sub.getObjectPropertiesInSignature())
			approx(prop).related = true;
		OWLClassExpression sup = axiom.getSuperClass();

		// we approximate the subsumption axiom
		approximate(getNNF(sub), getNNF(sup));
	}


	@Override
	public void visit(OWLReflexiveObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
	
		Role role = approx(axiom.getProperty());
		role.reflexive = true;
		role.inverse.reflexive = true;	
	}


	// get the entry A->\bot, or in other words, ->\neg A.
	Implies getA2Bot(Basic basic){
		//		Implies implies = basic.A2Bot;
		//		if(implies == null)
		//		{
		//			implies = new Implies();
		//			implies.lhs.add(basic);
		//			implies.rhs = bot;
		//			basic.A2Bot = implies;
		//		}
		//		return implies;
		return basic.complement.entry;
	}

	protected void approximate(OWLClassExpression sub, OWLClassExpression sup)
	{
		Description lhs = approx(sub);
		Description rhs = approx(sup);
	
		// original subsumee
		if(relOntology.largeT && lhs instanceof Basic && rhs instanceof Basic)
		{
			Basic lbasic = (Basic) lhs;
			Basic rbasic = (Basic) rhs;
			if(rbasic.originalSubsumee == null)
				rbasic.originalSubsumee = new HashSet<Basic>();
			rbasic.originalSubsumee.add(lbasic);
		}
		// transform C \sub \some r.(D1 \or D2 \or ... \or Dn) to
		// C \sub \some r.D1 \or \some r.D2 \or ... \or \some r.Dn
		// might be a bit redundant with the nominalFillerMins processing.
		if(lhs instanceof Basic && sup instanceof OWLObjectSomeValuesFrom)
		{
			OWLObjectSomeValuesFrom some = (OWLObjectSomeValuesFrom) sup;
			if(some.getFiller() instanceof OWLObjectUnionOf)
			{
				HashSet<OWLObjectSomeValuesFrom> somes = new HashSet<OWLObjectSomeValuesFrom>();
				for(OWLClassExpression exp:((OWLObjectUnionOf)some.getFiller()).getOperands())
					somes.add(factory.getOWLObjectSomeValuesFrom(some.getProperty(), exp));
				Basic rewriting = (Basic)approx( factory.getOWLObjectUnionOf(somes));
				normalise(lhs, rewriting);
				if(relOntology.largeT)
				{
					if(rewriting.originalSubsumee == null)
						rewriting.originalSubsumee = new HashSet<Basic>();
					rewriting.originalSubsumee.add((Basic)lhs);
				}
			}
		}
	
	
		normalise(lhs, rhs);
	
		// Only for meta modelling ontology
		if(relOntology.MetaOn && sub instanceof OWLObjectSomeValuesFrom)
		{
			OWLObjectSomeValuesFrom some = (OWLObjectSomeValuesFrom) sub;
			OWLObjectPropertyExpression prop = some.getProperty();
			//			if(prop instanceof OWLObjectProperty && prop.asOWLObjectProperty().getIRI().getFragment().equals("p_type"))
			approximate(some.getFiller(), factory.getOWLObjectAllValuesFrom(prop.getInverseProperty(), sup));
		}
	}

	/**
	 * This method gets the NNF of the input class expression.
	 * @param concept
	 * @return the NNF of concept
	 */
	protected OWLClassExpression getNNF(OWLClassExpression concept)
	{
		// we did not use the original method in OWLAPI because
		// 1. the method used to have some errors in OWLAPI, don't know if it is fixed now.
		// 2. we do some transformation here as well.
		OWLClassExpression nnf = null;
		if(concept.isOWLThing() || concept.isOWLNothing() || concept instanceof OWLClass || concept instanceof OWLObjectOneOf)
			nnf = concept;
		else if(concept instanceof OWLObjectComplementOf)
		{
			OWLObjectComplementOf comp = (OWLObjectComplementOf) concept;
			OWLClassExpression des = comp.getOperand();
			if(des.isOWLThing())
				nnf = factory.getOWLNothing();
			else if(des.isOWLNothing())
				nnf = factory.getOWLThing();
			else if(des instanceof OWLClass)
				nnf = concept;
			else if(des instanceof OWLObjectComplementOf)
			{
				OWLObjectComplementOf doublecomp = (OWLObjectComplementOf) des;
				nnf = doublecomp.getOperand();
			}
			else if(des instanceof OWLObjectIntersectionOf)
			{
				OWLObjectIntersectionOf intersection = (OWLObjectIntersectionOf) des;
				Set<OWLClassExpression> interNNF = new HashSet<OWLClassExpression>();
				for(OWLClassExpression inter : intersection.getOperands())
				{
					interNNF.add(getNNF(factory.getOWLObjectComplementOf(inter)));
				}
				nnf = factory.getOWLObjectUnionOf(interNNF);
			}
			else if(des instanceof OWLObjectUnionOf)
			{
				OWLObjectUnionOf union = (OWLObjectUnionOf) des;
				Set<OWLClassExpression> uniNNF = new HashSet<OWLClassExpression>();
				for(OWLClassExpression uni:union.getOperands())
					uniNNF.add(getNNF(factory.getOWLObjectComplementOf(uni)));
				nnf = factory.getOWLObjectIntersectionOf(uniNNF);
			}
			else if(des instanceof OWLObjectSomeValuesFrom)
			{
				OWLObjectSomeValuesFrom some = (OWLObjectSomeValuesFrom) des;
				OWLObjectPropertyExpression property = some.getProperty();
				OWLClassExpression filler = some.getFiller();
				nnf = factory.getOWLObjectAllValuesFrom(property, getNNF(factory.getOWLObjectComplementOf(filler)));
			}
			else if(des instanceof OWLObjectAllValuesFrom)
			{
				OWLObjectAllValuesFrom all = (OWLObjectAllValuesFrom) des;
				OWLObjectPropertyExpression property = all.getProperty();
				OWLClassExpression filler = all.getFiller();
				nnf = factory.getOWLObjectSomeValuesFrom(property, getNNF(factory.getOWLObjectComplementOf(filler)));
			}
			else if(des instanceof OWLObjectMinCardinality)
			{
				OWLObjectMinCardinality min = (OWLObjectMinCardinality) des;
				OWLObjectPropertyExpression property = min.getProperty();
				OWLClassExpression filler = min.getFiller();
				int card = min.getCardinality();
				if(card >= 1)
				{
					nnf = factory.getOWLObjectMaxCardinality(card-1, property, getNNF(filler));
				}
				else
					nnf = factory.getOWLNothing();
			}
			else if(des instanceof OWLObjectMaxCardinality)
			{
				OWLObjectMaxCardinality max = (OWLObjectMaxCardinality) des;
				OWLObjectPropertyExpression property = max.getProperty();
				OWLClassExpression filler = max.getFiller();
				int card = max.getCardinality();
				nnf = factory.getOWLObjectMinCardinality(card+1, property, getNNF(filler));
			}
			else if(des instanceof OWLObjectExactCardinality)
			{
				OWLObjectExactCardinality exact = (OWLObjectExactCardinality) des;
				if(exact.getCardinality() >= 1)
				{
					OWLClassExpression low = factory.getOWLObjectMaxCardinality(exact.getCardinality()-1,exact.getProperty(),  getNNF(exact.getFiller()));
					OWLClassExpression high = factory.getOWLObjectMinCardinality(exact.getCardinality()+1, exact.getProperty(), getNNF(exact.getFiller()));
					nnf = factory.getOWLObjectUnionOf(low,high);
				}
				else
					nnf = factory.getOWLObjectSomeValuesFrom(exact.getProperty(), getNNF(exact.getFiller()));
			}
			else if(des instanceof OWLObjectOneOf)
			{
				OWLObjectOneOf oneof = (OWLObjectOneOf)des;
				HashSet<OWLObjectComplementOf> compinter = new HashSet<OWLObjectComplementOf>();
				for(OWLIndividual indi:oneof.getIndividuals())
					compinter.add(factory.getOWLObjectComplementOf(factory.getOWLObjectOneOf(indi)));
				nnf = factory.getOWLObjectIntersectionOf(compinter);
			}
			else if(des instanceof OWLObjectHasValue)
			{
				OWLObjectHasValue value = (OWLObjectHasValue) des;
				nnf = factory.getOWLObjectAllValuesFrom(value.getProperty(), factory.getOWLObjectComplementOf(factory.getOWLObjectOneOf(value.getValue())));
				//				nnf = getNNF(factory.getOWLObjectComplementOf(getNNF(des)));
			}

			// datatype
			else if(des instanceof OWLDataSomeValuesFrom)
			{
				OWLDataSomeValuesFrom some = (OWLDataSomeValuesFrom) des;
				OWLObjectPropertyExpression property = factory.getOWLObjectProperty(some.getProperty().asOWLDataProperty().getIRI());
				nnf = factory.getOWLObjectAllValuesFrom(property, getNNF(factory.getOWLDataComplementOf(some.getFiller())));
			}
			else if(des instanceof OWLDataAllValuesFrom)
			{
				OWLDataAllValuesFrom all = (OWLDataAllValuesFrom) des;
				OWLObjectPropertyExpression property = factory.getOWLObjectProperty(all.getProperty().asOWLDataProperty().getIRI());
				nnf = factory.getOWLObjectSomeValuesFrom(property, getNNF(factory.getOWLDataComplementOf(all.getFiller())));
			}
			else if(des instanceof OWLDataHasValue)
			{
				OWLDataHasValue value = (OWLDataHasValue) des;
				OWLObjectPropertyExpression property = factory.getOWLObjectProperty(value.getProperty().asOWLDataProperty().getIRI());
				OWLIndividual indi = factory.getOWLNamedIndividual(IRI.create(INDI_PREFIX+value.getValue().getLiteral()));
				constants.add(indi);
				if(value.getValue().isFloat())
					floats.put(value.getValue().parseFloat(), indi);
				nnf = factory.getOWLObjectAllValuesFrom(property, factory.getOWLObjectComplementOf(factory.getOWLObjectOneOf(indi)));

			}
			else if(des instanceof OWLDataMinCardinality)
			{
				OWLDataMinCardinality min = (OWLDataMinCardinality) des;
				OWLObjectPropertyExpression property = factory.getOWLObjectProperty(min.getProperty().asOWLDataProperty().getIRI());
				OWLDataRange filler = min.getFiller();
				int card = min.getCardinality();
				if(card >= 1)
				{
					nnf = factory.getOWLObjectMaxCardinality(card-1, property, getNNF(filler));
				}
				else
					nnf = factory.getOWLNothing();
			}
			else if(des instanceof OWLDataMaxCardinality)
			{
				OWLDataMaxCardinality max = (OWLDataMaxCardinality) des;
				OWLObjectPropertyExpression property = factory.getOWLObjectProperty(max.getProperty().asOWLDataProperty().getIRI());
				OWLDataRange filler = max.getFiller();
				int card = max.getCardinality();
				nnf = factory.getOWLObjectMinCardinality(card+1, property, getNNF(filler));
			}
			else if(des instanceof OWLDataExactCardinality)
			{
				OWLDataExactCardinality exact = (OWLDataExactCardinality) des;
				OWLObjectPropertyExpression property = factory.getOWLObjectProperty(exact.getProperty().asOWLDataProperty().getIRI());
				if(exact.getCardinality() >= 1)
				{
					OWLClassExpression low = factory.getOWLObjectMaxCardinality(exact.getCardinality()-1, property, getNNF(exact.getFiller()));
					OWLClassExpression high = factory.getOWLObjectMinCardinality(exact.getCardinality()+1, property, getNNF(exact.getFiller()));
					nnf = factory.getOWLObjectUnionOf(low,high);
				}
				else
					nnf = factory.getOWLObjectSomeValuesFrom(property, getNNF(exact.getFiller()));
			}
			// end datatype

			else nnf = concept;

		}
		else if(concept instanceof OWLObjectIntersectionOf)
		{
			OWLObjectIntersectionOf inter = (OWLObjectIntersectionOf) concept;
			Set<OWLClassExpression> interNNF = new HashSet<OWLClassExpression>();
			for(OWLClassExpression des:inter.getOperands())
			{
				interNNF.add(getNNF(des));
			}
			nnf = factory.getOWLObjectIntersectionOf(interNNF);
		}
		else if(concept instanceof OWLObjectUnionOf)
		{
			OWLObjectUnionOf union = (OWLObjectUnionOf) concept;
			Set<OWLClassExpression> unionNNF = new HashSet<OWLClassExpression>();
			for(OWLClassExpression des:union.getOperands())
			{
				unionNNF.add(getNNF(des));
			}
			nnf = factory.getOWLObjectUnionOf(unionNNF);
		}
		else if(concept instanceof OWLObjectSomeValuesFrom)
		{
			OWLObjectSomeValuesFrom some = (OWLObjectSomeValuesFrom) concept;
			OWLObjectPropertyExpression property = some.getProperty();
			nnf = factory.getOWLObjectSomeValuesFrom(property, getNNF(some.getFiller()));
		}
		else if(concept instanceof OWLObjectAllValuesFrom)
		{
			OWLObjectAllValuesFrom all = (OWLObjectAllValuesFrom) concept;
			nnf = factory.getOWLObjectAllValuesFrom(all.getProperty(), getNNF(all.getFiller()));
		}
		else if(concept instanceof OWLObjectMinCardinality)
		{
			OWLObjectMinCardinality min = (OWLObjectMinCardinality) concept;
			OWLObjectPropertyExpression property = min.getProperty();
			OWLClassExpression filler = min.getFiller();
			int card = min.getCardinality();
			if(card == 0)
				nnf = factory.getOWLThing();
			else if(card == 1)
				nnf = factory.getOWLObjectSomeValuesFrom(property, getNNF(filler));
			else
			{
				nnf = factory.getOWLObjectMinCardinality(card, property, getNNF(filler));
			}
		}
		else if(concept instanceof OWLObjectMaxCardinality)
		{
			OWLObjectMaxCardinality max = (OWLObjectMaxCardinality) concept;
			OWLObjectPropertyExpression property = max.getProperty();
			OWLClassExpression filler = max.getFiller();
			int card = max.getCardinality();
			if(card < 1)
				nnf = factory.getOWLObjectAllValuesFrom(property, getNNF(factory.getOWLObjectComplementOf(filler)));
			else
				nnf = factory.getOWLObjectMaxCardinality(card, property, getNNF(filler));
		}
		else if(concept instanceof OWLObjectExactCardinality)
		{
			OWLObjectExactCardinality exact = (OWLObjectExactCardinality) concept;
			if(exact.getCardinality() >= 1)
			{
				OWLClassExpression low = factory.getOWLObjectMaxCardinality(exact.getCardinality(), exact.getProperty(), getNNF(exact.getFiller()));
				OWLClassExpression high = factory.getOWLObjectMinCardinality(exact.getCardinality(), exact.getProperty(), getNNF(exact.getFiller()));
				nnf = factory.getOWLObjectIntersectionOf(getNNF(low),getNNF(high));
			}
			else
				nnf = factory.getOWLObjectAllValuesFrom(exact.getProperty(), getNNF(factory.getOWLObjectComplementOf(exact.getFiller())));
		}
		else if(concept instanceof OWLObjectHasValue)
		{
			OWLObjectHasValue value = (OWLObjectHasValue) concept;
			OWLObjectPropertyExpression property = value.getProperty();
			OWLIndividual indi = value.getValue();
			nnf = factory.getOWLObjectSomeValuesFrom(property, factory.getOWLObjectOneOf(indi));
		}

		// datatype
		else if(concept instanceof OWLDataSomeValuesFrom)
		{
			OWLDataSomeValuesFrom some = (OWLDataSomeValuesFrom) concept;
			OWLObjectPropertyExpression property = factory.getOWLObjectProperty(some.getProperty().asOWLDataProperty().getIRI());
			nnf = factory.getOWLObjectSomeValuesFrom(property, getNNF(some.getFiller()));
		}
		else if(concept instanceof OWLDataAllValuesFrom)
		{
			OWLDataAllValuesFrom all = (OWLDataAllValuesFrom) concept;
			OWLObjectPropertyExpression property = factory.getOWLObjectProperty(all.getProperty().asOWLDataProperty().getIRI());
			nnf = factory.getOWLObjectAllValuesFrom(property, getNNF(all.getFiller()));

		}
		else if(concept instanceof OWLDataHasValue)
		{
			OWLDataHasValue value = (OWLDataHasValue) concept;
			OWLObjectPropertyExpression property = factory.getOWLObjectProperty(value.getProperty().asOWLDataProperty().getIRI());
			OWLIndividual indi = factory.getOWLNamedIndividual(IRI.create(INDI_PREFIX+value.getValue().getLiteral()));
			OWLClass cls = factory.getOWLClass(value.getValue().getDatatype().getIRI());
			constants.add(indi);
			if(value.getValue().isFloat())
				floats.put(value.getValue().parseFloat(), indi);
			nnf = factory.getOWLObjectSomeValuesFrom(property, factory.getOWLObjectOneOf(indi));
			//			visit(factory.getOWLClassAssertionAxiom(cls, indi));
			approx(indi).subsumers.add((Basic) approx(cls));

		}
		else if(concept instanceof OWLDataMinCardinality)
		{
			OWLDataMinCardinality min = (OWLDataMinCardinality) concept;
			OWLObjectPropertyExpression property = factory.getOWLObjectProperty(min.getProperty().asOWLDataProperty().getIRI());
			OWLDataRange filler = min.getFiller();
			int card = min.getCardinality();
			if(card == 0)
				nnf = factory.getOWLThing();
			else if(card == 1)
				nnf = factory.getOWLObjectSomeValuesFrom(property, getNNF(filler));
			else
			{
				nnf = factory.getOWLObjectMinCardinality(card, property, getNNF(filler));
			}
		}
		else if(concept instanceof OWLDataMaxCardinality)
		{
			OWLDataMaxCardinality max = (OWLDataMaxCardinality) concept;
			OWLObjectPropertyExpression property = factory.getOWLObjectProperty(max.getProperty().asOWLDataProperty().getIRI());
			OWLDataRange filler = max.getFiller();
			int card = max.getCardinality();
			if(card < 1)
				nnf = factory.getOWLObjectAllValuesFrom(property, getNNF(factory.getOWLDataComplementOf(filler)));
			else
				nnf = factory.getOWLObjectMaxCardinality(card, property, getNNF(filler));
		}
		else if(concept instanceof OWLDataExactCardinality)
		{
			OWLDataExactCardinality exact = (OWLDataExactCardinality) concept;
			OWLObjectPropertyExpression property = factory.getOWLObjectProperty(exact.getProperty().asOWLDataProperty().getIRI());
			if(exact.getCardinality() >= 1)
			{
				OWLClassExpression low = factory.getOWLObjectMaxCardinality(exact.getCardinality(), property, getNNF(exact.getFiller()));
				OWLClassExpression high = factory.getOWLObjectMinCardinality(exact.getCardinality(), property, getNNF(exact.getFiller()));
				nnf = factory.getOWLObjectIntersectionOf(getNNF(low),getNNF(high));
			}
			else
				nnf = factory.getOWLObjectAllValuesFrom(property, getNNF(factory.getOWLDataComplementOf(exact.getFiller())));
		}
		// end datatype

		else
		{
			//			System.out.println("Can't get NNF for "+concept);
			nnf = concept;
		}
		return nnf;
	}

	HashMap<Float, OWLIndividual> floats = new HashMap<Float, OWLIndividual>();
	HashSet<OWLClass> datatypes = new HashSet<OWLClass>();

	private OWLClassExpression getNNF(OWLDataRange data)
	{
		OWLClassExpression NC = null;
		// if(data.isDatatype())
		// modified by Sylvia Wang
		if (data.isOWLDatatype())
		{
			OWLDatatype type = data.asOWLDatatype();
			OWLClass dataclass = factory.getOWLClass(type.getIRI());
			datatypes.add(dataclass);
			NC = dataclass;
		}
		else if(data instanceof OWLDataComplementOf)
		{
			OWLDataComplementOf comp = (OWLDataComplementOf) data;
			OWLDataRange des = comp.getDataRange();
			NC = getNNF(factory.getOWLObjectComplementOf(getNNF(des)));
		}
		else if(data instanceof OWLDataIntersectionOf)
		{
			OWLDataIntersectionOf intesect = (OWLDataIntersectionOf) data;
			HashSet<OWLClassExpression> clss = new HashSet<OWLClassExpression>();
			for(OWLDataRange rng:intesect.getOperands())
				clss.add(getNNF(rng));
			NC = getNNF(factory.getOWLObjectIntersectionOf(clss));
		}
		else if(data instanceof OWLDataUnionOf)
		{
			OWLDataUnionOf union = (OWLDataUnionOf) data;
			HashSet<OWLClassExpression> clss = new HashSet<OWLClassExpression>();
			for(OWLDataRange rng:union.getOperands())
				clss.add(getNNF(rng));
			NC = getNNF(factory.getOWLObjectUnionOf(clss));
		}
		else if(data instanceof OWLDataOneOf)
		{
			OWLDataOneOf oneof = (OWLDataOneOf) data;

			Set<OWLIndividual> concepts = new HashSet<OWLIndividual>();
			for(OWLLiteral constant:oneof.getValues())
			{
				OWLIndividual individual = factory.getOWLNamedIndividual(IRI.create(INDI_PREFIX+constant.getLiteral()));
				constants.add(individual);
				if(constant.isFloat())
					floats.put(constant.parseFloat(), individual);
				concepts.add(individual);

				OWLClass cls = factory.getOWLClass(constant.getDatatype().getIRI());

				//				visit(factory.getOWLClassAssertionAxiom(cls, indi));
				approx(individual).subsumers.add((Basic) approx(cls));

			}
			NC = factory.getOWLObjectOneOf(concepts);
		}
		else if(data instanceof OWLDatatypeRestriction)
		{
			OWLDatatypeRestriction rest = (OWLDatatypeRestriction) data;
			HashSet<OWLClassExpression> exps = new HashSet<OWLClassExpression>();
			exps.add(getNNF(rest.getDatatype()));
			for(OWLFacetRestriction facet:rest.getFacetRestrictions())
			{
				if(facet.getFacetValue().isFloat())
				{
					float value = facet.getFacetValue().parseFloat();
					String restriction = facet.getFacet().getIRI().getFragment();
					if(restriction.contains("minInclusive"))
					{
						OWLClass cls=factory.getOWLClass(IRI.create("http://trowl.eu/minInclusive/"+value)); 
						minInclusives.put(value, cls);
						exps.add(cls);
					}
					else if(restriction.contains("minExclusive"))
					{
						OWLClass cls = factory.getOWLClass(IRI.create("http://trowl.eu/minExclusive/"+value));
						minExclusives.put(value, cls);
						exps.add(cls);
					}
					else if(restriction.contains("maxInclusive"))
					{
						OWLClass cls = factory.getOWLClass(IRI.create("http://trowl.eu/maxInclusive/"+value));
						maxInclusives.put(value, cls);
						exps.add(cls);
					}
					else if(restriction.contains("maxExclusive"))
					{
						OWLClass cls = factory.getOWLClass(IRI.create("http://trowl.eu/maxExclusive/"+value));
						maxExclusives.put(value, cls);
						exps.add(cls);
					}
					else{
						OWLIndividual individual = factory.getOWLNamedIndividual(IRI.create(INDI_PREFIX+facet.getFacetValue().parseFloat()));
						//					constants.add(individual);
						exps.add(factory.getOWLObjectHasValue((factory.getOWLObjectProperty(facet.getFacet().getIRI())), individual));
					}
				}
				else
					exps.add(factory.getOWLObjectHasValue((factory.getOWLObjectProperty(facet.getFacet().getIRI())), factory.getOWLNamedIndividual(IRI.create(INDI_PREFIX+facet.getFacetValue()))));
			}
			NC = factory.getOWLObjectIntersectionOf(exps);
		}
		return NC;
	}

	HashMap<Float, OWLClass> minExclusives = new HashMap<Float, OWLClass>();
	HashMap<Float, OWLClass> minInclusives = new HashMap<Float, OWLClass>();
	HashMap<Float, OWLClass> maxExclusives = new HashMap<Float, OWLClass>();
	HashMap<Float, OWLClass> maxInclusives = new HashMap<Float, OWLClass>();

	/**
	 * This method normalises a concept subsumption axiom
	 * @param lhs
	 * @param rhs
	 */
	public void normalise(Description lhs, Description rhs)
	{
		if(lhs instanceof And)
		{
			And and = (And) lhs;
			HashSet<Description> descriptions = and.operands;
			HashSet<Basic> normalised = new HashSet<Basic>();
			for(Description CHat:descriptions)
			{
				if(!(CHat instanceof Basic))
				{
					Atomic A = getAtomicConcept(CHat);
					normalised.add(A);
					normalise(CHat, A);
				}
				else
					normalised.add((Basic)CHat);
			}
			{
				Basic B = null;
				if(rhs instanceof Basic)
					B = (Basic)rhs;
				else
				{
					B = getAtomicConcept(rhs);
					normalise(B, rhs);
				}
				initialise(normalised, B);
				//				// full resolution
				//
				//				if(normalised.size() >1 && normalised.size() <=4)
				//				{
				//					Basic Bcomp = B.complement;
				//					if(Bcomp == null)
				//					{
				//						Atomic BcompA = new Atomic();
				//						BcompA.id = classindex;
				//						BcompA.original = false;
				//						BcompA.uri = IRI.create(CLASS_PREFIX+(classindex++));
				//						this.descriptions.put(BcompA.id, BcompA);
				//						imply(BcompA);
				//						BcompA.complement = B;
				//						B.complement = BcompA;
				//						Bcomp = BcompA;
				//					}
				//					normalised.add(Bcomp);
				//					for(Basic candidate:normalised)
				//					{
				//						if(!candidate.equals(Bcomp))
				//						{
				//							Basic cadicomp = candidate.complement;
				//							if(cadicomp == null)
				//							{
				//								Atomic cadicompA = new Atomic();
				//								cadicompA.id = classindex;
				//								cadicompA.original = false;
				//								cadicompA.uri = IRI.create(CLASS_PREFIX+(classindex++));
				//								this.descriptions.put(cadicompA.id, cadicompA);
				//								imply(cadicompA);
				//								cadicompA.complement = candidate;
				//								candidate.complement = cadicompA;
				//								cadicomp = cadicompA;
				//							}
				//							HashSet<Basic> newnorm = new HashSet<Basic>(normalised);
				//							newnorm.remove(candidate);
				//							initialise(newnorm, cadicomp);
				//						}
				//					}
				//				}

			}
		}
		else if(lhs instanceof Some)
		{
			Some some = (Some) lhs;
			Role role = some.role;
			Description filler = some.concept;
			Basic A = null;
			if(!(filler instanceof Basic))
			{
				A = getAtomicConcept(filler);
				normalise(filler, A);
				some = new Some(role,A);
				some.id = nonBasicID--;
			}
			else
				A = (Basic) filler;
			if(role.somes.get(A) == null)
				role.somes.put(A, some);
			if(rhs instanceof Basic)
			{
				initialise(role, A, (Basic)rhs);
			}
			else
			{
				Atomic B = getAtomicConcept(rhs);
				initialise(role, A, B);
				normalise(B, rhs);
			}
		}
		else if(lhs instanceof Basic)
		{
			if(rhs instanceof Some)
			{
				Some some = (Some) rhs;
				Role role = some.role;
				Description filler = some.concept;
				Basic B = null;
				if(!(filler instanceof Basic))
				{
					B = getAtomicConcept(filler);
					normalise(B, filler);
				}
				else
					B = (Basic)filler;
				initialise((Basic)lhs, role, B);
			}
			else if(rhs instanceof And)
			{
				And and = (And) rhs;
				for(Description operand:and.operands)
				{
					if(operand instanceof Basic)
						initialise((Basic)lhs, (Basic)operand);
					else
						normalise(lhs, operand);
				}
			}
			else
				initialise((Basic)lhs, (Basic)rhs);
		}

	}

	/**
	 * This method initialises a subsumption axiom lhs \sub rhs for reasoning
	 * @param lhs
	 * @param rhs
	 */
	protected void initialise(Basic lhs, Basic rhs)
	{
		lhs.Ohat.add(rhs.entry);
	}

	/**
	 * This method initialises a subsumption axiom lhs1 \and ... \and lhsn \sub rhs for reasoning
	 * @param lhss: the set of conjuncts on the LHS of the axiom
	 * @param rhs
	 */
	protected void initialise(HashSet<Basic> lhss, Basic rhs)
	{
		if(lhss.size() == 1)
		{
			Implies imply = rhs.entry;
			lhss.iterator().next().Ohat.add(imply);
		}
		else
		{			
			for (Basic desc : lhss)
			{
				Implies implies = new Implies();
				implies.rhs = rhs;
				for (Basic company : lhss)
				{
					if(!company.equals(desc))
						implies.lhs.add(company);
				}

				implies.id = implyID++;
				desc.Ohat.add(implies);
			}
		}
	}

	/**
	 * This method initialises a subsumption axiom A \sub \some role.B for reasoning
	 * @param A
	 * @param role
	 * @param B
	 */
	protected void initialise(Basic A, Role role, Basic B)
	{
		Some exists = role.somes.get(B);
		if(exists == null)
		{
			exists = new Some(role,B);
			exists.id = nonBasicID--;
			role.somes.put(B, exists);
		}
		A.Ohat.add(exists);

	}

	/**
	 * This method initialises a subsumption axiom \some role.A \sub B for reasoning
	 * @param role
	 * @param A
	 * @param B
	 */
	protected void initialise(Role role, Basic A, Basic B)
	{
		Some some = relOntology.roles.get(role.id).somes.get(A);
		if(some == null)
		{
			some = new Some(role, A);
			some.id = nonBasicID;
			nonBasicID--;
			descriptions.put(some.id, some);
			role.somes.put(A, some);	
		}
		some.Ohat.add(B.entry);
		if(!relOntology.largeT && !relOntology.largeA)
		{
			if(A instanceof CardinAtomic && ((CardinAtomic)A).minCardin <= RELReasonerConfiguration.cardinThreshold)
				role.cardiAtomics.add((CardinAtomic) A);

			//		// completeness only
			//		if(A.complement != null && B.complement != null)
			//		{
			//		Some newsome = elcontology.roles.get(role.inverse.id).somes.get(B.complement);
			//		if(newsome == null)
			//		{
			//			newsome = new Some(role.inverse, B.complement);
			//			newsome.id = nonbasicindex;
			//			nonbasicindex--;
			//			descriptions.put(newsome.id, newsome);
			//			role.inverse.somes.put(B.complement, newsome);
			//		}
			//		newsome.Ohat.add(A.complement.entry);
			//		}
		}
	}

	/**
	 * This method creates the queue entry ->A for concept A.
	 * @param A
	 */
	protected void imply(Basic A)
	{
		Implies simpleimply = new Implies();
		simpleimply.id = implyID++;
		simpleimply.lhs = null;
		simpleimply.rhs = A;
		A.entry = simpleimply;
	}

	/**
	 * This method is used to clean the temporal data after a duo-ontology classification
	 */
	public void clean() {
		// TODO Auto-generated method stub

		relOntology.basicConceptNum = basicID;

		HashSet<OWLClassExpression> ID2Delete = new HashSet<OWLClassExpression>();
		for(Entry<OWLClassExpression, Integer> entry:relOntology.classIDs.entrySet())
		{
			if(entry.getValue() >= basicID || entry.getValue() <= nonBasicID)
			{
				ID2Delete.add(entry.getKey());
				//				elcontology.descriptions.remove(entry.getValue());
			}
		}
		for(OWLClassExpression desc:ID2Delete)
		{
			relOntology.classIDs.remove(desc);
		}

		HashSet<Integer> desc2Delete = new HashSet<Integer>();
		for(Entry<Integer, Description> entry:relOntology.descriptions.entrySet())
		{
			if(entry.getKey() >= basicID || entry.getKey() <= nonBasicID)
			{
				desc2Delete.add(entry.getKey());
				if(entry.getValue() instanceof Some)
				{
					Some some = (Some) entry.getValue();
					Role r = some.role;
					if(some.concept instanceof Basic)
					{
						Basic basic = (Basic)some.concept;
						r.somes.remove(basic);
					}
				}
				continue;
			}
			entry.getValue().tempOhat.clear();
			if(entry.getValue() instanceof Basic)
			{
				Basic basic = (Basic) entry.getValue();
				if(basic.complement != null && basic.complement.id >= basicID)
					basic.complement = null;
				basic.tempcardins = null;
				basic.tempPredecessors.clear();
				basic.tempSubsumers.clear();
			}
		}
		for(int i = 0;i < relOntology.roleNum;i ++)
		{
			Role role = relOntology.roles.get(i);
			role.tempRelations.clear();
			HashSet<Basic> removeKey = new HashSet<Basic>();
			HashMap<Basic, Some> somes = role.somes;
			for(Basic key:somes.keySet())
				if(key.id >= basicID)
					removeKey.add(key);
			for(Basic key:removeKey)
				somes.remove(key);
		}
		for(int i:desc2Delete)
			relOntology.descriptions.remove(i);
	}

	public void nBoxPostProcessing() {
		// TODO Auto-generated method stub
		// we need to update the number of basic concepts after the ontology is closed.
		relOntology.basicConceptNum = basicID;
	}

	private void addClassID(OWLClassExpression A, int B){
		classIDs.put(A,B);
	}
}

