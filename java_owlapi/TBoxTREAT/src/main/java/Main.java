import TBoxScanner.TBoxPatternGenerator;

import java.io.File;



public class Main {
    public static void main(String[] args) throws Exception {
        String koncludeBinary = System.getProperty("koncludeBinary", "../Konclude/Binaries/Konclude");
        String task = System.getProperty("task", "TBoxScanner");
//        String schema_file = System.getProperty("schema", "../../resources/DBpediaP/tbox.nt");
//        String schema_file = System.getProperty("schema", "../../resources/DBpedia-politics/resized_tbox.nt");
//        String schema_file = System.getProperty("schema", "../../resources/DBpediaP/dbpedia_2016-10.owl");
//        String schema_file = System.getProperty("schema", "../../resources/NELL.ontology.ttl");
//        String schema_file = System.getProperty("schema", "../../resources/NELL/tbox_abox.nt");
        String schema_file = System.getProperty("schema", "../../resources/TREAT/tbox.nt");
//        String schema_file = System.getProperty("schema", "pizza.owl");
//        String schema_file = System.getProperty("schema", "ontology_log_instance.nt");
        String output_dir = System.getProperty("output_dir", "../../resources/TREAT/tbox_patterns");
//        String output_dir = System.getProperty("output_dir", "../../resources/DBpedia-politics/tbox_patterns");
//        String output_dir = System.getProperty("output_dir", "../../resources/DBpedia-politics/");
//        String output_dir = System.getProperty("output_dir", "output/");
        String type_file = System.getProperty("types", "output/types.txt");
        String rel_file = System.getProperty("rels", "output/properties.txt");
//        String abox_file = System.getProperty("abox", "../../resources/treat/");
        System.out.println(task + "\t" + schema_file + "\t" + output_dir);
        System.out.println("koncludeBinary: " + koncludeBinary);
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
        System.out.println("ontology file path: " + ontologyFullPath);
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
                Materialize materialize = new Materialize(koncludeBinary, outputFullPath + "/");
                materialize.materialize_konclude(ontologyFullPath);
                break;
            case "toNT":
                TBoxConverter.toNT(ontologyFullPath, outputFullPath + "/" + fileName + ".nt");
                break;
            case "DL-lite":
                DLLite dlliteCvt= new DLLite(koncludeBinary, outputFullPath + "/");
                dlliteCvt.owl2dllite(ontologyFullPath);
                break;
            case "Consistency":
                Materialize materialize2 = new Materialize(koncludeBinary, outputFullPath + "/");
                materialize2.checkConsistency(ontologyFullPath,outputFullPath + "/tbox_and_abox.nt");
                break;
            case "SubsetTBox":
                TBoxConverter.getTBoxSubset(ontologyFullPath, outputFullPath + "/less_tbox.nt", type_file, rel_file);
                break;
            default:
                return;
        }
    }

}
