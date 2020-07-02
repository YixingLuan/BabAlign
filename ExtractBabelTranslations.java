import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;
import java.io. *;
import java.util. *;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.StandardCharsets;

import com.babelscape.util.UniversalPOS;
import com.google.common.collect.Multimap;

import it.uniroma1.lcl.babelnet.BabelNet;
import it.uniroma1.lcl.babelnet.BabelNetQuery;
import it.uniroma1.lcl.babelnet.BabelNetUtils;
import it.uniroma1.lcl.babelnet.BabelSense;
import it.uniroma1.lcl.babelnet.BabelSenseComparator;
import it.uniroma1.lcl.babelnet.BabelSynset;
import it.uniroma1.lcl.babelnet.BabelSynsetComparator;
import it.uniroma1.lcl.babelnet.BabelSynsetID;
import it.uniroma1.lcl.babelnet.WordNetSynsetID;
import it.uniroma1.lcl.babelnet.BabelSynsetRelation;
import it.uniroma1.lcl.babelnet.InvalidSynsetIDException;
import it.uniroma1.lcl.babelnet.data.BabelGloss;
import it.uniroma1.lcl.babelnet.data.BabelImage;
import it.uniroma1.lcl.babelnet.data.BabelSenseSource;
import it.uniroma1.lcl.jlt.util.Language;
import it.uniroma1.lcl.jlt.util.ScoredItem;

/**
 * A demo class to test {@link BabelNet}'s various features.
 *
 * @author cecconi, navigli, vannella
 * @see it.uniroma1.lcl.babelnet.test.BabelNetTest
 * @see it.uniroma1.lcl.babelnet.test.BabelSenseTest
 * @see it.uniroma1.lcl.babelnet.test.BabelSynsetTest
 */
public class ExtractBabelTranslations { 

    public static void saveSynsetsFromID(String wordlistPath, String outPath) {
        BabelNet bn = BabelNet.getInstance();
        BufferedReader reader;
        try {
            System.out.println("starting to extract...");

            File fout = new File(outPath);
            FileOutputStream fos = new FileOutputStream(fout);
            OutputStreamWriter bw = new OutputStreamWriter(fos, StandardCharsets.UTF_8);

			reader = new BufferedReader(new FileReader(wordlistPath));
			String line = reader.readLine();
			BabelSynset by;
			String clstrStr;
			while (line != null) {
                clstrStr="";
                try{
                    by = bn.getSynset(new BabelSynsetID(line));
                    for (BabelSense sense : by.getSenses())
                        clstrStr+=sense.toString().replace("\n"," ") + "\t";

                    if (!(clstrStr.equals("")))
                    {
                        bw.write(line + "\t" + clstrStr+ "\n");
                    }
                }catch (NullPointerException ex) {}

                line = reader.readLine();
            }
            bw.close();
            reader.close();
        } catch (IOException ex) {
            System.out.println("Error in IO!");
        }
    }

    /**
	 * Just for testing
	 *
	 * @param args the demo arguments
	 *
	 */
    static public void main(String[] args) {
        try {

            if (args.length != 2){
                System.out.println("please specify all 2 arguments");
                System.out.println("Input_name Output_name");
                System.exit(1);
            }

            String IdListPath = args[0];
            String SynOutPath = args[1];
            saveSynsetsFromID(IdListPath, SynOutPath);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
