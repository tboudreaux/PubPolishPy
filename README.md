<h1 align="center"> PubPolishPy </h1>
<p align="center">
  <img src="https://github.com/tboudreaux/PubPolishPy/blob/master/assets/logo/PubPolishLogo-Dark.png?raw=true" alt="Logo of Project">
</p>

# A Python framework for reorganizing tex documents for submission to different sources
Different destinations for TeX documents often require (implicitly or explicitly) different
structures of a project. For example, I tend to organize all of my projects in the following structure


```bash
├── makefile
├── SelfConsistentModelingOfNGC2808.aux
├── SelfConsistentModelingOfNGC2808.bbl
├── SelfConsistentModelingOfNGC2808.blg
├── SelfConsistentModelingOfNGC2808.log
├── SelfConsistentModelingOfNGC2808.out
├── SelfConsistentModelingOfNGC2808.pdf
├── src
│   ├── aasjournal.bst
│   ├── aassymbols.tex
│   ├── aastex631.cls
│   ├── appendicies
│   ├── bib
│   │   └── ms.bib
│   ├── figures
│   │   ├── BestFit.png
│   │   ├── BestFitResults.pdf
│   │   ├── ClusterAnalysis.pdf
│   │   ├── DistributionOfErrors.pdf
│   │   ├── ExtractedIsoFit.pdf
│   │   ├── HeliumMeanOffset.pdf
│   │   ├── notebookFigures -> ../../FigureMakeing/Figures
│   │   └── photometricOffset.pdf
│   ├── ms.tex
│   ├── natbib.tex
│   ├── natnotes.tex
│   └── sections
│       ├── AtmopshericModels.tex
│       ├── conclusion.tex
│       ├── fidanka.tex
│       ├── fitting.tex
│       ├── intro.tex
│       ├── modeling.tex
│       ├── observations.tex
│       └── results.tex

```
This structure is great for organization while writing the manuscript as it keeps sections separated. However, The Astrophysical Journal implicitly requires that all uploaded manuscripts be in a flat directory structure.

While this is not technically challenging to manually update paths it is tedious. It is even more tedious when you have to do it multiple times during the peer review and copy editing process.

PubPolishPy aims to resolve this challenge. 

Currently, PubPolishPy recursively parses your LaTex souce and builds a graph of all of the local file dependencies it can find. These can be "flattened" into a directory structure. If you flatten them all the needed files will be copied from where there are to a new folder and all of the paths within the tex document will be updated to point there. Note, this is not an in place operation. <b>NO CHANGES WILL BE MADE TO YOUR ORIGINAL TEX SOURCE</b>. Rather, effectively completely new tex project is built from your existing project but with a different structure.

More Generally,PubPolishPy aims to provide a framework which destinations can be added into and can parse any tex project to any destination (such as MNRAS, ArXiV, ApJ, or other journals). This is done through the parsers module which implements a generic parser which other parsers can inherit from. Currently only ApJ and ArXiv are implemented.

## Installation
PubPolishPy may be installed from source. I hope to have it in PyPy soon

```bash
git clone git@github.com:tboudreaux/PubPolishPy.git
cd PubPolishPy
pip instal .
```

If you wish to develop for PubPolishPy replace the final line with

```bash
pip install -e .
```

## Usage
PubPolishPy may be used through either a command line script or a function call.

Using pragmatically in python (based on the above example directory structure and assuming the user is in the root (where the makefile it))

```python
from PubPolishPy.parsers import TeXApJFormatter

ApJ = TeXApJFormatter("src/ms.tex")
ApJ.migrate()
```

If you want to invoke it from the command line use the following script

```bash
pubPolish --target ApJ --dest ApJSubmission src/ms.tex
```
Valid submission locations are defined in a dictionary which connects the key (ApJ in this case) to the class. The dest folder defines where the flattened project will end up. The script then runs effectively the same code as is presented above

## Targets
Currently there are only two targets implemented as these are the targets which I use. If and when I submit to other targets I will build them in, otherwise I am very open to others submitting targets; however, I likely will not work on them spontaneously.
| Target                       | Command Line Key | Formatter Object Name | Details                                                                                                                                                     |
| ---------------------------- | ---------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The Astrophysical Journal    | ApJ              | TeXApJFormatter       | Flattens the latex directory and copies additional AASTeX files                                                                                             |
| The ArXiv                    | ArXiv            | TeXArXivFormatter     | Flattens the latex directory, copies additional AASTeX files if available, changes the acknowledgments environment to the macro, downloads the aastex62.cls file if aastex631 is detected, sets the document class options to twocolumn (removes other options if present). |
| Generic    | Generic              | TeXGenericFormatter       | Does not apply any additional logic.                                                                                             |


## Example Makefile
For sake of completion I have included a makefile which I use and includes PubPolishPy. Note the make rules for the arxiv and ApJ

```make
LTC="pdflatex"
BTC="bibtex"

ANAME="SelfConsistentModelingOfNGC2808"

SRCDIR="src/"
FIGDIR="src/figures"
BIBDIR="src/bibliography"
APEDIR="src/appendicies"

ApJDIR="ApJ"
ArXivDIR="ArXiv"

MANFILE="ms.tex"
MANPATH="$(SRCDIR)/$(MANFILE)"
ApJMANPATH="$(ApJDIR)/$(MANFILE)"
ArXivMANPATH="$(ArXivDIR)/$(MANFILE)"


ASSET_FILES = $(shell find ./src/ -regex '.*\(tex\|pdf\)$')


TFLAGS="-jobname=$(ANAME)"

.PHONY: manuscript apj arxiv clean veryclean

default: manuscript

all: manuscrip apj arxiv

manuscript: ./src/$(ASSET_FILES)
        $(LTC) $(TFLAGS) $(MANPATH)
        $(BTC) $(ANAME)
        $(LTC) $(TFLAGS) $(MANPATH)
        $(LTC) $(TFLAGS) $(MANPATH)


apj:
        if [ -d "ApJ" ]; then rm -rf "ApJ"; fi
        pubPolish --target ApJ --dest $(ApJDIR) $(MANPATH)
        cd $(ApJDIR) && $(LTC) $(TFLAGS) $(MANFILE)
        cd $(ApJDIR) && $(BTC) $(ANAME)
        cd $(ApJDIR) && $(LTC) $(TFLAGS) $(MANFILE)
        cd $(ApJDIR) && $(LTC) $(TFLAGS) $(MANFILE)

arxiv:
        if [ -d "ArXiv" ]; then rm -rf "ArXiv"; fi
        pubPolish --target ArXiv --dest $(ArXivDIR) $(MANPATH)
        cd $(ArXivDIR) && $(LTC) $(TFLAGS) $(MANFILE)
        cd $(ArXivDIR) && $(BTC) $(ANAME)
        cd $(ArXivDIR) && $(LTC) $(TFLAGS) $(MANFILE)
        cd $(ArXivDIR) && $(LTC) $(TFLAGS) $(MANFILE)


clean:
        -rm $(ANAME).blg
        -rm $(ANAME).bbl
        -rm $(ANAME).aux
        -rm $(ANAME).log
        -rm $(ANAME).out

veryclean: clean
        -rm $(ANAME).pdf
```

## Plugins
Recognizing that every project is different and that it is infeasible for me to impliment a catch all system, PubPolishPy comes with a simple plugin system to allow users to define their own migration logic without diving into fully adding new target classes. 

### Building a Plugin
Let us say that for your project, you want to flatten the directory structure and then after you want to replace all instances of the word foo with the word bar in every tex file. Below I will write a plugin that does this

```python
from PubPolishPy.parsers import TeXGenericFormatter
from PubPolishPy.plugins import PubPolishPlugin
import re

CustomPlugin(PubPolishPlugin):
    def post_migrate(self):
        for nodeName, nodeData in self.formatter.projectGraph.nodes(data=True):
            if nodeData.get('tex', False) == True:
                with open(self.formatter.updatedFilePaths[nodeName], 'r') as f:
                    content = f.read()
                newContent = re.sub('foo', 'bar', content)
                with open(self.formatter.updatedFilePaths[nodeName], 'w') as f:
                    f.write(newContent)

    def pre_migration(self):
        self.formatter.flatten() # If using the generic formatter then there is no default mogration logic between pre and post.
        pass

formatter = TeXGenericFormatter("src/main.tex")
formatter.register_plugin(CustomPlugin)
formatter.migrate()
```

Within formatter (or any child classes) pre_migrate methods will be called before the migration_logic method which all child classes must impliment while post_migrate methods will be called after migration_logic. ApJ and ArXiv targets impliment migration logic; however, the generic formatter simply passes when migration logic is called allowing any migration logic at all to be written using a plugin. Note that since there is nothing happening between pre and post migration for the generic formatter their names become somewhat confusing. The Key point is that pre always runs first then migration_logic() then post.
