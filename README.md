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
This structure is great for organization while writing the manuscript as it keeps sections seperated. However, The Astrophysical Journal implicitly requires that all uploaded manuscripts be in a flat directory structure.

While this is not technically challenging to manually update paths it is tedious. It is even more tedious when you have to do it multiple times during the peer review and copy editing process.

PubPolishPy aimes to resolve this challenfe. 

Currently, PubPolishPy recursivley parses your LaTex souce and builds a graoh of all of the local file dependencies it can find. These can be "flattened" into a directory structure. If you flatten them all the needed files will be copied from where there are to a new folder and all of the paths within the tex document will be updated to point there. Note, this is not an inplace operation. <b>NO CHANGES WILL BE MADE TO YOUR ORIGINAL TEX SOURCE</b>. Rather, effectlvley completely new tex project is built from your existing project but with a different structure.

More Generally,PubPolishPy aims to provide a framework which destinations can be added into and can parse any tex project to any destination (such as MNRAS, ArXiV, ApJ, or other journals). This is done through the parsers module which impliments a generic parser which other parsers can inherit from. Currently only ApJ and ArXiv are implimented.

## Installation
PubPolishPy may be installed from source. I hope to have it in PyPy soon

```bash
git clone git@github.com:tboudreaux/PubPolishPy.git
cd PubPolishPy
pip instal .
```

If you wish to develope for pub polish py replace the final line with

```bash
pip install -e .
```

## Usage
PubPolishPy may be used through either a command line script or a function call.

Using progratically in python (based on the above example directory structure and assuming the user is in the root (where the makefile it))

```python
from PubPolishPy.parsers import TeXApJFormatter

ApJ = TeXApJFormatter("src/ms.tex")
ApJ.migrate()
```

If you want to invoke it from the command line use the following script

```bash
pubPolish --target ApJ --dest ApJSubmission src/ms.tex
```
Valid submission locations are defined in a dictionary which connects the key (ApJ in this case) to the class. The dest folder defines where the flattened project will end up. The script then runs effectivley the same code as is presented above

