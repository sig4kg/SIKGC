import ReasonerUtils.HermitUtil;
import ReasonerUtils.TrOWLUtil;
import TBoxScanner.PatternDLLite;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.assertEquals;

import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.util.*;

import java.util.*;

public class TestDLLite {
    DLLite dlliteCvt= new DLLite("output/");
    private static final String TEST_IRI = "http://test/dllite/";
    OWLOntology ontology = null;
    OWLOntologyManager manager = dlliteCvt.man;
    TrOWLUtil trOWLUtil2 = new TrOWLUtil("./");
    HermitUtil hermitUtil = new HermitUtil("./");
    OWLDataFactory factory = dlliteCvt.dataFactory;
    IRI ontologyIRI = IRI.create(TEST_IRI);
    PrefixManager pm = new DefaultPrefixManager(ontologyIRI.toString());

    @Test
    public void testDisjointness() throws OWLOntologyCreationException {
        ontology = manager.createOntology(ontologyIRI);
        OWLClass clsA = factory.getOWLClass(IRI.create(ontologyIRI + "Woman"));
        OWLClass clsB = factory.getOWLClass(IRI.create(ontologyIRI + "Person"));
        OWLClass clsC = factory.getOWLClass(IRI.create(ontologyIRI + "Work"));
        // A subclassof B
        OWLAxiom axiom1 = factory.getOWLSubClassOfAxiom(clsA, clsB);
        AddAxiom addAxiom1 = new AddAxiom(ontology, axiom1);
        manager.applyChange(addAxiom1);
        // B disjointwith C
        OWLAxiom axiom2 = factory.getOWLDisjointClassesAxiom(clsB, clsC);
        AddAxiom addAxiom2 = new AddAxiom(ontology, axiom2);
        manager.applyChange(addAxiom2);
        Map<String, OWLObject> map = new HashMap<>();
        OWLOntology infOnt1 = dlliteCvt.inferAdditionalClass(trOWLUtil2, ontology, map);
        List<String> expect1 = Arrays.asList("<http://test/dllite/Person>", "<http://test/dllite#neg_Work>");
        List<String> expect2 = Arrays.asList("<http://test/dllite#neg_Person>", "<http://test/dllite#neg_Woman>");
        List<String> expect3 = Arrays.asList("<http://test/dllite/Work>", "<http://test/dllite#neg_Person>");
        List<String> expect4 = Arrays.asList("<http://test/dllite/Woman>", "<http://test/dllite#neg_Work>");
        List<String> expect5 = Arrays.asList("<http://test/dllite/Work>", "<http://test/dllite#neg_Woman>");
        List<List<String>> expects = Arrays.asList(expect1, expect2, expect3, expect4, expect5);
        Set<OWLSubClassOfAxiom> subclassof = infOnt1.getAxioms(AxiomType.SUBCLASS_OF);
        List<List<String>> actual = new ArrayList<>();
        for(OWLSubClassOfAxiom ax : subclassof) {
            List<String> ss = Arrays.asList(ax.getSubClass().toString(), ax.getSuperClass().toString());
            actual.add(ss);
        }
        for (List<String> ss : expects) {
            Assert.assertTrue(actual.stream().anyMatch(l -> l.get(0).equals(ss.get(0)) && l.get(1).equals(ss.get(1))));
        }
    }

    @Test
    public void testInverseOf() throws OWLOntologyCreationException {
        ontology = manager.createOntology(ontologyIRI);
        OWLClass clsB = factory.getOWLClass(IRI.create(ontologyIRI + "#Person"));
        OWLClass clsC = factory.getOWLClass(IRI.create(ontologyIRI + "#Work"));
        OWLClass clsA = factory.getOWLClass(IRI.create(ontologyIRI + "#Woman"));
        // A subclassof B
        OWLAxiom axiom1 = factory.getOWLSubClassOfAxiom(clsA, clsB);
        AddAxiom addAxiom1 = new AddAxiom(ontology, axiom1);
        manager.applyChange(addAxiom1);
        // B disjointwith C
        OWLAxiom axiom2 = factory.getOWLDisjointClassesAxiom(clsB, clsC);
        AddAxiom addAxiom2 = new AddAxiom(ontology, axiom2);
        manager.applyChange(addAxiom2);
        // inverseof
        OWLObjectProperty hasMother = factory.getOWLObjectProperty(":hasMother", pm);
        OWLObjectProperty hasChild = factory.getOWLObjectProperty(":hasChild", pm);
        OWLAxiom axiom3 = factory.getOWLInverseObjectPropertiesAxiom(hasChild, hasMother);
        AddAxiom addAxiom3 = new AddAxiom(ontology, axiom3);
        manager.applyChange(addAxiom3);
        // domain and range
        OWLObjectProperty work_for = factory.getOWLObjectProperty(":work_for", pm);
        OWLAxiom axiom5 = factory.getOWLObjectPropertyDomainAxiom(work_for, clsB);
        OWLAxiom axiom6 = factory.getOWLObjectPropertyRangeAxiom(work_for, clsC);
        AddAxiom addAxiom5 = new AddAxiom(ontology, axiom5);
        AddAxiom addAxiom6 = new AddAxiom(ontology, axiom6);
        manager.applyChange(addAxiom5);
        manager.applyChange(addAxiom6);
        OWLAxiom axiom7 = factory.getOWLObjectPropertyRangeAxiom(hasMother, clsB);
        OWLAxiom axiom8 = factory.getOWLObjectPropertyDomainAxiom(hasMother, clsA);
        AddAxiom addAxiom7 = new AddAxiom(ontology, axiom7);
        AddAxiom addAxiom8 = new AddAxiom(ontology, axiom8);
        manager.applyChange(addAxiom7);
        manager.applyChange(addAxiom8);

        Map<String, OWLObject> map = new HashMap<>();
//        OWLOntology infOnt1 = dlliteCvt.inferAdditionalClass(trOWLUtil2, ontology, map);
        OWLOntology infOnt2 = dlliteCvt.ont2dllite(trOWLUtil2, ontology);
        PatternDLLite pattern = new PatternDLLite();
        pattern.SetOWLAPIContext(infOnt2, trOWLUtil2.reasoner, factory, "./");
        pattern.generateOPPattern();
    }

    @Test
    public void testSymetric() throws OWLOntologyCreationException {
        ontology = manager.createOntology(ontologyIRI);
        // symetric
        OWLObjectProperty hasFriend = factory.getOWLObjectProperty(":hasFriend", pm);
        OWLAxiom axiom3 = factory.getOWLSymmetricObjectPropertyAxiom(hasFriend);
        AddAxiom addAxiom3 = new AddAxiom(ontology, axiom3);
        manager.applyChange(addAxiom3);
        Map<String, OWLObject> map = new HashMap<>();
        OWLOntology infOnt1 = dlliteCvt.inferAdditionalClass(trOWLUtil2, ontology, map);

    }

    @Test
    public void testSubPropertyOf() throws OWLOntologyCreationException {
        ontology = manager.createOntology(ontologyIRI);
        OWLObjectProperty hasMother = factory.getOWLObjectProperty(":hasMother", pm);
        // subpropertyof
        OWLObjectProperty hasParent = factory.getOWLObjectProperty(":hasParent", pm);
        OWLAxiom axiom4 = factory.getOWLSubObjectPropertyOfAxiom(hasMother, hasParent);
        AddAxiom addAxiom4 = new AddAxiom(ontology, axiom4);
        manager.applyChange(addAxiom4);
        Map<String, OWLObject> map = new HashMap<>();
        OWLOntology infOnt1 = dlliteCvt.inferAdditionalClass(trOWLUtil2, ontology, map);
        List<String> expect1 = Arrays.asList("<http://test/dllite#some_hasMother>", "<http://test/dllite#some_hasParent>");
        List<String> expect2 = Arrays.asList("<http://test/dllite#some_ivs_hasMother>", "<http://test/dllite#some_ivs_hasParent>");
        List<String> expect3 = Arrays.asList("<http://test/dllite#neg_some_hasParent>", "<http://test/dllite#neg_some_hasMother>");
        List<String> expect4 = Arrays.asList("<http://test/dllite#neg_some_ivs_hasParent>", "<http://test/dllite#neg_some_ivs_hasMother>");
        List<List<String>> expects = Arrays.asList(expect1, expect2, expect3, expect4);
        Set<OWLSubClassOfAxiom> subclassof = infOnt1.getAxioms(AxiomType.SUBCLASS_OF);
        List<List<String>> actual = new ArrayList<>();
        for(OWLSubClassOfAxiom ax : subclassof) {
            List<String> ss = Arrays.asList(ax.getSubClass().toString(), ax.getSuperClass().toString());
            actual.add(ss);
        }
        for (List<String> ss : expects) {
            Assert.assertTrue(actual.stream().anyMatch(l -> l.get(0).equals(ss.get(0)) && l.get(1).equals(ss.get(1))));
        }
    }

    @Test
    public void testNELL() throws Exception {
        ontology = dlliteCvt.loadOnto("../../resources/NELL.ontology.ttl");
        OWLOntology infOnt = dlliteCvt.ont2dllite(trOWLUtil2, ontology);
        PatternDLLite pattern = new PatternDLLite();
        pattern.SetOWLAPIContext(infOnt, trOWLUtil2.reasoner, factory, "output/");
        pattern.generateOPPattern();
    }
}
