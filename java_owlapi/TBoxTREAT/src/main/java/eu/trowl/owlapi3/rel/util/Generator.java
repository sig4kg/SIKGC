package eu.trowl.owlapi3.rel.util;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.AddAxiom;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLAxiom;
import org.semanticweb.owlapi.model.OWLLogicalAxiom;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyChangeException;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLOntologyStorageException;
import org.semanticweb.owlapi.model.UnknownOWLOntologyException;
import org.semanticweb.owlapi.util.SimpleIRIMapper;

/***
 * This class generates ontologies from a set or a list of axioms.
 * @author Yuan Ren
 *
 */
public class Generator {

	/**
	 * @param args
	 * @throws OWLOntologyCreationException 
	 * @throws OWLOntologyChangeException 
	 * @throws OWLOntologyStorageException 
	 * @throws UnknownOWLOntologyException 
	 */

	public static void generate(String prefix, String physical, Set<OWLAxiom> axioms) throws OWLOntologyCreationException, OWLOntologyChangeException, UnknownOWLOntologyException, OWLOntologyStorageException
	{
		
        IRI ontologyURI = IRI.create(prefix);
        
        IRI physicalURI = IRI.create(physical);
        
        SimpleIRIMapper mapper = new SimpleIRIMapper(ontologyURI, physicalURI);
        
    	OWLOntologyManager manager = OWLManager.createOWLOntologyManager();

    	manager.addIRIMapper(mapper);
        
        OWLOntology ontology = manager.createOntology(ontologyURI);
        
    	List<AddAxiom> addAxioms = new ArrayList<AddAxiom>();

    	for(OWLAxiom axiom:axioms)
    		addAxioms.add(new AddAxiom(ontology, axiom));
        
		manager.applyChanges(addAxioms);
		
		manager.saveOntology(ontology);        
		
		System.out.println("Ontology Saved to "+physical);
	}
	public static void generate(String prefix, String physical, ArrayList<OWLLogicalAxiom> axioms) throws OWLOntologyCreationException, OWLOntologyChangeException, UnknownOWLOntologyException, OWLOntologyStorageException
	{
		
		IRI ontologyURI = IRI.create(prefix);
        
		IRI physicalURI = IRI.create(physical);
        
        SimpleIRIMapper mapper = new SimpleIRIMapper(ontologyURI, physicalURI);
        
    	OWLOntologyManager manager = OWLManager.createOWLOntologyManager();

    	manager.addIRIMapper(mapper);
        
        OWLOntology ontology = manager.createOntology(ontologyURI);
        
    	List<AddAxiom> addAxioms = new ArrayList<AddAxiom>();

    	for(OWLAxiom axiom:axioms)
    		addAxioms.add(new AddAxiom(ontology, axiom));
        
		manager.applyChanges(addAxioms);
		
		manager.saveOntology(ontology);        
		System.out.println("Ontology Saved to "+physical);
	}
}
