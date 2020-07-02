README - BabelNet API 4.0.1 (April 2018)

This package consists of a Java API to work with BabelNet, a very large
multilingual semantic network. For more information please refer to the
documentation below on how to install and run the software, as well as
our website (http://babelnet.org) and Google group
(http://groups.google.com/group/babelnet-group) for news, updates and
papers.

--------
CONTENTS
--------

This package contains the following main components:

  babelnet-api-4.0.1.jar	# Jar of the BabelNet API
  CHANGELOG			# changelog for the BabelNet API
  config/			# configuration files
  docs/				# Javadocs
  lib/				# 3rd party libraries
  LICENSE			# BabelNet API's license
  licenses/			# 3rd party libraries' licenses
  README			# this file
  resources/			# resource files needed by the API
  run-babelnetdemo.sh		# shell script to test BabelNet in Linux
  run-babelnetdemo.bat		# shell script to test BabelNet in Windows
  examples/			# Java examples source file 

------------
REQUIREMENTS
------------

We assume that you have a standard installation of the Sun Java 1.8 JDK
and all the associated programs (i.e., java, javac, etc.) in your path.

------------
INSTALLATION
------------

Currently, we provide BabelNet as a semantic network consisting
of 284 languages (English, Catalan, French, German, Italian, Spanish, Afrikaans,
Arabic, Bulgarian, Czech, Welsh, Danish, Greek, Estonian, Persian, Finnish,
Irish, Hebrew, Hindi, Croatian, Hungarian, Indonesian, Icelandic, Japanese,
Korean, Lithuanian, Latvian, Malay, Dutch, Norwegian, Polish, Portuguese,
Romanian, Russian, Slovak, Slovenian, Albanian, Serbian, Swedish, Swahili,
Tagalog, Turkish, Ukranian, Vietnamese, Chinese, Esperanto, Galician, Maltese,
Basque, Latin, etc.) and described in the papers below.
 
 
**************
1 BabelNet API
**************

In order to access BabelNet RESTFul service, it is necessary to specify a valid key 
using the "babelnet.key" property in the config/babelnet.var.properties file. To obtain 
a key, please register on http://babelnet.org/register.


You are now ready to use the API. For testing purposes we 
provide a shell script:

		      Linux:   run-babelnetdemo.sh, make sure that the file is 
			       executable by running: chmod +x run-babelnetdemo.sh.
		      Windows: run-babelnetdemo.bat


IMPORTANT: please note that, in order to enable the log4j settings, you
have to add the config folder to your classpath. For instance:

    export CLASSPATH="lib/*:babelnet-api-4.0.1.jar:config:.."
    Linux:   java -classpath lib/*:babelnet-api-4.0.1.jar:config it.uniroma1.lcl.babelnet.demo.BabelNetDemo

    Windows: java -classpath lib/*;babelnet-api-4.0.1.jar;config it.uniroma1.lcl.babelnet.demo.BabelNetDemo

******************************************************
1.1 Configuring BabelNet API within an Eclipse project
******************************************************

1) Create your Eclipse project (File -> New -> Java project, give the project a name and press Finish). 
   This creates a new folder with the project name projectFolder/ under your Eclipse workspace folder. 
2) Copy the 'config/' and 'resources/' folders from the BabelNet-API-4.0.1 folder into your 'workspace/projectFolder/'
3) Now we need to include all the 'lib/*.jar' files and the 'babelnet-api-4.0.1.jar' file in the project build classpath:
  3.1) Select the project from 'Package Explorer' tree view
  3.2) From the top bar click on 'Project' and then 'Properties'
  3.3) Once inside the 'Properties' section click on 'Java build path' and select the 'Libraries' tab
  3.4) From the right menu click on the 'Add External JARs' button
  3.5) Browse to the downloaded `BabelNet-API-4.0.1` folder, and select all the `lib/*.jar` 
       files along with the 'babelnet-api-4.0.1.jar' file
4) Next we need to include the 'config/' folder in the project build classpath:
  4.1) Select the project from 'Package Explorer' tree view
  4.2) From the top bar click on 'File' and then 'Refresh'
  4.3) From the 'Java build path' (see point 3 above) select the 'Source' tab
  4.4) Once in the 'Source' tab, click on 'Add Folder' from the right sidebar and select the downloaded 'config/' folder
5) Happy coding!! ;-)

For more information consult the guide online, http://babelnet.org/guide

****************
2 BabelNet Index
****************

To start using BabelNet with the local indices, first download the compressed index and
unpack it, e.g.:

    NOTE: For more information about how to send a request to download the BabelNet indices,
    please consult the guide at: http://babelnet.org/guide (tab: key & limits). The instructions will be inserted in the guide when
    the indices will be downloadable. Thank you for your patience.
    
    # unpack the archives
    tar xjvf babelnet-4.0.1-index.tar.bz2

The BabelNet-4.0.1 directory now contains all the unpacked indices.

Next, tell the API where to find BabelNet by setting the "babelnet.dir"
property in the config/babelnet.var.properties file. For instance,
assuming you unpacked BabelNet in the "/home/your_user/BabelNet-4.0.1",
you simply need to write the following within "config/babelnet.var.properties":

    babelnet.dir=/home/your_user/BabelNet-4.0.1

If your WordNet is not installed in the standard location 
(/usr/local/share/wordnet-3.0), please change the corresponding property
in the config/jlt.var.properties file:

# simply put /usr/local/share/wordnet
jlt.wordnetPrefix=/usr/local/share/wordnet

to the prefix of your WordNet path without the "-3.0" suffix. For instance,
if WordNet 3.0 is located in /opt/WordNet-3.0, you should change the property
to:

jlt.wordnetPrefix=/opt/WordNet

You are now ready to use the API with local indices.

---------- 
REFERENCES 
----------

If you want to refer to BabelNet in your scientific work, please cite
this paper:

Navigli, R. and Ponzetto, S. P. (2012a): BabelNet: The Automatic
Construction, Evaluation and Application of a Wide-Coverage Multilingual
Semantic Network. Artificial Intelligence, 193, 217-250.

If you want to refer to the BabelNet dump, API or BabelNetXplorer (our
Web-based GUI for BabelNet available at http://babelnet.org), please
cite this paper:

Navigli, R. and Ponzetto, S. P. (2012b): BabelNetXplorer: A platform for
multilingual lexical knowledge base access and exploration. In:
Companion Volume to the Proceedings of the 21st World Wide Web
Conference, Lyon, France, 16-20 April 2012, pp. 393-396.

-------
AUTHORS
-------

Roberto Navigli, Sapienza University of Rome
(navigli@di.uniroma1.it)

Francesco Cecconi, Babelscape srl
(cecconi@babelscape.com)

Francesco Maria Elia, Babelscape srl
(elia@babelscape.com)

Additional credits go to:
- Daniele Vannella for working on versions 2.x and 3.x
- Simone Paolo Ponzetto for working on versions 1.x

---------
COPYRIGHT
---------

BabelNet and the Babelnet API are licensed under a Creative Commons 
Attribution-Noncommercial-Share Alike 3.0 License. 
See the file LICENSE for details.

-------
CONTACT
-------

Please feel free to get in touch with us for any question or problem you
may have using the following Google group:

  http://groups.google.com/group/babelnet-group

---------------
ACKNOWLEDGMENTS
---------------

BabelNet has received funding from the European Research Council (ERC) 
under grant agreement No. 259234.
