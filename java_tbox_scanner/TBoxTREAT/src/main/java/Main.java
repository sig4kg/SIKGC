import TBoxScanner.TBoxPatternGenerator;

import java.io.File;

public class Main {

    public static void main(String[] args) throws Exception {
//        if(args.length == 0) {
//            System.out.println("Usage:\n-Dtask Materialize/TBoxScanner/ALlClass\n-Dontology ontology_file\n-Doutput_dir output_dir");
//            System.exit(-1);
//        }
        String task = System.getProperty("task", "AllClass");
        String ontoloty_file = System.getProperty("ontology", "data/dbpedia_2016-10.owl");
//        String ontoloty_file = System.getProperty("ontology", "data/NELL.ontology.ttl");
//        String ontoloty_file = System.getProperty("ontology", "data/FBSchemaWithDisjoint.owl");
        String output_dir = System.getProperty("output_dir", "output/dbpedia");
        System.out.println(task+ "\t"+ ontoloty_file + "\t" + output_dir);
        java.net.URL url = Main.class.getProtectionDomain().getCodeSource()
                .getLocation();

        String filePath = java.net.URLDecoder.decode(url.getPath(), "utf-8");
        System.out.println("filePath: " + filePath);
        String rootPath;
        if (filePath.endsWith(".jar")) {
            rootPath = filePath.substring(0, filePath.lastIndexOf("/") + 1);
        } else{
            rootPath = filePath.substring(0, filePath.lastIndexOf("target"));
        }
        System.out.println("rootPath: " + rootPath);
        File outputFull = new File(rootPath + output_dir);
        if(!outputFull.exists() || !outputFull.isDirectory()) {
            if(outputFull.mkdirs()) {
                System.out.println("created output dir: " + outputFull.getAbsolutePath());
            } else {
                System.out.println("failed to make dir for: " + outputFull.getAbsolutePath());
            }
        } else {
            System.out.println(outputFull.getAbsolutePath() + " exists, skip creating dir");
        }
        String outputFullPath = outputFull.getAbsolutePath();
        String ontologyFullPath = rootPath + ontoloty_file;
        TBoxPatternGenerator tboxScanner = new TBoxPatternGenerator(ontologyFullPath, outputFullPath);
        switch (task) {
            case "TBoxScanner":
                tboxScanner.GeneratePatterns();
            case "AllClass":
                tboxScanner.getAllClasses();
            default:
        }
    }

}
