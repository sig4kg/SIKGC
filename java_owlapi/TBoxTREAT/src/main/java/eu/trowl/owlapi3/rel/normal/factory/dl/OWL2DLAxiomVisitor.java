/**
 * 
 */
package eu.trowl.owlapi3.rel.normal.factory.dl;

import java.util.HashSet;
import java.util.Set;

import org.semanticweb.owlapi.model.OWLAnnotationAssertionAxiom;
import org.semanticweb.owlapi.model.OWLAnnotationPropertyDomainAxiom;
import org.semanticweb.owlapi.model.OWLAnnotationPropertyRangeAxiom;
import org.semanticweb.owlapi.model.OWLAsymmetricObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLAxiom;
import org.semanticweb.owlapi.model.OWLAxiomVisitor;
import org.semanticweb.owlapi.model.OWLClassAssertionAxiom;
import org.semanticweb.owlapi.model.OWLDataPropertyAssertionAxiom;
import org.semanticweb.owlapi.model.OWLDataPropertyDomainAxiom;
import org.semanticweb.owlapi.model.OWLDataPropertyRangeAxiom;
import org.semanticweb.owlapi.model.OWLDatatypeDefinitionAxiom;
import org.semanticweb.owlapi.model.OWLDeclarationAxiom;
import org.semanticweb.owlapi.model.OWLDisjointClassesAxiom;
import org.semanticweb.owlapi.model.OWLDisjointDataPropertiesAxiom;
import org.semanticweb.owlapi.model.OWLDisjointObjectPropertiesAxiom;
import org.semanticweb.owlapi.model.OWLDisjointUnionAxiom;
import org.semanticweb.owlapi.model.OWLEquivalentClassesAxiom;
import org.semanticweb.owlapi.model.OWLEquivalentDataPropertiesAxiom;
import org.semanticweb.owlapi.model.OWLEquivalentObjectPropertiesAxiom;
import org.semanticweb.owlapi.model.OWLFunctionalDataPropertyAxiom;
import org.semanticweb.owlapi.model.OWLHasKeyAxiom;
import org.semanticweb.owlapi.model.OWLInverseFunctionalObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLIrreflexiveObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLNegativeDataPropertyAssertionAxiom;
import org.semanticweb.owlapi.model.OWLNegativeObjectPropertyAssertionAxiom;
import org.semanticweb.owlapi.model.OWLObjectPropertyAssertionAxiom;
import org.semanticweb.owlapi.model.OWLObjectPropertyRangeAxiom;
import org.semanticweb.owlapi.model.OWLReflexiveObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLSubAnnotationPropertyOfAxiom;
import org.semanticweb.owlapi.model.OWLSubObjectPropertyOfAxiom;
import org.semanticweb.owlapi.model.OWLSubPropertyChainOfAxiom;
import org.semanticweb.owlapi.model.OWLSymmetricObjectPropertyAxiom;
import org.semanticweb.owlapi.model.OWLTransitiveObjectPropertyAxiom;
import org.semanticweb.owlapi.model.SWRLRule;

import eu.trowl.owlapi3.rel.util.UnsupportedFeatureException;


/*** 
 * @author Yuan Ren
 * @version 2012-05-18
 */
public abstract class OWL2DLAxiomVisitor implements OWLAxiomVisitor {
	
	// some legacy code
	// This class is not necessarily needed in REL any more.

	public final Set<OWLAxiom> unsupportedAxioms = new HashSet<OWLAxiom>();

	protected boolean ignoreUnsupportedAxioms;

	protected OWL2DLAxiomVisitor(boolean ignoreUnsupportedAxioms) {
		this.ignoreUnsupportedAxioms = ignoreUnsupportedAxioms;
	}

	/**
	 * @return all unsupported axioms in the ontology
	 */
	public Set<OWLAxiom> getUnsupportedAxioms() {
		return unsupportedAxioms;
	}

	protected void unsupportedAxiom(OWLAxiom axiom) {
		if (ignoreUnsupportedAxioms)
			unsupportedAxioms.add(axiom);
		else
			throw new UnsupportedFeatureException("Unsupported axiom: " + axiom);
	}


	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLNegativeObjectPropertyAssertionAxiom)
	 */
	@Override
	public void visit(OWLNegativeObjectPropertyAssertionAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLAntiSymmetricObjectPropertyAxiom)
	 */
	@Override
	public void visit(OWLAsymmetricObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLReflexiveObjectPropertyAxiom)
	 */
	@Override
	public void visit(OWLReflexiveObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}



//	/* (non-Javadoc)
//	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLImportsDeclaration)
//	 */
//	@Override
//	public void visit(OWLImportsDeclaration axiom) {
//		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);
//
//	}

//	/* (non-Javadoc)
//	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLAxiomAnnotationAxiom)
//	 */
//	@Override
//	public void visit(OWLAxiomAnnotationAxiom axiom) {
//		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);
//	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLDataPropertyDomainAxiom)
	 */
	@Override
	public void visit(OWLDataPropertyDomainAxiom axiom) {
		// TODO Auto-generated method stub
	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLEquivalentObjectPropertiesAxiom)
	 */
	@Override
	public void visit(OWLEquivalentObjectPropertiesAxiom axiom) {
		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLNegativeDataPropertyAssertionAxiom)
	 */
	@Override
	public void visit(OWLNegativeDataPropertyAssertionAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}


	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLDisjointDataPropertiesAxiom)
	 */
	@Override
	public void visit(OWLDisjointDataPropertiesAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLDisjointObjectPropertiesAxiom)
	 */
	@Override
	public void visit(OWLDisjointObjectPropertiesAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLObjectPropertyRangeAxiom)
	 */
	@Override
	public void visit(OWLObjectPropertyRangeAxiom axiom) {
		// TODO Auto-generated method stub

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLObjectPropertyAssertionAxiom)
	 */
	@Override
	public void visit(OWLObjectPropertyAssertionAxiom axiom) {
		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLObjectSubPropertyAxiom)
	 */
	@Override
	public void visit(OWLSubObjectPropertyOfAxiom axiom) {
		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLDisjointUnionAxiom)
	 */
	@Override
	public void visit(OWLDisjointUnionAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLDeclarationAxiom)
	 */
	@Override
	public void visit(OWLDeclarationAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLEntityAnnotationAxiom)
	 */
	@Override
	public void visit(OWLAnnotationAssertionAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);
	}

//	/* (non-Javadoc)
//	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLOntologyAnnotationAxiom)
//	 */
//	@Override
//	public void visit(OWLOntologyAnnotationAxiom axiom) {
//		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);
//
//	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLSymmetricObjectPropertyAxiom)
	 */
	@Override
	public void visit(OWLSymmetricObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLDataPropertyRangeAxiom)
	 */
	@Override
	public void visit(OWLDataPropertyRangeAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLFunctionalDataPropertyAxiom)
	 */
	@Override
	public void visit(OWLFunctionalDataPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLEquivalentDataPropertiesAxiom)
	 */
	@Override
	public void visit(OWLEquivalentDataPropertiesAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLClassAssertionAxiom)
	 */
	@Override
	public void visit(OWLClassAssertionAxiom axiom) {
		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);
	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLDataPropertyAssertionAxiom)
	 */
	@Override
	public void visit(OWLDataPropertyAssertionAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLTransitiveObjectPropertyAxiom)
	 */
	@Override
	public void visit(OWLTransitiveObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLIrreflexiveObjectPropertyAxiom)
	 */
	@Override
	public void visit(OWLIrreflexiveObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLInverseFunctionalObjectPropertyAxiom)
	 */
	@Override
	public void visit(OWLInverseFunctionalObjectPropertyAxiom axiom) {
		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);

	}


	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.OWLObjectPropertyChainSubPropertyAxiom)
	 */
	@Override
	public void visit(OWLSubPropertyChainOfAxiom axiom) {
		// TODO Auto-generated method stub
//		unsupportedAxiom(axiom);

	}


	/* (non-Javadoc)
	 * @see org.semanticweb.owl.model.OWLAxiomVisitor#visit(org.semanticweb.owl.model.SWRLRule)
	 */
	@Override
	public void visit(SWRLRule axiom) {
		// TODO Auto-generated method stub
		unsupportedAxiom(axiom);

	}

	@Override
	public void visit(OWLEquivalentClassesAxiom axiom) {
		// TODO Auto-generated method stub

	}

	@Override
	public void visit(OWLDisjointClassesAxiom axiom) {
		// TODO Auto-generated method stub

	}
	
	@Override
	public void visit(OWLHasKeyAxiom arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void visit(OWLDatatypeDefinitionAxiom arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void visit(OWLSubAnnotationPropertyOfAxiom arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void visit(OWLAnnotationPropertyDomainAxiom arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void visit(OWLAnnotationPropertyRangeAxiom arg0) {
		// TODO Auto-generated method stub
		
	}
	

}
