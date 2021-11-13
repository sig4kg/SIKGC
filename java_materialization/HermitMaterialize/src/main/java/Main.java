import java.io.File;

public class Main {

    public static void main(String[] args) throws Exception {
//        if(args.length == 0) {
//            System.out.println("Usage:\n-Dtask Materialize/TBoxScanner/ALlClass\n-Dontology ontology_file\n-Doutput_dir output_dir");
//            System.exit(-1);
//        }
        String ontoloty_file = System.getProperty("ontology", "data/dbpedia_2016-10.owl");
//        String ontoloty_file = System.getProperty("ontology", "data/NELL.ontology.ttl");
        String output_dir = System.getProperty("output_dir", "output");
        System.out.println("Materialize"+ "\t"+ ontoloty_file + "\t" + output_dir);
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
        String fileName = ontoloty_file.substring(ontoloty_file.lastIndexOf('/') + 1, ontoloty_file.lastIndexOf('.')) + ".owl";
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
        Materialize.materialize(ontologyFullPath, outputFullPath + "/materialized_" + fileName);
    }
}
