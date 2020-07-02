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

// This code is taken and modified from the official BabelNet API guide

/**
 * A demo class to test {@link BabelNet}'s various features.
 *
 * @author cecconi, navigli, vannella
 * @see it.uniroma1.lcl.babelnet.test.BabelNetTest
 * @see it.uniroma1.lcl.babelnet.test.BabelSenseTest
 * @see it.uniroma1.lcl.babelnet.test.BabelSynsetTest
 */
public class ExtractBabelSynsetIDs {


    public static void saveSynsetsIds(String wordlistPath, String outPath, Language lang) {
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
			String synsetsStr;
			while (line != null) {
                synsetsStr="";
                try{
                    for (BabelSynset synset : bn.getSynsets(line, lang))
                    {
                        synsetsStr+=synset.getID() + " ";
                    }

                    if (!(synsetsStr.equals("")))
                    {
                        bw.write(line + "\t" + synsetsStr+ "\n");
                    }
                }catch (NullPointerException ex) {}

                line = reader.readLine();
            }
            bw.close();
            reader.close();
        } catch (IOException ex) {
            System.out.println(ex);
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

            if (args.length != 3){
                System.out.println("please specify all 3 arguments");
                System.out.println("Input_name Output_name Language_code");
                System.exit(1);
            }
            
            String WordListPath = args[0];
            String IdOutPath = args[1];
            // cannot directly pass string as an object (Language class is an Enum --> use valueOf if want to use string)
            String sourceLang = args[2]; 
            // saveSynsetsIds(WordListPath, IdOutPath, Language.EN);
            saveSynsetsIds(WordListPath, IdOutPath, Language.valueOf(sourceLang));


        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
