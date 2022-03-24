package eu.trowl.owlapi3.rel.reasoner.el;

import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import org.semanticweb.owlapi.model.AddAxiom;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLAxiom;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassAssertionAxiom;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLDataPropertyExpression;
import org.semanticweb.owlapi.model.OWLDisjointClassesAxiom;
import org.semanticweb.owlapi.model.OWLException;
import org.semanticweb.owlapi.model.OWLFunctionalDataPropertyAxiom;
import org.semanticweb.owlapi.model.OWLFunctionalObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLLiteral;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyChange;
import org.semanticweb.owlapi.model.OWLOntologyChangeListener;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLSubClassOfAxiom;
import org.semanticweb.owlapi.reasoner.AxiomNotInProfileException;
import org.semanticweb.owlapi.reasoner.BufferingMode;
import org.semanticweb.owlapi.reasoner.ClassExpressionNotInProfileException;
import org.semanticweb.owlapi.reasoner.FreshEntitiesException;
import org.semanticweb.owlapi.reasoner.FreshEntityPolicy;
import org.semanticweb.owlapi.reasoner.InconsistentOntologyException;
import org.semanticweb.owlapi.reasoner.IndividualNodeSetPolicy;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerConfiguration;
import org.semanticweb.owlapi.reasoner.ReasonerInterruptedException;
import org.semanticweb.owlapi.reasoner.TimeOutException;
import org.semanticweb.owlapi.reasoner.UnsupportedEntailmentTypeException;
import org.semanticweb.owlapi.reasoner.impl.OWLClassNode;
import org.semanticweb.owlapi.reasoner.impl.OWLClassNodeSet;
import org.semanticweb.owlapi.reasoner.impl.OWLDataPropertyNode;
import org.semanticweb.owlapi.reasoner.impl.OWLDataPropertyNodeSet;
import org.semanticweb.owlapi.reasoner.impl.OWLNamedIndividualNode;
import org.semanticweb.owlapi.reasoner.impl.OWLNamedIndividualNodeSet;
import org.semanticweb.owlapi.reasoner.impl.OWLObjectPropertyNode;
import org.semanticweb.owlapi.reasoner.impl.OWLObjectPropertyNodeSet;
import org.semanticweb.owlapi.util.Version;

import eu.trowl.owlapi3.rel.normal.classify.dl.CombinedClassifier;
import eu.trowl.owlapi3.rel.normal.factory.dl.OntologyFactory;
import eu.trowl.owlapi3.rel.normal.model.Atomic;
import eu.trowl.owlapi3.rel.normal.model.Basic;
import eu.trowl.owlapi3.rel.normal.model.Description;
import eu.trowl.owlapi3.rel.normal.model.Implies;
import eu.trowl.owlapi3.rel.normal.model.Ontology;
import eu.trowl.owlapi3.rel.normal.model.QueueEntry;
import eu.trowl.owlapi3.rel.normal.model.Ontology.Profile;
import eu.trowl.owlapi3.rel.normal.model.Role;
import eu.trowl.owlapi3.rel.normal.model.RoleConcept;
import eu.trowl.owlapi3.rel.normal.model.Singleton;
import eu.trowl.owlapi3.rel.util.RELReasonerConfiguration;

/***
 * REL reasoner for EL ontologies. 
 * @author Yuan Ren
 * @version 2014-11-25:
 */
public class RELReasoner implements OWLReasoner, OWLOntologyChangeListener{
	/*
	 * @version 2014-11-25:
	 * 1. revised getSuperClasses(), getSubClasses() and getEquivalentClasses()
	 * to handel complex expressions, especially when they are unsatisfiable.
	 * @version 2014-07-15:
	 * 1. revised classify(), isConsistent(), precomputeInference() to not throw error in isConsistent() when ontology is inconsistent.
	 * @version 2013-07-17:
	 * 1. remove ABox materialisation from precompute;
	 * 2. separate TBox completion and ABox completion;
	 * 3. separate precompute into supported precompute and current precompute;
	 * 4. introduce supported_TBox_Precompute;
	 * 5. when current_Precompute contains some ABox precompute, compute whole ABox;
	 * 6. when current_Precompute contains some TBox precompute, compute whole TBox;
	 * 7. revise precomputeInferences() to support the inferences;
	 * 8. remove classify() from the constructor();
	 * 9. add TBox, ABox parameters into classify();
	 * 10. add pre-computation to relevant methods();
	 * @version 2013-07-02:
	 * 1. update the entailment checkings to support functional datatype and object properties;
	 * @version 2013-06-12:
	 * 1. update the classify() method to return when the ontology is inconsistent;
	 * @version 2013-06-11:
	 * 1. updated the get SuperClasses, SubClasses, EquivalentClasses, 
	 * Types methods to remove singltons from direct hierarchy; 
	 * @version 2013-05-06:
	 * 1. updated methods to exclude non-original individuals in results
	 * @version 2013-04-07:
	 * 1. added configuration information;
	 * 1. added Class Assertion entailment checking support;
	 * @version 2013-01-28:
	 * 1. included OWL-DBC related methods;
	 * 2. updated OWL-DBC related methods to change Individual to Singleton;
	 * 3. include TrOWL-BGP related methods;
	 * 4. re-create as EL reasoner;
	 * @version 2012-08-19
	 * @version 2012-05-18
	 */

	protected static OntologyFactory elcfactory = null;

	// whether a buffered reasoner
	public boolean bufferred = true;

	// configuration
	public OWLReasonerConfiguration configuration = null;
	public ArrayList<OWLNamedIndividual> inconsistentIndividuals = new ArrayList<OWLNamedIndividual>();
	public final OWLOntologyManager manager;
	protected final OWLDataFactory factory;
	protected OWLOntology ontology = null;

	// bottom level satisfiable atomic classes
	protected OWLClassNodeSet leafClasses;

	// satisfiable atomic classes
	protected OWLClassNodeSet satisfiableClasses;

	// unsatisfiable atomic classes
	protected OWLClassNode unsatisfiableClasses;

	// list of buffered ontology changes
	protected List<OWLOntologyChange> changes = new ArrayList<OWLOntologyChange>();
	protected Set<OWLAxiom> toadd = new HashSet<OWLAxiom>();	
	protected Set<OWLAxiom> toremove = new HashSet<OWLAxiom>();

	// whether the reasoner will be used for BGP query answering.
	protected boolean bgp = false;

	// whether the reasoner will apply set Disjointness
	protected boolean disjointness = false;

	// whether the ontology contains meta-modelling
	protected boolean MetaOn = false;

	protected CombinedClassifier classifier;
	public Ontology relOntology;

	// bottom level satisfiable basic concepts
	protected HashSet<Basic> leafBasics;

	// satisfiable basic concepts
	HashSet<Basic> satisfiableBasics;

	protected Version version = new Version(1,5,0,0);

	// inference types
	Set<InferenceType> current_Precompute = new HashSet<InferenceType>();
	Set<InferenceType> supported_Precompute = new HashSet<InferenceType>();
	Set<InferenceType> supported_TBox_Precompute = new HashSet<InferenceType>();

	/**
	 * This method constructs an REL reasoner
	 * @param manager: input ontology manager
	 * @param ontology: input ontology
	 * @param bgp: whether the ontology will be used for BGP query answering
	 * @param MetaOn: whether the ontology contains meta-modelling
	 * @param disjoint: whether the reasoner applies set disjointness
	 */
	public RELReasoner(OWLOntologyManager manager, OWLOntology ontology, boolean bgp, boolean MetaOn, boolean disjoint) {
		super();

		this.manager = manager;
		this.factory = manager.getOWLDataFactory();
		this.ontology = ontology;
		this.bgp = bgp;
		this.MetaOn = MetaOn;
		this.disjointness = disjoint;

		// initialise inference types
		supported_Precompute.add(InferenceType.CLASS_HIERARCHY);
		supported_Precompute.add(InferenceType.DATA_PROPERTY_HIERARCHY);
		supported_Precompute.add(InferenceType.DISJOINT_CLASSES);
		supported_Precompute.add(InferenceType.OBJECT_PROPERTY_HIERARCHY);
		supported_Precompute.add(InferenceType.CLASS_ASSERTIONS);
		supported_Precompute.add(InferenceType.DIFFERENT_INDIVIDUALS);
		supported_Precompute.add(InferenceType.OBJECT_PROPERTY_ASSERTIONS);
		supported_Precompute.add(InferenceType.SAME_INDIVIDUAL);        
		supported_TBox_Precompute.add(InferenceType.CLASS_HIERARCHY);
		supported_TBox_Precompute.add(InferenceType.DATA_PROPERTY_HIERARCHY);
		supported_TBox_Precompute.add(InferenceType.DISJOINT_CLASSES);
		supported_TBox_Precompute.add(InferenceType.OBJECT_PROPERTY_HIERARCHY);

		if(bgp)
			current_Precompute.add(InferenceType.CLASS_ASSERTIONS);

		this.configuration = new RELReasonerConfiguration();

		initialiseClassifier();
		loadOntology();
	}

	// a native method to count atomic subsumptions
	public int countersubsumers(){
		return relOntology.countsubsumers();
	}

	@Override
	public void dispose() {
		// TODO Auto-generated method stub
		manager.removeOntologyChangeListener(this);
	}

	@Override
	public void flush() {
		// TODO Auto-generated method stub
		// basically reload the ontology and re-perform reasoning
		toadd = new HashSet<OWLAxiom>();
		toremove = new HashSet<OWLAxiom>();
		initialiseClassifier();
		loadOntology();
		// if current_Precompute is un-empty, compute it;
		// otherwise, classify none;
		relOntology.tBox_Classified = false;
		relOntology.aBox_Classified = false;
		precomputeInferences();
	}

	@Override
	public Node<OWLClass> getBottomClassNode() {
		// TODO Auto-generated method stub
		return getEquivalentClasses(factory.getOWLNothing());
	}

	@Override
	public Node<OWLDataProperty> getBottomDataPropertyNode() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		return new OWLDataPropertyNode();
	}

	@Override
	public Node<OWLObjectPropertyExpression> getBottomObjectPropertyNode() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		return new OWLObjectPropertyNode();
	}

	@Override
	public BufferingMode getBufferingMode() {
		// TODO Auto-generated method stub
		if(this.bufferred == true)
			return BufferingMode.BUFFERING;
		else
			return BufferingMode.NON_BUFFERING;
	}

	@Override
	public NodeSet<OWLClass> getDataPropertyDomains(OWLDataProperty arg0,
			boolean arg1){
		// TODO Auto-generated method stub
		// todo
		// not supported yet
//		System.out.print("getDataPropertyDomains method is not supported yet!");
		return new OWLClassNodeSet();
	}

	@Override
	public Set<OWLLiteral> getDataPropertyValues(OWLNamedIndividual arg0,
			OWLDataProperty arg1) {
		// TODO Auto-generated method stub
		// todo
		// unsupported yet
//		System.out.println("getDataPropertyValues method is not supported yet!");
		return new HashSet<OWLLiteral>();
	}

	@Override
	public NodeSet<OWLNamedIndividual> getDifferentIndividuals(
			OWLNamedIndividual arg0) throws InconsistentOntologyException,
			FreshEntitiesException, ReasonerInterruptedException,
			TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.aBox_Classified)
			precomputeInferences(InferenceType.DIFFERENT_INDIVIDUALS);
		OWLNamedIndividualNodeSet indis = new OWLNamedIndividualNodeSet();
		Singleton indi = getSingleton(arg0);
		if(indi != null)
		{
			for(Singleton diff:indi.differentIndividuals)
			{
				OWLNamedIndividualNode node = new OWLNamedIndividualNode();
				for(Basic equa:diff.equivalence)
					if(equa.original && equa instanceof Singleton)
						node.add(factory.getOWLNamedIndividual(equa.asSingleton().uri));
				if(node.getSize()>0)
					indis.addNode(node);
			}
		}
		return indis;
	}

	@Override
	public NodeSet<OWLClass> getDisjointClasses(OWLClassExpression concept)
			throws ReasonerInterruptedException, TimeOutException,
			FreshEntitiesException, InconsistentOntologyException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.DISJOINT_CLASSES);
		OWLClassNodeSet	disjoints = new OWLClassNodeSet();
		//		Description desc = getDescription(concept);
		//		Atomic bot = (Atomic) elcontology.descriptions.get(0);
		//
		////		boolean duo = false;
		////		if(desc == null || !(desc instanceof Atomic))
		////		{
		////			// apply duo classification approach
		////			duo = true;
		////			// add an additional axiom tempC \sub X
		////			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempC"));
		////			OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(tempclass, concept);
		////			Entry<Basic, Basic> entry = elcfactory.loadAxiom(axiom);
		////
		////			// incrementally classify the new ontology
		////			CombinedClassifier classifier = new CombinedClassifier();
		////			classifier.ontology = elcontology;
		////			classifier.classify_duo();
		////
		////			desc = (Atomic) entry.getKey();
		////
		////		}
		////		
		////		
		////		
		////				Atomic atom = (Atomic)desc;
		////				HashSet<Basic> subsumers = new HashSet<Basic>();
		////				if(atom.equivalence.contains(bot))
		////					return satisfiable;
		//////				if(atom.equivalence.contains(top))
		//////					return 
		////				else
		////				{
		////					// todo: update EL complement part
		////					for(Basic sub:atom.subsumers)
		////					{
		////						if(sub.complement.original && !subsumers.contains(sub.complement))
		////						{
		////							subsumers.addAll(sub.complement.equivalence);
		////						}
		////					}					
		////					for(Basic sub:atom.tempSubsumers)
		////					{
		////						if(sub.complement.original && !subsumers.contains(sub.complement))
		////						{
		////							subsumers.addAll(sub.complement.equivalence);
		////						}
		////					}					
		////				}
		////
		////
		////				while(subsumers.size()>0)
		////				{
		////					Basic sub = subsumers.iterator().next();
		////					subsumers.removeAll(sub.equivalence);
		////					OWLClassNode ancestor = new OWLClassNode();
		////					for(Basic eq:sub.equivalence)
		////						if(eq instanceof Atomic && ((Atomic)eq).original)
		////							ancestor.add(factory.getOWLClass(((Atomic)eq).uri));							
		////					if(ancestor.getSize() > 0)
		////						disjoints.addNode(ancestor);
		////				}
		////
		////				// clean the classifier, factory, ontology, etc for duo-classification.
		////				if(duo)
		////					elcfactory.clean();

		System.out.println("getDisjointClasses method is not supported yet!");
		return disjoints;
	}

	@Override
	public NodeSet<OWLDataProperty> getDisjointDataProperties(
			OWLDataPropertyExpression arg0)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.DATA_PROPERTY_HIERARCHY);
		OWLDataPropertyNodeSet props = new OWLDataPropertyNodeSet();
		Role role = getRole(arg0);
		if(role != null)
		{
			for(Role diff:role.disjoints)
			{
				OWLDataPropertyNode node = new OWLDataPropertyNode();
				for(Role equa:diff.equivalence)
					if(equa.original)
						node.add(factory.getOWLDataProperty(equa.uri));
				if(node.getSize()>0)
					props.addNode(node);
			}
		}
		return props;
	}

	@Override
	public NodeSet<OWLObjectPropertyExpression> getDisjointObjectProperties(
			OWLObjectPropertyExpression arg0)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {		
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.OBJECT_PROPERTY_HIERARCHY);
		OWLObjectPropertyNodeSet props = new OWLObjectPropertyNodeSet();
		Role role = getRole(arg0);
		if(role != null)
		{
			for(Role diff:role.disjoints)
			{
				OWLObjectPropertyNode node = new OWLObjectPropertyNode();
				for(Role equa:diff.equivalence)
					if(equa.original)
						node.add(factory.getOWLObjectProperty(equa.uri));
				if(node.getSize()>0)
					props.addNode(node);
			}
		}
		return props;
	}

	@Override
	public Node<OWLClass> getEquivalentClasses(OWLClassExpression concept) {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.CLASS_HIERARCHY);
		OWLClassNode equivalence = new OWLClassNode();
		Description desc = getDescription(concept);
		Atomic bot = (Atomic) relOntology.descriptions.get(0);
		boolean duo = false;
		if(desc == null || !(desc instanceof Atomic))
		{
			// apply duo-ontology classification approach
			duo = true;
			// add an additional axiom X \equiv tempC
			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempC"));
			Entry<Basic, Basic> entry = elcfactory.loadAxiom(tempclass, concept);

			// incrementally classify the new ontology
			CombinedClassifier classifier = new CombinedClassifier();
			classifier.ontology = relOntology;
			classifier.completion_duo(relOntology.aBox_Classified);

			desc = (Atomic) entry.getValue();
		}

		// todo
		// the tempC equivalence needs to be post-processed after reasoning

		Atomic atomic = (Atomic) desc;
		if((atomic.equivalence.contains(bot) || atomic.subsumers.contains(bot) || atomic.tempSubsumers.contains(bot)) && atomic.id != 0)
			return getEquivalentClasses(factory.getOWLNothing());
		if(atomic.id == 0)
			return unsatisfiableClasses;
		for(Basic eq:atomic.equivalence)
			if(eq instanceof Atomic && eq.original)
				equivalence.add(factory.getOWLClass(((Atomic)eq).uri));
		for(Basic sup:atomic.tempSubsumers)
			if(sup instanceof Atomic && sup.original && (sup.subsumers.contains(atomic) || sup.tempSubsumers.contains(atomic)))
				equivalence.add(factory.getOWLClass(((Atomic)sup).uri));

		// clean the classifier, factory, ontology, etc for duo-ontology classification.
		if(duo)
			elcfactory.clean();

		return equivalence;
	}

	@Override
	public Node<OWLDataProperty> getEquivalentDataProperties(
			OWLDataProperty arg0) throws InconsistentOntologyException,
			FreshEntitiesException, ReasonerInterruptedException,
			TimeOutException {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.DATA_PROPERTY_HIERARCHY);
		OWLDataPropertyNode equivalence = new OWLDataPropertyNode();
		Role desc = getRole(arg0);
		if(desc != null)
		{
			for(Role eq:desc.equivalence)
				if(eq.original)
					equivalence.add(factory.getOWLDataProperty(eq.uri));
		}
		return equivalence;
	}

	@Override
	public Node<OWLObjectPropertyExpression> getEquivalentObjectProperties(
			OWLObjectPropertyExpression arg0)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.OBJECT_PROPERTY_HIERARCHY);
		OWLObjectPropertyNode equivalence = new OWLObjectPropertyNode();
		Role desc = getRole(arg0);
		if(desc != null)
		{
			for(Role eq:desc.equivalence)
				if(eq.original)
					equivalence.add(factory.getOWLObjectProperty(eq.uri));
		}
		return equivalence;
	}

	@Override
	public FreshEntityPolicy getFreshEntityPolicy() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		//		System.out.println("getFreshEntityPolicy is not supported yet.");
		return this.configuration.getFreshEntityPolicy();
	}

	@Override
	public IndividualNodeSetPolicy getIndividualNodeSetPolicy() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		//		System.out.println("getIndividualNodePolicy is not supported yet.");
		return this.configuration.getIndividualNodeSetPolicy();
	}

	@Override
	public NodeSet<OWLNamedIndividual> getInstances(OWLClassExpression arg0, boolean arg1) {
		// TODO Auto-generated method stub
		// now only returns indirect instances
		// todo
		return getIndividuals(arg0);
	}

	@Override
	public Node<OWLObjectPropertyExpression> getInverseObjectProperties(
			OWLObjectPropertyExpression arg0)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.OBJECT_PROPERTY_HIERARCHY);
		Role role = getRole(arg0);
		if(role != null)
		{
			OWLObjectPropertyNode inverse = new OWLObjectPropertyNode();
			for(Role invrole:role.inverse.equivalence)
				if(invrole.original)
					inverse.add(factory.getOWLObjectProperty(invrole.uri));
			return inverse;
		}
		return new OWLObjectPropertyNode();
	}

	@Override
	public NodeSet<OWLClass> getObjectPropertyDomains(
			OWLObjectPropertyExpression arg0, boolean arg1)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		OWLClassExpression exp = factory.getOWLObjectSomeValuesFrom(arg0, factory.getOWLThing());
		return getSuperClasses(exp, arg1);
	}

	public Map<OWLNamedIndividual, Set<OWLNamedIndividual>> getObjectPropertyInstances(
			OWLObjectProperty owlOP) {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.aBox_Classified)
			precomputeInferences(InferenceType.OBJECT_PROPERTY_ASSERTIONS);
		Role role = getRole(owlOP);
		Map<OWLNamedIndividual, Set<OWLNamedIndividual>> insts = new HashMap<OWLNamedIndividual, Set<OWLNamedIndividual>>();
		for(Singleton indi:role.subjects)
		{
			if(!indi.original)
				continue;
			OWLNamedIndividual sub = factory.getOWLNamedIndividual(indi.uri);
			HashSet<OWLNamedIndividual> objs = new HashSet<OWLNamedIndividual>();
			for(Basic obj:role.Relations.get(indi))
			{
				if(obj.original && obj instanceof Singleton)
				{
					objs.add(factory.getOWLNamedIndividual(obj.uri));
				}
			}
			if(objs.size()>0)
				insts.put(sub, objs);
		}
		return insts;
	}

	@Override
	public NodeSet<OWLClass> getObjectPropertyRanges(
			OWLObjectPropertyExpression arg0, boolean arg1)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		OWLClassExpression exp = factory.getOWLObjectSomeValuesFrom(arg0.getInverseProperty(), factory.getOWLThing());
		return getSuperClasses(exp, arg1);
	}

	@Override
	public NodeSet<OWLNamedIndividual> getObjectPropertyValues(OWLNamedIndividual arg0,
			OWLObjectPropertyExpression arg1) {
		// TODO Auto-generated method stub
		// todo
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.aBox_Classified)
			precomputeInferences(InferenceType.OBJECT_PROPERTY_ASSERTIONS);
		OWLNamedIndividualNodeSet toreturn = new OWLNamedIndividualNodeSet();
		Singleton indi = getSingleton(arg0);
		Role role = getRole(arg1);
		if(indi != null && role != null)
		{
			// since we don't derive all (indi,obj):role
			//  we need to find objs in subroles of role
			for(Role subRole:role.subroles)
			{
				if(subRole.Relations.get(indi)!=null)
				{
					HashSet<Basic> objs = new HashSet<Basic>(subRole.Relations.get(indi));
					while(!objs.isEmpty())
					{
						Basic bsc = objs.iterator().next();
						if(bsc instanceof Singleton)
						{
							Singleton obj = (Singleton)bsc;
							OWLNamedIndividualNode node = new OWLNamedIndividualNode();
							for(Basic equa:obj.equivalence)
							{
								if(equa instanceof Singleton)
									node.add(factory.getOWLNamedIndividual(equa.asSingleton().uri));
							}
							if(node.getSize() > 0)
								toreturn.addNode(node);
							objs.removeAll(obj.equivalence);
						}
						objs.remove(bsc);
						objs.removeAll(bsc.equivalence);
					}
				}
			}
			// similarly, we need to find objs in the inverse roles of role
			for(RoleConcept rc:indi.predecessors)
			{
				if(rc.role.inverse.subsumers.contains(role) && rc.concept instanceof Singleton)
				{
					OWLNamedIndividualNode node = new OWLNamedIndividualNode();
					for(Basic basic:rc.concept.equivalence)
					{
						if(basic.original)
							if(basic instanceof Singleton)
								node.add(factory.getOWLNamedIndividual(basic.asSingleton().uri));
					}
					if(node.getSize() > 0)
						toreturn.addNode(node);					
				}
			}
		}
		return toreturn;
	}

	@Override
	public Set<OWLAxiom> getPendingAxiomAdditions() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		return toadd;
	}

	@Override
	public Set<OWLAxiom> getPendingAxiomRemovals() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		return toremove;
	}

	@Override
	public List<OWLOntologyChange> getPendingChanges() {
		// TODO Auto-generated method stub
		return changes;
	}

	@Override
	public Set<InferenceType> getPrecomputableInferenceTypes() {
		// TODO Auto-generated method stub
		return supported_Precompute;
	}

	@Override
	public String getReasonerName() {
		// TODO Auto-generated method stub
		return "REL";
	}

	@Override
	public Version getReasonerVersion() {
		// TODO Auto-generated method stub
		return version;
	}

	@Override
	public OWLOntology getRootOntology() {
		// TODO Auto-generated method stub
		return ontology;
	}

	@Override
	public Node<OWLNamedIndividual> getSameIndividuals(OWLNamedIndividual arg0)
			throws InconsistentOntologyException, FreshEntitiesException,
			ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.aBox_Classified)
			precomputeInferences(InferenceType.SAME_INDIVIDUAL);
		OWLNamedIndividualNode node = new OWLNamedIndividualNode();
		Singleton indi = getSingleton(arg0);
		if(indi != null)
		{
			for(Basic equa:indi.equivalence)
			{
				if(equa.original && equa instanceof Singleton)
					node.add(factory.getOWLNamedIndividual(((Singleton)equa).uri));
			}
		}
		return node;
	}

	@Override
	public NodeSet<OWLClass> getSubClasses(OWLClassExpression concept, boolean direct) {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.CLASS_HIERARCHY);
		OWLClassNodeSet	descendants = new OWLClassNodeSet();
		Description desc = getDescription(concept);
		Atomic bot = (Atomic) relOntology.descriptions.get(0);
		boolean duo = false;
		if(desc == null || !(desc instanceof Atomic))
		{
			// apply duo-ontology classification approach
			duo = true;
			// add an additional axiom X \sub tempC
			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempC"));
			OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(concept, tempclass);
			Entry<Basic, Basic> entry = elcfactory.loadAxiom(axiom);

			// incrementally classify the new ontology
			CombinedClassifier classifier = new CombinedClassifier();
			classifier.ontology = relOntology;
			classifier.completion_duo(relOntology.aBox_Classified);

			desc = (Atomic) entry.getValue();
		}

		Atomic atom = (Atomic) desc;
		if(atom.equivalence.contains(bot) || atom.tempSubsumers.contains(bot))
			return descendants;
		HashSet<Basic> subsumees = new HashSet<Basic>();
		if(direct)
		{
			// if only ask for direct subclasses, need to remove indirect ones
			for(Basic sub:relOntology.originalNamedConcepts)
			{
				if(!sub.subsumers.contains(bot) && !sub.tempSubsumers.contains(bot) && !atom.equivalence.contains(sub) && !subsumees.contains(sub) && (sub.subsumers.contains(atom) || sub.tempSubsumers.contains(atom)))
				{
					boolean toadd = true;
					for(Basic subsub:sub.subsumers)
						if(subsub instanceof Atomic && subsub.original && !sub.equivalence.contains(subsub) && !atom.equivalence.contains(subsub) && (subsub.subsumers.contains(atom) || subsub.tempSubsumers.contains(atom)))
						{
							toadd = false;
							break;
						}
					for(Basic subsub:sub.tempSubsumers)
						if(subsub instanceof Atomic && subsub.original && !sub.equivalence.contains(subsub) && !atom.equivalence.contains(subsub) && (subsub.subsumers.contains(atom) || subsub.tempSubsumers.contains(atom)))
						{
							toadd = false;
							break;
						}
					if(toadd)
						subsumees.addAll(sub.equivalence);
				}
			}
		}
		else
		{
			for(Basic sub:relOntology.originalNamedConcepts)
			{
				if((sub.tempSubsumers.contains(atom) || sub.subsumers.contains(atom)) && !sub.equivalence.contains(atom))
					subsumees.add(sub);
			}
		}
		while(subsumees.size()>0)
		{
			Basic sub = subsumees.iterator().next();
			subsumees.removeAll(sub.equivalence);
			OWLClassNode descendant = new OWLClassNode();
			for(Basic eq:sub.equivalence)
				if(eq instanceof Atomic && ((Atomic)eq).original)
					descendant.add(factory.getOWLClass(((Atomic)eq).uri));							
			if(descendant.getSize() > 0)
				descendants.addNode(descendant);
		}
		if(!direct || descendants.getFlattened().size() == 0)
			descendants.addNode(unsatisfiableClasses);

		// clean the classifier, factory, ontology, etc for duo-ontology classification.
		if(duo)
			elcfactory.clean();

		return descendants;
	}

	@Override
	public NodeSet<OWLDataProperty> getSubDataProperties(OWLDataProperty arg0,
			boolean direct) throws InconsistentOntologyException,
			FreshEntitiesException, ReasonerInterruptedException,
			TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.DATA_PROPERTY_HIERARCHY);
		OWLDataPropertyNodeSet	descendants = new OWLDataPropertyNodeSet();
		Role role = getRole(arg0);
		if(role != null)
		{
			HashSet<Role> subsumees = new HashSet<Role>();
			if(direct)
				for(Role sub:relOntology.roles.values())
				{
					if(!role.equivalence.contains(sub) && !subsumees.contains(sub) && sub.subsumers.contains(role))
					{
						boolean toadd = true;
						for(Role subsub:sub.subsumers)
							if(subsub.original && !sub.equivalence.contains(subsub) && !role.equivalence.contains(subsub) && subsub.subsumers.contains(role))
							{
								toadd = false;
								break;
							}
						if(toadd)
							subsumees.addAll(sub.equivalence);
					}
				}
			else
				for(Role sub:relOntology.roles.values())
					if(sub.subsumers.contains(role))
						subsumees.add(sub);
			while(subsumees.size()>0)
			{
				Role sub = subsumees.iterator().next();
				subsumees.removeAll(sub.equivalence);
				OWLDataPropertyNode descendant = new OWLDataPropertyNode();
				for(Role eq:sub.equivalence)
					if(eq.original)
						descendant.add(factory.getOWLDataProperty(eq.uri));							
				if(descendant.getSize() > 0)
					descendants.addNode(descendant);
			}
		}
		return descendants;	

	}

	@Override
	public NodeSet<OWLObjectPropertyExpression> getSubObjectProperties(
			OWLObjectPropertyExpression arg0, boolean direct)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.OBJECT_PROPERTY_HIERARCHY);
		OWLObjectPropertyNodeSet	descendants = new OWLObjectPropertyNodeSet();
		Role role = getRole(arg0);
		if(role != null)
		{
			HashSet<Role> subsumees = new HashSet<Role>();
			if(direct)
				for(Role sub:relOntology.roles.values())
				{
					if(!role.equivalence.contains(sub) && !subsumees.contains(sub) && sub.subsumers.contains(role))
					{
						boolean toadd = true;
						for(Role subsub:sub.subsumers)
							if(subsub.original && !sub.equivalence.contains(subsub) && !role.equivalence.contains(subsub) && subsub.subsumers.contains(role))
							{
								toadd = false;
								break;
							}
						if(toadd)
							subsumees.addAll(sub.equivalence);
					}
				}
			else
				for(Role sub:relOntology.roles.values())
					if(sub.subsumers.contains(role))
						subsumees.add(sub);
			while(subsumees.size()>0)
			{
				Role sub = subsumees.iterator().next();
				subsumees.removeAll(sub.equivalence);
				OWLObjectPropertyNode descendant = new OWLObjectPropertyNode();
				for(Role eq:sub.equivalence)
					if(eq.original)
						descendant.add(factory.getOWLObjectProperty(eq.uri));							
				if(descendant.getSize() > 0)
					descendants.addNode(descendant);
			}
		}
		return descendants;
	}

	@Override
	public NodeSet<OWLClass> getSuperClasses(OWLClassExpression concept,
			boolean direct) throws InconsistentOntologyException,
			ClassExpressionNotInProfileException, FreshEntitiesException,
			ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.CLASS_HIERARCHY);
		OWLClassNodeSet	ancestors = new OWLClassNodeSet();
		Description desc = getDescription(concept);
		Atomic bot = (Atomic) relOntology.descriptions.get(0);
		boolean duo = false;
		if(desc == null || !(desc instanceof Atomic))
		{
			// apply duo-ontology classification approach
			duo = true;
			// add an additional axiom tempC \sub X
			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempC"));
			OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(tempclass, concept);
			Entry<Basic, Basic> entry = elcfactory.loadAxiom(axiom);

			// incrementally classify the new ontology
			CombinedClassifier classifier = new CombinedClassifier();
			classifier.ontology = relOntology;
			classifier.completion_duo(relOntology.aBox_Classified);

			desc = (Atomic) entry.getKey();

		}

		Atomic atom = (Atomic)desc;
		HashSet<Basic> subsumers = new HashSet<Basic>();
		if(direct)
		{
			if(atom.equivalence.contains(bot) || atom.tempSubsumers.contains(bot))
				return leafClasses;
			for(Basic sub:atom.subsumers)
			{
				if(sub instanceof Atomic && sub.original && !atom.equivalence.contains(sub) && !subsumers.contains(sub))
				{
					boolean toadd = true;
					for(Basic sub2:atom.subsumers)
						if(sub2 instanceof Atomic && sub2.original && !atom.equivalence.contains(sub2) && !sub.equivalence.contains(sub2) && (sub2.subsumers.contains(sub) || sub2.tempSubsumers.contains(sub)))
						{
							toadd =false;
							break;
						}
					for(Basic sub2:atom.tempSubsumers)
						if(sub2 instanceof Atomic && sub2.original && !atom.equivalence.contains(sub2) && !sub.equivalence.contains(sub2) && (sub2.subsumers.contains(sub) || sub2.tempSubsumers.contains(sub)))
						{
							toadd =false;
							break;
						}
					if(toadd)
						subsumers.addAll(sub.equivalence);
				}
			}
			for(Basic sub:atom.tempSubsumers)
			{
				if(sub instanceof Atomic && sub.original && !atom.equivalence.contains(sub) && !subsumers.contains(sub))
				{
					boolean toadd = true;
					for(Basic sub2:atom.subsumers)
						if(sub2 instanceof Atomic && sub2.original && !atom.equivalence.contains(sub2) && !sub.equivalence.contains(sub2) && (sub2.subsumers.contains(sub) || sub2.tempSubsumers.contains(sub)))
						{
							toadd =false;
							break;
						}
					for(Basic sub2:atom.tempSubsumers)
						if(sub2 instanceof Atomic && sub2.original && !atom.equivalence.contains(sub2) && !sub.equivalence.contains(sub2) && (sub2.subsumers.contains(sub) || sub2.tempSubsumers.contains(sub)))
						{
							toadd =false;
							break;
						}
					if(toadd)
						subsumers.addAll(sub.equivalence);
				}
			}
		}
		else
		{
			if(atom.equivalence.contains(bot) || atom.tempSubsumers.contains(bot))
				return satisfiableClasses;
			for(Basic sub:atom.subsumers)
				if(sub instanceof Atomic && !atom.equivalence.contains(sub) && sub.original)
					subsumers.add(sub);
			for(Basic sub:atom.tempSubsumers)
				if(sub instanceof Atomic && !atom.equivalence.contains(sub) && sub.original)
					subsumers.add(sub);
		}
		while(subsumers.size()>0)
		{
			Basic sub = subsumers.iterator().next();
			subsumers.removeAll(sub.equivalence);
			OWLClassNode ancestor = new OWLClassNode();
			for(Basic eq:sub.equivalence)
				if(eq instanceof Atomic && ((Atomic)eq).original)
					ancestor.add(factory.getOWLClass(((Atomic)eq).uri));							
			if(ancestor.getSize() > 0)
				ancestors.addNode(ancestor);
		}

		// clean the classifier, factory, ontology, etc for duo-ontology classification.
		if(duo)
			elcfactory.clean();

		return ancestors;
	}

	@Override
	public NodeSet<OWLDataProperty> getSuperDataProperties(
			OWLDataProperty arg0, boolean arg1)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.DATA_PROPERTY_HIERARCHY);
		OWLDataPropertyNodeSet	ancestors = new OWLDataPropertyNodeSet();
		Role role = getRole(arg0);
		if(role != null)
		{
			HashSet<Role> subsumers = new HashSet<Role>();
			if(arg1)
			{
				for(Role sub:role.subsumers)
					if(sub.original && !role.equivalence.contains(sub) && !subsumers.contains(sub))
					{
						boolean toadd = true;
						for(Role sub2:role.subsumers)
							if(sub2.original && !role.equivalence.contains(sub2) && !sub.equivalence.contains(sub2) && sub2.subsumers.contains(sub))
							{
								toadd =false;
								break;
							}
						if(toadd)
							subsumers.addAll(sub.equivalence);
					}
			}
			else
				for(Role sub:role.subsumers)
					subsumers.add(sub);

			while(subsumers.size()>0)
			{
				Role sub = subsumers.iterator().next();
				subsumers.removeAll(sub.equivalence);
				OWLDataPropertyNode ancestor = new OWLDataPropertyNode();
				for(Role eq:sub.equivalence)
					if(eq.original)
						ancestor.add(factory.getOWLDataProperty(eq.uri));							
				if(ancestor.getSize() > 0)
					ancestors.addNode(ancestor);
			}
		}
		return ancestors;
	}

	@Override
	public NodeSet<OWLObjectPropertyExpression> getSuperObjectProperties(
			OWLObjectPropertyExpression arg0, boolean arg1)
					throws InconsistentOntologyException, FreshEntitiesException,
					ReasonerInterruptedException, TimeOutException {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.OBJECT_PROPERTY_HIERARCHY);
		OWLObjectPropertyNodeSet	ancestors = new OWLObjectPropertyNodeSet();
		Role role = getRole(arg0);
		if(role != null)
		{
			HashSet<Role> subsumers = new HashSet<Role>();
			if(arg1)
			{
				for(Role sub:role.subsumers)
					if(sub.original && !role.equivalence.contains(sub) && !subsumers.contains(sub))
					{
						boolean toadd = true;
						for(Role sub2:role.subsumers)
							if(sub2.original && !role.equivalence.contains(sub2) && !sub.equivalence.contains(sub2) && sub2.subsumers.contains(sub))
							{
								toadd =false;
								break;
							}
						if(toadd)
							subsumers.addAll(sub.equivalence);
					}
			}
			else
				for(Role sub:role.subsumers)
					subsumers.add(sub);

			while(subsumers.size()>0)
			{
				Role sub = subsumers.iterator().next();
				subsumers.removeAll(sub.equivalence);
				OWLObjectPropertyNode ancestor = new OWLObjectPropertyNode();
				for(Role eq:sub.equivalence)
					if(eq.original)
						ancestor.add(factory.getOWLObjectProperty(eq.uri));							
				if(ancestor.getSize() > 0)
					ancestors.addNode(ancestor);
			}
		}
		return ancestors;
	}

	@Override
	public long getTimeOut() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		//		System.out.println("getTimeOut is not supported yet.");
		return this.configuration.getTimeOut();
	}

	@Override
	public Node<OWLClass> getTopClassNode() {
		// TODO Auto-generated method stub
		return getEquivalentClasses(factory.getOWLThing());
	}

	@Override
	public Node<OWLDataProperty> getTopDataPropertyNode() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		System.out.println("getTopDataPropertyNode is not supported yet.");
		return new OWLDataPropertyNode();
	}

	@Override
	public Node<OWLObjectPropertyExpression> getTopObjectPropertyNode() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		System.out.print("getTopObjectPropertyNode is not supported yet.");
		return new OWLObjectPropertyNode();
	}

	@Override
	public NodeSet<OWLClass> getTypes(OWLNamedIndividual arg0, boolean arg1) {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.aBox_Classified)
			precomputeInferences(InferenceType.CLASS_ASSERTIONS);
		OWLClassNodeSet types = new OWLClassNodeSet();
		Singleton indi = getSingleton(arg0);
		if(indi == null)
			return types;
		Atomic bot = (Atomic) relOntology.descriptions.get(0);
		HashSet<Atomic> classes = new HashSet<Atomic>();
		if(indi.subsumers.contains(bot)){
			classes = relOntology.originalNamedConcepts;
		}
		else
			for(Basic cls:indi.subsumers)
				if(cls instanceof Atomic && cls.original)
					classes.add((Atomic) cls);
		if(arg1 == true)
		{
			HashSet<Basic> toremove = new HashSet<Basic>(classes);
			for(Basic basic:toremove)
			{
				for(Basic basic2:toremove)
				{
					if(basic.subsumers.contains(basic2) && !basic.equivalence.contains(basic2))
						classes.removeAll(basic2.equivalence);
				}
			}
		}

		while(classes.size()>0)
		{
			Basic sub = classes.iterator().next();
			classes.removeAll(sub.equivalence);
			OWLClassNode type = new OWLClassNode();
			for(Basic eq:sub.equivalence)
				if(eq instanceof Atomic && ((Atomic)eq).original)
					type.add(factory.getOWLClass(((Atomic)eq).uri));							
			if(type.getSize() > 0)
				types.addNode(type);
		}
		return types;
	}

	@Override
	public Node<OWLClass> getUnsatisfiableClasses() {
		// TODO Auto-generated method stub
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.CLASS_HIERARCHY);
		return unsatisfiableClasses;
	}

	public boolean hasObjectPropertyRelationship(OWLNamedIndividual ind1,
			OWLObjectProperty ope, OWLNamedIndividual ind2) {
		// TODO Auto-generated method stub
		Singleton sub = getSingleton(ind1);
		Role role = getRole(ope);
		Singleton obj = getSingleton(ind2);

		if(sub != null && role != null && role.subjects.contains(sub))
			return role.Relations.get(sub).contains(obj);

		return false;
	}

	@Override
	public void interrupt() {
		// TODO Auto-generated method stub
		// todo
		// not supported yet
		System.out.println("interrupt is not supported yet.");
	}

	@Override
	public boolean isConsistent() {
		// TODO Auto-generated method stub
		if(relOntology.consistency)
			if(!relOntology.aBox_Classified)
				//			precomputeInferences(InferenceType.CLASS_ASSERTIONS);
			{
				current_Precompute.addAll(supported_Precompute);
				// if TBox not classified and ABox not classified, then classify both;
				// if TBox classified and ABox not, then classify only ABox;
				// if TBox not classified and ABox classified, impossible;
				// if TBox classified and ABox classified, then classify none;
				classify(!relOntology.tBox_Classified,!relOntology.aBox_Classified);
			}
		return relOntology.consistency;
	}

	@Override
	public boolean isEntailed(OWLAxiom arg0)
			throws ReasonerInterruptedException,
			UnsupportedEntailmentTypeException, TimeOutException,
			AxiomNotInProfileException, FreshEntitiesException {
		// TODO Auto-generated method stub
		// todo
		// only support limited types of checking
		if(arg0 instanceof OWLSubClassOfAxiom)
			return entail((OWLSubClassOfAxiom)arg0);
		else if(arg0 instanceof OWLClassAssertionAxiom)
			return entail((OWLClassAssertionAxiom)arg0);
		else if(arg0 instanceof OWLDisjointClassesAxiom)
			return entail((OWLDisjointClassesAxiom)arg0);
		else if(arg0 instanceof OWLFunctionalDataPropertyAxiom)
			return entail((OWLFunctionalDataPropertyAxiom)arg0);
		else if(arg0 instanceof OWLFunctionalObjectPropertyAxiom)
			return entail((OWLFunctionalObjectPropertyAxiom)arg0);
		System.out.println("This type of entailment checking is not supported yet");
		throw new UnsupportedEntailmentTypeException(arg0);
	}

	@Override
	public boolean isEntailed(Set<? extends OWLAxiom> arg0)
			throws ReasonerInterruptedException,
			UnsupportedEntailmentTypeException, TimeOutException,
			AxiomNotInProfileException, FreshEntitiesException {
		// TODO Auto-generated method stub
		// todo
		for(OWLAxiom axiom:arg0)
		{
			if(!isEntailed(axiom))
				return false;
		}
		return true;
	}

	@Override
	public boolean isEntailmentCheckingSupported(AxiomType<?> arg0) {
		// TODO Auto-generated method stub
		// todo
		if(arg0.equals(AxiomType.CLASS_ASSERTION) 
				|| arg0.equals(AxiomType.SUBCLASS_OF)
				|| arg0.equals(AxiomType.DISJOINT_CLASSES)
				|| arg0.equals(AxiomType.FUNCTIONAL_DATA_PROPERTY)
				|| arg0.equals(AxiomType.FUNCTIONAL_OBJECT_PROPERTY))
			return true;
		return false;
	}


	public boolean isoriginal(OWLClass concept) {
		// TODO Auto-generated method stub
		Basic elpconcept = (Basic) getDescription(concept);
		if(elpconcept != null)
			return elpconcept.original;
		return false;
	}

	@Override
	public boolean isPrecomputed(InferenceType arg0) {
		// TODO Auto-generated method stub
		return current_Precompute.contains(arg0);
	}

	@Override
	public boolean isSatisfiable(OWLClassExpression arg0) {
		// TODO Auto-generated method stub

		OWLSubClassOfAxiom axiom1 = factory.getOWLSubClassOfAxiom(arg0, factory.getOWLNothing());
		return !entail(axiom1);
	}

	@Override
	public void ontologiesChanged(List<? extends OWLOntologyChange> arg0) {
		// TODO Auto-generated method stub
		if(bufferred)
		{
			for(OWLOntologyChange change:arg0)
			{
				if(change instanceof AddAxiom)
					toadd.add(change.getAxiom());
				else
					toremove.add(change.getAxiom());
			}
			changes.addAll(arg0);
		}
		else
		{
			loadOntology();
			// if current_Precompute is un-empty, compute it;
			// otherwise, classify none;
			relOntology.tBox_Classified = false;
			relOntology.aBox_Classified = false;
			precomputeInferences();
		}

	}


	@Override
	public void precomputeInferences(InferenceType... arg0)
			throws ReasonerInterruptedException, TimeOutException,
			InconsistentOntologyException {
		// TODO Auto-generated method stub
		// add into the current_Precompute
		for(InferenceType type:arg0)
		{
			if(!supported_Precompute.contains(type))
				System.out.println("REL does not support precomputation of this inference type yet. It will be ignored.");
			else current_Precompute.add(type);
		}
		// decide if want to do ABox reasoning
		if(current_Precompute.contains(InferenceType.CLASS_ASSERTIONS)
				|| current_Precompute.contains(InferenceType.DIFFERENT_INDIVIDUALS)
				|| current_Precompute.contains(InferenceType.OBJECT_PROPERTY_ASSERTIONS)
				|| current_Precompute.contains(InferenceType.SAME_INDIVIDUAL))
		{
			current_Precompute.addAll(supported_Precompute);
			// if TBox not classified and ABox not classified, then classify both;
			// if TBox classified and ABox not, then classify only ABox;
			// if TBox not classified and ABox classified, impossible;
			// if TBox classified and ABox classified, then classify none;
			classify(!relOntology.tBox_Classified,!relOntology.aBox_Classified);
		}
		// decide if want to do TBox reasoning only
		else if(current_Precompute.contains(InferenceType.CLASS_HIERARCHY)
				|| current_Precompute.contains(InferenceType.DATA_PROPERTY_HIERARCHY)
				|| current_Precompute.contains(InferenceType.DISJOINT_CLASSES)
				|| current_Precompute.contains(InferenceType.OBJECT_PROPERTY_HIERARCHY))
		{
			current_Precompute.addAll(supported_TBox_Precompute);
			// if TBox not classified, then classify TBox;
			// if TBox classified, then classify none;
			classify(!relOntology.tBox_Classified,false);
		}
		//		if(!elcontology.consistency || inconsistent())
		if(!relOntology.consistency)
			throw(new InconsistentOntologyException());

	}

	private boolean inconsistent() {
		// TODO Auto-generated method stub
		Basic bot = (Basic) relOntology.descriptions.get(0);
		for(Integer indi:relOntology.individualIDs.values())
		{
			Singleton single = (Singleton) relOntology.descriptions.get(indi);
			//			if(single.uri.getFragment().toString().equals("A"))
			//				System.out.println();
			ArrayList<Basic> imps = new ArrayList<Basic>();
			for(QueueEntry entry:single.Ohat)
				if(entry instanceof Implies)
				{
					Implies imp = (Implies) entry;
					if(imp.lhs == null && imp.rhs.subsumers.contains(bot))
						return true;
					imps.add(imp.rhs);
				}
			for(Basic bsc1:imps)
				for(Basic bsc2:imps)
					if(bsc1.complement != null && (bsc2.subsumers.contains(bsc1.complement) || bsc1.complement.subsumers.contains(bsc2)))
						return true;
					else if(bsc2.complement != null && (bsc1.subsumers.contains(bsc2.complement) || bsc2.complement.subsumers.contains(bsc1)))
						return true;

			//			for(Basic bsc:single.subsumers)
			//				if(bsc.subsumers.contains(bot))
			//					return true;
			//			for(Basic bsc1:single.subsumers)
			//				for(Basic bsc2:single.subsumers)
			//					if(bsc1.complement != null && (bsc2.subsumers.contains(bsc1.complement) || bsc1.complement.subsumers.contains(bsc2)))
			//						return true;
			//					else if(bsc2.complement != null && (bsc1.subsumers.contains(bsc2.complement) || bsc2.complement.subsumers.contains(bsc1)))
			//						return true;
		}
		return false;
	}


	public void loadOntology()
	{
		elcfactory = new OntologyFactory(ontology,bgp,MetaOn,disjointness);
		elcfactory.createbuilder();
		this.relOntology = elcfactory.createELOntology();	
		this.relOntology.profile = Profile.OWL_2_EL;
	}

	// OWL-DBC methods
	/**
	 * This method saves REL reasoning results to a output stream.
	 * @param TBox: whether to save TBox classification results
	 * @param Type: whether to save class assertion results
	 * @param Relation: whether to save role assertion results
	 * @param subType: whether to save only direct subsumptions
	 * @param clsType: whether to save only direct class assertions
	 * @param out: the output stream to save to
	 * @throws IOException
	 */
	public void save(boolean TBox, boolean Type, boolean Relation, boolean subType, boolean clsType,
			OutputStream out) throws IOException {
		// TODO Auto-generated method stub
		String rdfs="<http://www.w3.org/2000/01/rdf-schema#> .\n";
		String rdf="<http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n";
		//		String subcls = "\t<"+rdfs+"subClassOf>\t";
		//		String type = "\t<"+rdf+"type>\t";
		//		final PrintStream ps= new PrintStream(out);
		OutputStreamWriter writer = new OutputStreamWriter(out);
		writer.write("@prefix rdf: "+rdf);
		writer.write("@prefix rdfs: "+rdfs);

		if(TBox)
			for(Basic cls:relOntology.originalNamedConcepts)
			{
				if(cls instanceof Atomic && cls.id > 1)
				{
					ArrayList<Basic> sups = getsubsumers(cls,subType);
					if(sups.size()>0)
					{
						writer.write("<"+cls.uri+"> rdfs:subClassOf ");
						for(int i = 0;i<sups.size()-1;i++)
						{
							//						String subs = "<"+cls.uri+"> rdfs:subClassOf <"+sups.get(i).uri+">\n";
							//						System.out.print(subs);
							//						ps.println(subs);
							writer.write("<"+sups.get(i).uri+"> ,\n");
						}
						writer.write("<"+sups.get(sups.size()-1)+"> .\n");
						//					System.out.print("<"+cls.uri+"> rdfs:subClassOf <"+sups.get(sups.size()-1).uri+">\n");
					}
					//					System.out.println(cls.uri.getFragment()+" "+sups.size());
				}
			}

		if(Type && Relation)
			for(int id:relOntology.individualIDs.values())
			{
				Singleton indi = (Singleton)relOntology.descriptions.get(id);
				if(indi.original)
				{
					ArrayList<Basic> clss = getcls(indi,clsType);
					if(clss.size()>0)
					{
						writer.write("<"+indi.uri+"> a ");
						for(int i = 0;i<clss.size()-1;i++)
							//						ps.println(indi.uri+type+cls.uri);
							writer.write("<"+clss.get(i).uri+"> ,\n");
						writer.write("<"+clss.get(clss.size()-1)+"> .\n");
					}
					//					System.out.println(indi.uri.getFragment()+" "+clss.size());

					for(Role role:relOntology.roles.values())
					{
						if(role.original && role.Relations.get(indi)!=null)
						{
							ArrayList<Singleton> objs = new ArrayList<Singleton>();
							for(Basic obj:role.Relations.get(indi))
								if(obj instanceof Singleton && obj.original)
									objs.add(obj.asSingleton());
							if(objs.size()>0)
							{
								writer.write("<"+indi.uri+"> <"+role.uri+"> ");
								for(int i = 0;i<objs.size()-1;i++)
									writer.write("<"+objs.get(i).uri+"> ,\n");
								//							for(Individual indi2:indi.relations.get(role))
								//								ps.println(indi.uri+"\t"+role.uri+"\t"+indi2.uri);
								writer.write("<"+objs.get(objs.size() -1)+"> .\n");
							}
						}
					}
				}
			}
		else if(Type)
			for(int id:relOntology.individualIDs.values())
			{
				Singleton indi = (Singleton)relOntology.descriptions.get(id);
				if(indi.original)
				{
					ArrayList<Basic> clss = getcls(indi,clsType);
					if(clss.size()>0)
					{
						writer.write("<"+indi.uri+"> a ");
						for(int i = 0;i<clss.size()-1;i++)
							//						ps.println(indi.uri+type+cls.uri);
							writer.write("<"+clss.get(i).uri+"> ,");
						writer.write("<"+clss.get(clss.size()-1)+"> .");
					}
				}
			}
		else if(Relation)
			for(int id:relOntology.individualIDs.values())
			{
				Singleton indi = (Singleton)relOntology.descriptions.get(id);
				if(indi.original)
				{
					for(Role role:relOntology.roles.values())
					{
						if(role.original && role.Relations.get(indi)!=null)
						{
							writer.write("<"+indi.uri+"> <"+role.uri+"> ");
							ArrayList<Singleton> objs = new ArrayList<Singleton>();
							for(Basic obj:role.Relations.get(indi))
								if(obj instanceof Singleton && obj.original)
									objs.add(obj.asSingleton());
							for(int i = 0;i<objs.size()-1;i++)
								writer.write("<"+objs.get(i).uri+"> ,");
							//							for(Individual indi2:indi.relations.get(role))
							//								ps.println(indi.uri+"\t"+role.uri+"\t"+indi2.uri);
							writer.write("<"+objs.get(objs.size() -1)+"> .");
						}
					}
				}
			}

		writer.close();
	}

	protected void initialiseClassifier()
	{
		classifier = new CombinedClassifier();
	}

	/**
	 * This method calls the classifer to perform reasoning.
	 * Note that ABox realisation must be performed together with or after TBox classification.
	 * @param classifyTBox: whether TBox classification needs to be performed
	 * @param classifyABox: whether ABox realisation needs to be performed
	 */
	public void classify(boolean classifyTBox, boolean classifyABox){
		// TODO Auto-generated method stub
		classifier.ontology = relOntology;
		if(!classifyTBox && !classifyABox)
			return;
		relOntology.consistency = true;
		classifier.completion(classifyTBox, classifyABox);
		if(Thread.currentThread().isInterrupted())
			return;
		if(!relOntology.consistency)
		{
			relOntology.tBox_Classified = true;
			relOntology.aBox_Classified = true;
			return;
		}

		// only perform the below if classified TBox the first time
		// TBox classification post-processing for OWLAPI methods
		if(!relOntology.tBox_Classified)
		{
			satisfiableBasics = new HashSet<Basic>(relOntology.originalNamedConcepts);
			Atomic bot = (Atomic) relOntology.descriptions.get(0);
			satisfiableBasics.removeAll(bot.equivalence);

			leafClasses = new OWLClassNodeSet();
			satisfiableClasses = new OWLClassNodeSet();
			leafBasics = new HashSet<Basic>(satisfiableBasics);

			// remove non-leaf concepts from leafBasics
			for(Basic basic:satisfiableBasics)
			{
				if(!leafBasics.contains(basic))
					continue;
				Atomic atom = (Atomic) basic;
				for(Basic sub:atom.subsumers)
				{
					if(!atom.equivalence.contains(sub) && leafBasics.contains(sub))
						leafBasics.removeAll(sub.equivalence);
				}
			}

			// obtain unsatisfiable classes
			unsatisfiableClasses = new OWLClassNode();
			for(Basic bsc:bot.equivalence)
			{
				if(bsc instanceof Atomic && bsc.original)
					unsatisfiableClasses.add(factory.getOWLClass(bsc.uri));
			}

			// obtain satisfialbe classes
			while(satisfiableBasics.size()>0)
			{
				Basic sub = satisfiableBasics.iterator().next();
				satisfiableBasics.removeAll(sub.equivalence);
				OWLClassNode ancestor = new OWLClassNode();
				for(Basic eq:sub.equivalence)
					if(eq instanceof Atomic && ((Atomic)eq).original)
						ancestor.add(factory.getOWLClass(((Atomic)eq).uri));							
				if(ancestor.getSize() > 0)
					satisfiableClasses.addNode(ancestor);
			}

			// obtain leaf classes
			while(leafBasics.size()>0)
			{
				Basic sub = leafBasics.iterator().next();
				leafBasics.removeAll(sub.equivalence);
				OWLClassNode ancestor = new OWLClassNode();
				for(Basic eq:sub.equivalence)
					if(eq instanceof Atomic && ((Atomic)eq).original)
						ancestor.add(factory.getOWLClass(((Atomic)eq).uri));							
				if(ancestor.getSize() > 0)
					leafClasses.addNode(ancestor);
			}

			relOntology.tBox_Classified = true;
		}
		if(classifyABox)
			relOntology.aBox_Classified = true;
	}

	protected boolean entail(OWLClassAssertionAxiom axiom){
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.aBox_Classified)
			precomputeInferences(InferenceType.CLASS_ASSERTIONS);
		Singleton indi = getSingleton(axiom.getIndividual());
		Description sup = getDescription(axiom.getClassExpression());
		Atomic bot = (Atomic) relOntology.descriptions.get(0);

		boolean answer = false;
		boolean duo = false;
		if(sup == null || !(sup instanceof Basic))
		{
			// apply duo-ontology classification approach
			duo = true;
			// add an additional axiom sup \sub tempD
			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempD"));
			OWLSubClassOfAxiom tempaxiom = factory.getOWLSubClassOfAxiom(axiom.getClassExpression(),tempclass);
			Entry<Basic, Basic> entry = elcfactory.loadAxiom(tempaxiom);

			// incrementally classify the new ontology
			CombinedClassifier classifier = new CombinedClassifier();
			classifier.ontology = relOntology;
			classifier.completion_duo(relOntology.aBox_Classified);

			sup = (Atomic) entry.getValue();
		}

		Basic bsup = (Basic) sup;
		answer = (indi.subsumers.contains(bsup) || indi.subsumers.contains(bot) || indi.tempSubsumers.contains(bsup) || indi.tempSubsumers.contains(bot));

		// clean the classifier, factory, ontology, etc for duo-ontology classification.
		if(duo)
			elcfactory.clean();

		return answer;
	}

	protected boolean entail(OWLDisjointClassesAxiom axiom)
	{
		List<OWLClassExpression> list = axiom.getClassExpressionsAsList();
		for(int i = 0;i<list.size()-1;i++)
			for(int j = i+1;j<list.size();j++)
			{
				if(!entail(factory.getOWLSubClassOfAxiom(list.get(i), factory.getOWLObjectComplementOf(list.get(j)))))
					return false;
			}
		return true;
	}

	protected boolean entail(OWLFunctionalDataPropertyAxiom axiom)
	{
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.DATA_PROPERTY_HIERARCHY);
		Role role = getRole(axiom.getProperty());
		// might be incomplete
		for(Role sup:role.subsumers)
			if(sup.functional)
				return true;
		return false;
	}

	protected boolean entail(OWLFunctionalObjectPropertyAxiom axiom)
	{
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.OBJECT_PROPERTY_HIERARCHY);
		Role role = getRole(axiom.getProperty());
		// might be incomplete
		for(Role sup:role.subsumers)
			if(sup.functional)
				return true;
		return false;
	}

	protected boolean entail(OWLSubClassOfAxiom axiom){
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.CLASS_HIERARCHY);
		Description sub = getDescription(axiom.getSubClass());
		Description sup = getDescription(axiom.getSuperClass());
		Atomic bot = (Atomic) relOntology.descriptions.get(0);

		boolean answer = false;
		boolean duo = false;
		if(sub == null || !(sub instanceof Basic))
		{
			// apply duo-ontology classification approach
			duo = true;
			// add an additional axiom tempC \sub sub
			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempC"));
			OWLSubClassOfAxiom tempaxiom = factory.getOWLSubClassOfAxiom(tempclass, axiom.getSubClass());
			Entry<Basic, Basic> entry = elcfactory.loadAxiom(tempaxiom);

			// incrementally classify the new ontology
			CombinedClassifier classifier = new CombinedClassifier();
			classifier.ontology = relOntology;
			classifier.completion_duo(relOntology.aBox_Classified);

			sub = (Atomic) entry.getKey();
		}

		if(sup == null || !(sup instanceof Basic))
		{
			// apply duo-ontology classification approach
			duo = true;
			// add an additional axiom sup \sub tempD
			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempD"));
			OWLSubClassOfAxiom tempaxiom = factory.getOWLSubClassOfAxiom(axiom.getSuperClass(),tempclass);
			Entry<Basic, Basic> entry = elcfactory.loadAxiom(tempaxiom);

			// incrementally classify the new ontology
			CombinedClassifier classifier = new CombinedClassifier();
			classifier.ontology = relOntology;
			classifier.completion_duo(relOntology.aBox_Classified);

			sup = (Atomic) entry.getValue();
		}

		Basic bsub = (Basic) sub;
		Basic bsup = (Basic) sup;
		answer = (bsub.subsumers.contains(bsup) || bsub.subsumers.contains(bot) || bsub.tempSubsumers.contains(bsup) || bsub.tempSubsumers.contains(bot));

		// clean the classifier, factory, ontology, etc for duo-ontology classification.
		if(duo)
			elcfactory.clean();

		return answer;
	}

	protected Description getDescription(OWLClassExpression desc){
		if(relOntology.classIDs.get(desc)!=null)
			return relOntology.descriptions.get(relOntology.classIDs.get(desc));
		return null;
	}

	protected Singleton getSingleton(OWLIndividual indi){
		if(relOntology.individualIDs.get(indi)!=null)
			return (Singleton) relOntology.descriptions.get(relOntology.individualIDs.get(indi));
		return null;
	}

	protected NodeSet<OWLNamedIndividual> getIndividuals(OWLClassExpression concept){
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.aBox_Classified)
			precomputeInferences(InferenceType.CLASS_ASSERTIONS);
		OWLNamedIndividualNodeSet individuals = new OWLNamedIndividualNodeSet();
		HashSet<Singleton> indis = new HashSet<Singleton>();
		boolean duo = false;
		Atomic elpconcept = null;
		Atomic bot = (Atomic) relOntology.descriptions.get(0);
		// check if the concept does not already exist
		if(relOntology.classIDs.get(concept) == null || !(relOntology.descriptions.get(relOntology.classIDs.get(concept)) instanceof Atomic))
		{
			// apply duo-ontology classification approach
			duo = true;
			// add an additional axiom X \sub tempC
			OWLClass tempclass = factory.getOWLClass(IRI.create("http://trowl.eu/REL#tempC"));
			OWLSubClassOfAxiom axiom = factory.getOWLSubClassOfAxiom(concept, tempclass);
			Entry<Basic, Basic> entry = elcfactory.loadAxiom(axiom);

			// incrementally classify the new ontology
			CombinedClassifier classifier = new CombinedClassifier();
			classifier.ontology = relOntology;
			classifier.completion_duo(relOntology.aBox_Classified);

			elpconcept = (Atomic) entry.getValue();
		}
		else
			elpconcept = (Atomic) relOntology.descriptions.get(relOntology.classIDs.get(concept));
		for(Description bsc:relOntology.descriptions.values())
		{
			if(bsc instanceof Singleton)
			{
				Singleton indi = (Singleton) bsc;
				if(indi.subsumers.contains(bot) || indi.subsumers.contains(elpconcept)||indi.tempSubsumers.contains(elpconcept))
					indis.add(indi);
			}
		}
		while(indis.size()>0)
		{
			Singleton head = indis.iterator().next();
			indis.removeAll(head.equivalence);
			OWLNamedIndividualNode	node = new OWLNamedIndividualNode();
			for(Basic same:head.equivalence)
				if(same instanceof Singleton && ((Singleton)same).original)
					node.add(factory.getOWLNamedIndividual(same.asSingleton().uri));
			individuals.addNode(node);
		}
		// clean the classifier, factory, ontology, etc for duo-ontology classification.
		if(duo)
			elcfactory.clean();
		return individuals;
	}

	// TrOWL-BGP methods
	protected Role getRole(OWLDataPropertyExpression role){
		OWLObjectPropertyExpression objrole = factory.getOWLObjectProperty(role.asOWLDataProperty().getIRI());
		if(relOntology.roleIDs.get(objrole)!=null)
			return relOntology.roles.get(relOntology.roleIDs.get(objrole));
		return null;
	}

	protected Role getRole(OWLObjectPropertyExpression role){
		if(relOntology.roleIDs.get(role)!=null)
			return relOntology.roles.get(relOntology.roleIDs.get(role));
		return null;
	}

	ArrayList<Basic> getcls(Singleton indi, boolean arg1){
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.DATA_PROPERTY_HIERARCHY);
		Atomic bot = (Atomic) relOntology.descriptions.get(0);
		ArrayList<Basic> classes = new ArrayList<Basic>();
		if(indi.subsumers.contains(bot)){
			classes = new ArrayList<Basic>(relOntology.originalNamedConcepts);
		}
		else
			for(Basic cls:indi.subsumers)
				if(cls instanceof Atomic && cls.original)
					classes.add(cls);
		if(arg1 == true)
		{
			ArrayList<Basic> toremove = new ArrayList<Basic>(classes);
			for(Basic basic:toremove)
			{
				for(Basic basic2:toremove)
				{
					if(basic.subsumers.contains(basic2) && !basic.equivalence.contains(basic2))
						classes.removeAll(basic2.equivalence);
				}
			}
		}
		return classes;
	}

	ArrayList<Basic> getsubsumers(Basic desc, boolean direct){
		if(!isConsistent())
		{
			throw(new InconsistentOntologyException());
		}
		if(!relOntology.tBox_Classified)
			precomputeInferences(InferenceType.CLASS_HIERARCHY);
		Atomic bot = (Atomic) relOntology.descriptions.get(0);
		ArrayList<Basic> subsumers = new ArrayList<Basic>();
		Atomic atom = (Atomic)desc;
		if(direct)
		{
			if(atom.equivalence.contains(bot))
				return new ArrayList<Basic>(leafBasics);
			for(Basic sub:atom.subsumers)
			{
				if(sub.original && sub instanceof Atomic && !subsumers.contains(sub))
				{
					boolean toadd = true;
					for(Basic sub2:atom.subsumers)
						if(sub2.original && !atom.equivalence.contains(sub2) && !sub.equivalence.contains(sub2) && sub2.subsumers.contains(sub))
						{
							toadd =false;
							break;
						}
					for(Basic sub2:atom.tempSubsumers)
						if(sub2.original && !atom.equivalence.contains(sub2) && !sub.equivalence.contains(sub2) && sub2.subsumers.contains(sub))
						{
							toadd =false;
							break;
						}
					if(toadd)
						subsumers.add(sub);
				}
			}
		}
		else
		{
			if(atom.equivalence.contains(bot))
				return new ArrayList<Basic>(satisfiableBasics);
			for(Basic sub:atom.subsumers)
				if(sub.original)
					subsumers.add(sub);
		}
		return subsumers;
	}


}
