package ReasonerUtils;

import org.semanticweb.owlapi.reasoner.OWLReasoner;

import java.io.File;
import java.util.Random;

public abstract class ReasonerBase  implements IReasonerUtil {
    protected String output_dir;
    private Random r = new Random();
    public OWLReasoner reasoner = null;
    protected String getTmpName(String filePrefix) {
        int i = r.nextInt(100);
        return this.output_dir + filePrefix + i + ".xml";
    }

    protected Boolean waitUntilFileSaved(String fileName, int timeout) {
        int i = timeout;
        File file = new File(fileName);
        while (!file.exists()) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
            }
            if (--i <= 0) {
                System.out.println("Saving file timeout after " + timeout + " seconds");
                return false;
            }
        }
        System.out.println(fileName + " has  been saved.");
        return true;
    }
}
