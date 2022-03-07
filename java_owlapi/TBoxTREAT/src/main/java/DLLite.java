import java.io.*;
import java.util.*;
//import com.clarkparsia.pellet.owlapiv3.PelletReasonerFactory;
import org.semanticweb.HermiT.Configuration;
import org.semanticweb.HermiT.Reasoner.ReasonerFactory;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.NTriplesDocumentFormat;
import org.semanticweb.owlapi.formats.TurtleDocumentFormat;
import org.semanticweb.owlapi.io.StringDocumentTarget;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
//import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
//import org.semanticweb.owlapi.reasoner.structural.StructuralReasonerFactory;
import org.semanticweb.owlapi.util.*;
import uk.ac.manchester.cs.owl.owlapi.OWLSubClassOfAxiomImpl;


public class DLLite {
    public static void testOWL2DLlite(String out_file) throws Exception {
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        String base = "http://org.semanticweb.restrictionexample";
        OWLOntology ont = man.createOntology(IRI.create(base));
        OWLDataFactory factory = man.getOWLDataFactory();
        OWLObjectProperty R = factory.getOWLObjectProperty(IRI.create(base + "#hasPart"));
        OWLObjectProperty R2 = factory.getOWLObjectProperty(IRI.create(base + "#hasPart"));
        Map<String, OWLClassExpression> map = new HashMap<String, OWLClassExpression>();
        OWLClass nose = factory.getOWLClass(IRI.create(base + "#Nose"));
        OWLClass eyes = factory.getOWLClass(IRI.create(base + "#Eyes"));
        OWLClass nosered = factory.getOWLClass(IRI.create(base + "#NoseRed"));
        OWLClass head = factory.getOWLClass(IRI.create(base + "#Head"));
        OWLDeclarationAxiom noseA = factory.getOWLDeclarationAxiom(nose);
        OWLDeclarationAxiom rednoseA = factory.getOWLDeclarationAxiom(nosered);
        OWLDeclarationAxiom eyesA = factory.getOWLDeclarationAxiom(eyes);
        OWLDeclarationAxiom headA = factory.getOWLDeclarationAxiom(head);
        man.addAxiom(ont, eyesA);
        man.addAxiom(ont, noseA);
        man.addAxiom(ont, rednoseA);
        man.addAxiom(ont, headA);
        Set<OWLAxiom> hasAxioms = new HashSet<OWLAxiom>();
        hasAxioms.add(factory.getOWLInverseFunctionalObjectPropertyAxiom(R));
        hasAxioms.add(factory.getOWLIrreflexiveObjectPropertyAxiom(R));
        hasAxioms.add(factory.getOWLAsymmetricObjectPropertyAxiom(R));
        man.addAxioms(ont, hasAxioms);
        man.addAxiom(ont, factory.getOWLInverseObjectPropertiesAxiom(R, R2));

        OWLClass negNose = factory.getOWLClass(IRI.create(base + "#negNose"));
        OWLClass negNosered = factory.getOWLClass(IRI.create(base + "#negNosered"));
        OWLClass negeyes = factory.getOWLClass(IRI.create(base + "#negeyes"));
        OWLClass neghead = factory.getOWLClass(IRI.create(base + "#neghead"));
        OWLClassExpression complnose = nose.getObjectComplementOf();
        OWLClassExpression complnosered = nosered.getObjectComplementOf();
        OWLClassExpression compleyes = eyes.getObjectComplementOf();
        OWLClassExpression complhead = head.getObjectComplementOf();
        OWLAxiom negN = factory.getOWLEquivalentClassesAxiom(negNose, complnose);
        OWLAxiom negRed = factory.getOWLEquivalentClassesAxiom(negNosered, complnosered);
        OWLAxiom negE = factory.getOWLEquivalentClassesAxiom(negeyes, compleyes);
        OWLAxiom negH = factory.getOWLEquivalentClassesAxiom(neghead, complhead);
        man.addAxiom(ont, negN);
        man.addAxiom(ont, negRed);
        man.addAxiom(ont, negE);
        man.addAxiom(ont, negH);
        map.put(negNose.getIRI().toString(), complnose);
        map.put(negNosered.getIRI().toString(), complnosered);
        map.put(negeyes.getIRI().toString(), compleyes);
        map.put(neghead.getIRI().toString(), complhead);

        // Now create a restriction to describe the class of individuals that
        // have at least one part that is a kind of nose
        OWLClass D1 = factory.getOWLClass(IRI.create(base + "#D1"));
        OWLClassExpression expression1 = factory.getOWLObjectSomeValuesFrom(R, factory.getOWLThing());
        OWLAxiom definition1 = factory.getOWLEquivalentClassesAxiom(D1, expression1);
        man.addAxiom(ont, definition1);
        map.put(D1.getIRI().toString(), expression1);
        OWLClass D2 = factory.getOWLClass(IRI.create(base + "#D2"));
        OWLClassExpression expression2 = factory.getOWLObjectSomeValuesFrom(R.getInverseProperty(), factory.getOWLThing());
        OWLAxiom definition2 = factory.getOWLEquivalentClassesAxiom(D2, expression2);
        man.addAxiom(ont, definition2);
        map.put(D2.getIRI().toString(), expression2);
        // Obtain a reference to the Head class so that we can specify that
        // Heads have noses
          // We now want to state that hasPart some is subclassof , to
        // do this we create a subclass axiom (remember, restrictions are
        // also classes - they describe classes of individuals -- they are
        // anonymous classes).
        OWLSubClassOfAxiom ax = factory.getOWLSubClassOfAxiom(head, D1);
        OWLSubClassOfAxiom bx = factory.getOWLSubClassOfAxiom(nosered, nose);
        OWLSubClassOfAxiom cx = factory.getOWLSubClassOfAxiom(nosered, D2);
        OWLSubClassOfAxiom dx = factory.getOWLSubClassOfAxiom(eyes, D2);
        // Add the axiom to our ontology
        AddAxiom addAx = new AddAxiom(ont, ax);
        AddAxiom addAxb = new AddAxiom(ont, bx);
        AddAxiom addAxc = new AddAxiom(ont, cx);
        AddAxiom addAxd = new AddAxiom(ont, dx);
        man.applyChange(addAx);
        man.applyChange(addAxb);
        man.applyChange(addAxc);
        man.applyChange(addAxd);

//        OWLReasonerFactory reasonerFactory = new StructuralReasonerFactory();
        // Uncomment the line below
//        reasonerFactory = new PelletReasonerFactory();
        // Load an example ontology - for the purposes
        // of the example, we will just load the ontology.
        // Create the reasoner and classify the ontology
        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        ReasonerFactory rf = new ReasonerFactory();
        OWLReasoner reasoner = rf.createReasoner(ont, configuration);
        reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY);
        // To generate an inferred ontology we use implementations of inferred
        // axiom generators to generate the parts of the ontology we want (e.g.
        // subclass axioms, equivalent classes axioms, class assertion axiom
        // etc. - see the org.semanticweb.owlapi.util package for more
        // implementations). Set up our list of inferred axiom generators
        List<InferredAxiomGenerator<? extends OWLAxiom>> gens =
                new ArrayList<InferredAxiomGenerator<? extends OWLAxiom>>();
        gens.add(new InferredSubClassAxiomGenerator());
        // Put the inferred axioms into a fresh empty ontology - note that there
        // is nothing stopping us stuffing them back into the original asserted
        // ontology if we wanted to do this.
        OWLOntology infOnt = man.createOntology();
        // Now get the inferred ontology generator to generate some inferred
        // axioms for us (into our fresh ontology). We specify the reasoner that
        // we want to use and the inferred axiom generators that we want to use.
        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, gens);
        iog.fillOntology(man.getOWLDataFactory(), infOnt);
        // merge ont and infOnt
        OWLOntologyMerger merger = new OWLOntologyMerger(man);
        // We merge all of the loaded ontologies. Since an OWLOntologyManager is
        // an OWLOntologySetProvider we just pass this in. We also need to
        // specify the IRI of the new ontology that will be created.
        IRI mergedOntologyIRI = IRI.create("http://www.semanticweb.com/mymergedont");
        OWLOntology merged = merger.createMergedOntology(man, mergedOntologyIRI);

        // OWLAPI axiom instances are immutable, therefore to update one you have to remove it and add a
        // new axiom with altered values.
        Set<OWLSubClassOfAxiom> subclassof = merged.getAxioms(AxiomType.SUBCLASS_OF);

        // recover D and N
        for (OWLSubClassOfAxiom s : subclassof) {
            OWLClassExpression sub = s.getSubClass();
            OWLClassExpression sup = s.getSuperClass();
            String subIRI = "";
            String supIRI = "";
//            OWLClassExpression recoverSub = Null;
            if (sub.isNamed()) {
                subIRI = ((OWLClass) sub).getIRI().toString();
            }
            if (sup.isNamed()) {
                supIRI = ((OWLClass) sup).getIRI().toString();
            }
            if (map.containsKey(subIRI) || map.containsKey(supIRI)) {
                OWLClassExpression recoverSub = map.getOrDefault(subIRI, sub);
                OWLClassExpression recoverSup = map.getOrDefault(supIRI, sup);
                OWLSubClassOfAxiom recoverAX = factory.getOWLSubClassOfAxiom(recoverSub, recoverSup);
                // Add the axiom to our ontology
                AddAxiom tmpaddAx = new AddAxiom(merged, recoverAX);
                man.applyChange(tmpaddAx);
            }
        }
        // remove additional classes from merged
        OWLEntityRemover remover1 = new OWLEntityRemover(merged);
        for (OWLClass namedClass: merged.getClassesInSignature()) {
            if (map.containsKey(namedClass.getIRI().toString())) {
                namedClass.accept(remover1);
            }
        }
        // Now we get all of the changes from the entity remover, which should
        // be applied to remove all of the individuals that we have visited from
        // the ontology. Notice that "batch" deletes can essentially be
        // performed - we simply visit all of the classes, properties and
        // individuals that we want to remove and then apply ALL of the changes
        // after using the entity remover to collect them
        man.applyChanges(remover1.getChanges());

        OWLReasoner reasoner2 = rf.createReasoner(merged, configuration);
        reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY);
        List<InferredAxiomGenerator<? extends OWLAxiom>> gens2 =
                new ArrayList<InferredAxiomGenerator<? extends OWLAxiom>>();
        gens2.add(new InferredSubClassAxiomGenerator());
        OWLOntology infOnt2 = man.createOntology();
        // Now get the inferred ontology generator to generate some inferred
        // axioms for us (into our fresh ontology). We specify the reasoner that
        // we want to use and the inferred axiom generators that we want to use.
        InferredOntologyGenerator iog2 = new InferredOntologyGenerator(reasoner2, gens2);
        iog2.fillOntology(man.getOWLDataFactory(), infOnt2);
        IRI flattenOntologyIRI = IRI.create("http://www.semanticweb.com/flatten");
        // remore ont from manager
        man.removeOntology(ont);
        man.removeOntology(infOnt);
        OWLOntology flatten = merger.createMergedOntology(man, flattenOntologyIRI);
        File inferredOntologyFile = new File(out_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            // We use the nt format as for the input ontology.
            NTriplesDocumentFormat format = new NTriplesDocumentFormat();
//            TurtleDocumentFormat format = new TurtleDocumentFormat();
            man.saveOntology(flatten, format, outputStream);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    public static void removeAnnotations(String in_file, String out_file) throws Exception {
        System.out.println("To DL-lite: " + in_file);
        // load ontology from file
        File initialFile = new File(in_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(inputStream);
        String base = "http://org.semanticweb.restrictionexample";
        OWLDataFactory factory = man.getOWLDataFactory();
        // remove annotations
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ont.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax : toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            man.applyChange(removeAxiom);
        }
        System.out.println("Saving new ontology " + out_file);
        File inferredOntologyFile = new File(out_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            // We use the nt format as for the input ontology.
//             NTriplesDocumentFormat format = new NTriplesDocumentFormat();
            TurtleDocumentFormat format = new TurtleDocumentFormat();
            OWLDocumentFormat formatOri = man.getOntologyFormat(ont);
            if (formatOri.isPrefixOWLDocumentFormat()) {
                format.copyPrefixesFrom(formatOri.asPrefixOWLDocumentFormat());
            }
            man.saveOntology(ont, format, outputStream);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    public static void owl2dllite(String in_file, String out_file) throws Exception {
        System.out.println("To DL-lite: " + in_file);
        // load ontology from file
        File initialFile = new File(in_file);
        InputStream inputStream = new FileInputStream(initialFile);
        // the stream holding the file content
        if (inputStream == null) {
            throw new IllegalArgumentException("file not found! " + in_file);
        }
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(inputStream);
        String base = "http://org.semanticweb.restrictionexample";
        OWLDataFactory factory = man.getOWLDataFactory();
        // remove annotations
        List<OWLAxiom> toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(ont.getAxioms(AxiomType.ANNOTATION_ASSERTION));
        for (OWLAxiom ax: toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(ont, ax);
            man.applyChange(removeAxiom);
        }
        // a map to keep additional class IRI to class expression
        Map<String, OWLClassExpression> map = new HashMap<String, OWLClassExpression>();
        // Now create restrictions to describe the class of individual object properties
        System.out.println("Creating D...");
        for (OWLObjectProperty R : ont.getObjectPropertiesInSignature()) {
            if (!R.isNamed()) {
                continue;
            }
            // expression for R and R-
            OWLClassExpression expD1 = factory.getOWLObjectSomeValuesFrom(R, factory.getOWLThing());
            OWLClassExpression expD2 = factory.getOWLObjectSomeValuesFrom(R.getInverseProperty(), factory.getOWLThing());
            // additianal class for (\some R) and (\some R-)
            String nameR = R.getNamedProperty().toStringID();
            if (nameR.contains("#")) {
                nameR = nameR.substring(nameR.lastIndexOf('#') + 1, nameR.length());
            } else {
                nameR = nameR.substring(nameR.lastIndexOf('/') + 1, nameR.length());
            }
            String classNameD1 = base + "#some_" + nameR;
            String classNameD2 = base + "#some_ivs_" + nameR;
            OWLClass D1 = factory.getOWLClass(IRI.create(classNameD1));
            OWLClass D2 = factory.getOWLClass(IRI.create(classNameD2));
            // map D1 to (\some R) and D2 to (\some R-)
            OWLAxiom def1 = factory.getOWLEquivalentClassesAxiom(D1, expD1);
            OWLAxiom def2 = factory.getOWLEquivalentClassesAxiom(D2, expD2);
            man.addAxiom(ont, def1);
            man.addAxiom(ont, def2);
            map.put(D1.getIRI().toString(), expD1);
            map.put(D2.getIRI().toString(), expD2);
        }
        // now create restriction to describe the named classes
        System.out.println("Creating N...");
        for (OWLClass cls: ont.getClassesInSignature()) {
            if (!cls.isNamed()) {
                continue;
            }
            String clsName = cls.toStringID();
            if (clsName.contains("#")) {
                clsName = clsName.substring(clsName.lastIndexOf('#') + 1, clsName.length());
            } else {
                clsName = clsName.substring(clsName.lastIndexOf('/') + 1, clsName.length());
            }
            String negClsName = base + "#neg_" + clsName;
            OWLClass negCls = factory.getOWLClass(IRI.create(negClsName));
            OWLClassExpression expCompl = cls.getObjectComplementOf();
            OWLAxiom negDef = factory.getOWLEquivalentClassesAxiom(negCls, expCompl);
            man.addAxiom(ont, negDef);
            map.put(negCls.getIRI().toString(), expCompl);
        }
        // Schema + Delta, then inference
        Configuration configuration = new Configuration();
        configuration.ignoreUnsupportedDatatypes = true;
        ReasonerFactory rf = new ReasonerFactory();
        OWLReasoner reasoner = rf.createReasoner(ont, configuration); // It takes time to create Hermit reasoner
        System.out.println("Infer Schema + Delta...");
        reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY);
        List<InferredAxiomGenerator<? extends OWLAxiom>> gens = new ArrayList<InferredAxiomGenerator<? extends OWLAxiom>>();
        gens.add(new InferredSubClassAxiomGenerator());
        OWLOntology infOnt1 = man.createOntology();
        InferredOntologyGenerator iog = new InferredOntologyGenerator(reasoner, gens);
        iog.fillOntology(man.getOWLDataFactory(), infOnt1);
        // merge ont and infOnt1
        System.out.println("merging infOnt1 to ont...");
        OWLOntologyMerger merger = new OWLOntologyMerger(man);
        IRI mergedOntologyIRI1 = IRI.create("http://www.semanticweb.com/merged1");
        OWLOntology merged = merger.createMergedOntology(man, mergedOntologyIRI1);

//        // remove redundants: a /sub b, b /sub c, a /sub c ---> delete a /sub c
//        SubClassOfRedundant redtUtil = new SubClassOfRedundant(merged.getAxioms(AxiomType.SUBCLASS_OF));
//        List<OWLSubClassOfAxiom> toRemove = redtUtil.findRedundants();
//        for (OWLAxiom ax: toRemove) {
//            RemoveAxiom removeAxiom = new RemoveAxiom(merged, ax);
//            man.applyChange(removeAxiom);
//        }
        // replace D, N with expressions
        System.out.println("Replace D and N with expressions...");
        Set<OWLSubClassOfAxiom> subclassof = merged.getAxioms(AxiomType.SUBCLASS_OF);
        for (OWLSubClassOfAxiom s : subclassof) {
            OWLClassExpression sub = s.getSubClass();
            OWLClassExpression sup = s.getSuperClass();
            String subIRI = "";
            String supIRI = "";
            if (sub.isNamed()) {
                subIRI = ((OWLClass) sub).getIRI().toString();
            }
            if (sup.isNamed()) {
                supIRI = ((OWLClass) sup).getIRI().toString();
            }
            if (map.containsKey(subIRI) || map.containsKey(supIRI)) {
                OWLClassExpression recoverSub = map.getOrDefault(subIRI, sub);
                OWLClassExpression recoverSup = map.getOrDefault(supIRI, sup);
                OWLSubClassOfAxiom recoverAX = factory.getOWLSubClassOfAxiom(recoverSub, recoverSup);
                // Add the axiom to our ontology
                AddAxiom tmpaddAx = new AddAxiom(merged, recoverAX);
                man.applyChange(tmpaddAx);
            }
        }
        // remove additional classes
        System.out.println("Removing D and N...");
        OWLEntityRemover remover = new OWLEntityRemover(merged);
        for (OWLClass namedClass: merged.getClassesInSignature()) {
            if (map.containsKey(namedClass.getIRI().toString())) {
                namedClass.accept(remover);
            }
        }
        man.applyChanges(remover.getChanges());
        // new schema = Schema.classification ( recover D and N)
        System.out.println("Infer recovered schema + delta ...");
        OWLReasoner reasoner2 = rf.createReasoner(merged, configuration);
        reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY);
        List<InferredAxiomGenerator<? extends OWLAxiom>> gens2 =
                new ArrayList<InferredAxiomGenerator<? extends OWLAxiom>>();
        gens2.add(new InferredSubClassAxiomGenerator()); //B1 \in B2 or B1 \in \negB2
        OWLOntology infOnt2 = man.createOntology();
        // Now get the inferred ontology generator to generate some inferred
        // axioms for us (into our fresh ontology). We specify the reasoner that
        // we want to use and the inferred axiom generators that we want to use.
        InferredOntologyGenerator iog2 = new InferredOntologyGenerator(reasoner2, gens2);
        iog2.fillOntology(man.getOWLDataFactory(), infOnt2);
        // merge new inferred atoms
        System.out.println("Removing ont and infOnt1...");
        man.removeOntology(ont);
        man.removeOntology(infOnt1);
        System.out.println("Merging infOnt2 with last round merged...");
        IRI mergedOntologyIRI2 = IRI.create("http://www.semanticweb.com/merged2");
        merged = merger.createMergedOntology(man, mergedOntologyIRI2);
        // remove unwanted axioms like asymmetric etc.
        System.out.println("Removing additional properties ...");
        toRemoveAxiom = new ArrayList<OWLAxiom>();
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.ASYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.SYMMETRIC_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.EQUIVALENT_OBJECT_PROPERTIES));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.REFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.IRREFLEXIVE_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.TRANSITIVE_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.INVERSE_OBJECT_PROPERTIES));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.SUB_OBJECT_PROPERTY));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.DISJOINT_CLASSES));
        toRemoveAxiom.addAll(merged.getAxioms(AxiomType.EQUIVALENT_CLASSES));

        for (OWLAxiom ax: toRemoveAxiom) {
            RemoveAxiom removeAxiom = new RemoveAxiom(merged, ax);
            man.applyChange(removeAxiom);
        }
        // remove redundants: a /sub b, b /sub c, a /sub c ---> delete a /sub c
//        redtUtil = new SubClassOfRedundant(merged.getAxioms(AxiomType.SUBCLASS_OF));
//        for (OWLAxiom ax: redtUtil.findRedundants()) {
//            RemoveAxiom removeAxiom = new RemoveAxiom(merged, ax);
//            man.applyChange(removeAxiom);
//        }
        System.out.println("Saving new ontology " + out_file);
        File inferredOntologyFile = new File(out_file);
        // Now we create a stream since the ontology manager can then write to that stream.
        try (OutputStream outputStream = new FileOutputStream(inferredOntologyFile)) {
            // We use the nt format as for the input ontology.
//             NTriplesDocumentFormat format = new NTriplesDocumentFormat();
            TurtleDocumentFormat format = new TurtleDocumentFormat();
            man.saveOntology(merged, format, outputStream);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }
}
