import TBoxScanner.TBoxPatternGenerator;

import java.io.File;

public class Main {

    public static void main(String[] args) throws Exception {
        String task = System.getProperty("task", "DL-lite");
//        String schema_file = System.getProperty("ontology", "../../resources/DBpedia-politics/dbpedia_2016-10.owl");
        String schema_file = System.getProperty("schema", "../../resources/NELL/NELL.ontology.ttl");
//        String schema_file = System.getProperty("ontology", "pizza.owl");
//        String output_dir = System.getProperty("output_dir", "output");
        String output_dir = System.getProperty("output_dir", "../../resources/NELL/");
        String abox_file = System.getProperty("abox", "");
        System.out.println(task + "\t" + schema_file + "\t" + output_dir);
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
        String ontologyFullPath = rootPath + schema_file;
        String aboxFullPath = abox_file.equalsIgnoreCase("")? "":rootPath + abox_file;
        System.out.println("ontology file path: " + ontologyFullPath);
        System.out.println("abox file path: " + aboxFullPath);
        TBoxPatternGenerator tboxScanner = null;
        String fileName = schema_file.substring(schema_file.lastIndexOf('/') + 1, schema_file.lastIndexOf('.'));
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
                Materialize2.materialize(ontologyFullPath, aboxFullPath, outputFullPath + "/materialized_" + fileName + ".nt");
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
