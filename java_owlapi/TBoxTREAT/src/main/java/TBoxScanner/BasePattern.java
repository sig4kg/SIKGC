package TBoxScanner;

import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.reasoner.OWLReasoner;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public abstract class BasePattern implements IPattern{
    protected String outputDir;
    protected String filePrefix = "TBoxPattern";
    protected PrintWriter pw = null;
    protected OWLDataFactory factory;
    protected OWLReasoner reasoner;
    protected OWLOntology ont;

    protected PrintWriter GetPrintWriter(String index) throws IOException{
        File f = new File(this.outputDir + "/" + this.filePrefix + "_" + index + ".txt");
        FileWriter fw = new FileWriter(f);
        this.pw = new PrintWriter(fw);
        return this.pw;
    }

    public BasePattern SetOWLAPIContext(OWLOntology ont, OWLReasoner reasoner, OWLDataFactory factory, String outputDir) {
        this.ont = ont;
        this.reasoner = reasoner;
        this.factory = factory;
        this.outputDir = outputDir;
        return this;
    }
}
