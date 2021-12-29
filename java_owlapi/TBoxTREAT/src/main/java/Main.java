import TBoxScanner.TBoxPatternGenerator;

import java.io.File;

public class Main {

    public static void main(String[] args) throws Exception {
        String task = System.getProperty("task", "Materialize");
//        String schema_file = System.getProperty("ontology", "../../resources/DBpedia-politics/dbpedia_2016-10.owl");
//        String schema_file = System.getProperty("schema", "../../resources/NELL/NELL.ontology.ttl");
        String schema_file = System.getProperty("schema", "../../outputs/cm/tbox_dllite.ttl");
//        String schema_file = System.getProperty("schema", "pizza.owl");
//        String output_dir = System.getProperty("output_dir", "output");
//        String output_dir = System.getProperty("output_dir", "../../resources/NELL/");
        String output_dir = System.getProperty("output_dir", "./");
//        String abox_file = System.getProperty("abox", "");
        String abox_file = System.getProperty("abox", "../../outputs/cm/abox.nt");
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
                Materialize2.materialize(ontologyFullPath, aboxFullPath, outputFullPath + "/materialized_tbox_abox.nt");
                break;
            case "toNT":
                FormatConverter.toNT(ontologyFullPath, outputFullPath + "/" + fileName + ".nt");
                break;
            case "DL-lite":
                DLLite.owl2dllite(ontologyFullPath, outputFullPath + "/tbox_dllite.ttl");
                break;
            case "Consistency":
                Materialize2.checkConsistency(ontologyFullPath, aboxFullPath, outputFullPath + "/tbox_and_abox.nt");
                break;
            default:
                return;
        }
    }

}
