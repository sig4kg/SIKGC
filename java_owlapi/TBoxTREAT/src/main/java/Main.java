import TBoxScanner.TBoxPatternGenerator;

import java.io.File;

public class Main {

    public static void main(String[] args) throws Exception {
        String task = System.getProperty("task", "DL-lite");
//        String ontoloty_file = System.getProperty("ontology", "../../resources/DBpedia-politics/dbpedia_2016-10.owl");
//        String ontoloty_file = System.getProperty("ontology", "data/tbox_abox.nt");
//        String ontoloty_file = System.getProperty("ontology", "../../resources/NELL/NELL.ontology.ttl");
        String ontoloty_file = System.getProperty("ontology", "pizza.owl");
        String output_dir = System.getProperty("output_dir", "output");
//        String ontoloty_file = System.getProperty("ontology", "data/FBSchemaWithDisjoint.owl");
//        String output_dir = System.getProperty("output_dir", "../../resources/NELL-patterns/");
        System.out.println(task + "\t" + ontoloty_file + "\t" + output_dir);
        java.net.URL url = Main.class.getProtectionDomain().getCodeSource()
                .getLocation();

        String filePath = java.net.URLDecoder.decode(url.getPath(), "utf-8");
        System.out.println("filePath: " + filePath);
        String rootPath;
        if (filePath.endsWith(".jar")) {
            rootPath = filePath.substring(0, filePath.lastIndexOf("/") + 1);
        } else {
            rootPath = filePath.substring(0, filePath.lastIndexOf("target"));
        }
        System.out.println("rootPath: " + rootPath);
        File outputFull = new File(rootPath + output_dir);
        if (!outputFull.exists() || !outputFull.isDirectory()) {
            if (outputFull.mkdirs()) {
                System.out.println("created output dir: " + outputFull.getAbsolutePath());
            } else {
                System.out.println("failed to make dir for: " + outputFull.getAbsolutePath());
            }
        } else {
            System.out.println(outputFull.getAbsolutePath() + " exists, skip creating dir");
        }
        String outputFullPath = outputFull.getAbsolutePath();
        String ontologyFullPath = rootPath + ontoloty_file;
        System.out.println("ontology file path: " + ontologyFullPath);
        TBoxPatternGenerator tboxScanner = null;
        String fileName = ontoloty_file.substring(ontoloty_file.lastIndexOf('/') + 1, ontoloty_file.lastIndexOf('.'));
        switch (task) {
            case "TBoxScanner":
                tboxScanner = new TBoxPatternGenerator(ontologyFullPath, outputFullPath);
                tboxScanner.GeneratePatterns();
                break;
            case "AllClass":
                tboxScanner = new TBoxPatternGenerator(ontologyFullPath, outputFullPath);
                tboxScanner.getAllClasses();
                break;
            case "Materialize":
                Materialize.materialize(ontologyFullPath, outputFullPath + "/materialized_" + fileName + ".nt");
                break;
            case "toNT":
                FormatConverter.toNT(ontologyFullPath, outputFullPath + "/" + fileName + ".nt");
                break;
            case "DL-lite":
                DLLite.owl2dllite(ontologyFullPath, outputFullPath + "/" + fileName + "_dllite.ttl");
                break;
            default:
                return;
        }
    }

}
