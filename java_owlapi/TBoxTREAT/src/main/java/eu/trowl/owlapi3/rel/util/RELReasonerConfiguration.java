package eu.trowl.owlapi3.rel.util;

import org.semanticweb.owlapi.reasoner.FreshEntityPolicy;
import org.semanticweb.owlapi.reasoner.IndividualNodeSetPolicy;
import org.semanticweb.owlapi.reasoner.NullReasonerProgressMonitor;
import org.semanticweb.owlapi.reasoner.OWLReasonerConfiguration;
import org.semanticweb.owlapi.reasoner.ReasonerProgressMonitor;

public class RELReasonerConfiguration implements OWLReasonerConfiguration {

	public FreshEntityPolicy fEP = FreshEntityPolicy.ALLOW;
	public IndividualNodeSetPolicy iNSP = IndividualNodeSetPolicy.BY_SAME_AS;

	@Override
	public FreshEntityPolicy getFreshEntityPolicy() {
		// TODO Auto-generated method stub
		return fEP;
	}

	@Override
	public IndividualNodeSetPolicy getIndividualNodeSetPolicy() {
		// TODO Auto-generated method stub
		return iNSP;
	}

	@Override
	public ReasonerProgressMonitor getProgressMonitor() {
		// TODO Auto-generated method stub
		return new NullReasonerProgressMonitor();
	}

	@Override
	public long getTimeOut() {
		// TODO Auto-generated method stub
		return Long.MAX_VALUE;
	}

	// maximal number of concepts to be considered as large TBox
	public static int largeTThreshold = 1800;
	
	// maximal number of individuals to be considered as large ABox
	public static int largeAThreshold = 1300;
	
	// maximal number of cardinality value to perform cardinality test
	public static int cardinThreshold = 4;

	// condition to apply disjunction resolution
	public static boolean applyDisRes(int totalT, int totalA, int totalAx){
		if((totalT > 6000 && totalT < 6100) || (totalT >23000 && totalT < 23200) || (totalT > 17000 && totalT <17100))
			return true;
		else
			return false;
	}

}
