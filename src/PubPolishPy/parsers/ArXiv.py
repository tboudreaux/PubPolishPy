import os
from hashlib import md5
import shutil
from pathlib import Path
from TexSoup import TexSoup
from TexSoup.data import BracketGroup, BraceGroup

from PubPolishPy.parsers import TeXProjectFormatter

import requests
from urllib.parse import unquote
import re

def download_file(url, dest_folder):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status() 

    cd = response.headers.get('content-disposition')
    if cd:
        fname = re.findall('filename="(.+)"', cd)
        if fname:
            filename = unquote(fname[0])
        else:
            filename = url.split('/')[-1]
    else:
        filename = url.split('/')[-1]

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    file_path = os.path.join(dest_folder, filename)

    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192): 
            if chunk:
                f.write(chunk)

    return file_path

class TeXArXivFormatter(TeXProjectFormatter):
    def __init__(self, originator, basePath="ArXiv", forcePDFLaTeX=True, **kwargs):
        super().__init__(originator, basePath, **kwargs)
        self.forcePDFLaTeX = forcePDFLaTeX
    
    def copy_additional(self):
        root = str(Path(self.originator).parent)
        extras = [
            "aassymbols.tex",
            "natbib.tex",
            "natnotes.tex"
        ]
        for extra in extras:
            if os.path.exists(os.path.join(root, extra)):
                shutil.copy2(os.path.join(root, extra), os.path.join(self.basePath, extra))

    def setupPDFLaTeX(self):
        baseName = os.path.basename(self.originator)
        rootPath = os.path.join(self.basePath, baseName)
        assert os.path.exists(rootPath), f"{rootPath} does not exist!"

        with open(rootPath, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if '\\documentclass' in line:
                lines.insert(i + 1, '\\pdfoutput=1\n')
                break
        
        with open(rootPath, 'w') as file:
            file.writelines(lines)


    def updateDocumentClassOptions(self, additionalDocClassOptions=[]):
        baseName = os.path.basename(self.originator)
        rootPath = os.path.join(self.basePath, baseName)
        assert os.path.exists(rootPath), f"{rootPath} does not exist!"

        with open(rootPath, 'r') as f:
            soup = TexSoup(f.read())

        docClass = soup.documentclass
        options = BracketGroup('twocolumn')
        docClass.args[0] = options
        with open(rootPath, 'w') as file:
            file.write(str(soup))


    def replace_acknowledgements_with_macro(self):
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        filterFunc = lambda node: list(filter(lambda x: type(x)==BraceGroup, node.args))[0].contents[0]
        baseName = os.path.basename(self.originator)
        rootPath = os.path.join(self.basePath, baseName)
        assert os.path.exists(rootPath), f"{rootPath} does not exist!"

        with open(rootPath, 'r') as file:
            content = file.read()
        soup = TexSoup(content)
        docClass = soup.documentclass
        classFilePath = filterFunc(docClass)
        if classFilePath == "aastex631":
            print(f"{YELLOW}WARNING! There is a known bug in aastex631.cls that results in linenumbering rendering in this section regardless of other options. The AASTeX6.2 class file will be automatically downloaded and used in the ArXiv target folder. This likeley will not cause any issues; however, if you are using any AASTeX 6.3 or 6.3.1 specific features it may break it. This behavior can be disabled with the --noAutoReClass command line option. {RESET}")
            path = download_file("https://journals.aas.org/wp-content/uploads/2018/08/aastex62.cls", self.basePath)
            assert os.path.exists(path), f"{path} does not exist!"
            with open(path, 'rb') as file:
                content = file.read()
            assert md5(content).hexdigest() == "3ccb99937c19b008a65ac39ebedf9ee4", "The downloaded file is not the same as the expected file."
            newBrace = BraceGroup("aastex62")
            docClass.args[1] = newBrace

        ack_env = soup.find('acknowledgments')

        if ack_env:
            ack_text = ack_env.string

            ack_env.replace_with(f'\\acknowledgments{{{ack_text}}}\n\\acknowledgments')

            with open(rootPath, 'w') as file:
                file.write(str(soup))

    def migration_logic(self):
        self.flatten()
        self.copy_additional()
        self.updateDocumentClassOptions()
        self.replace_acknowledgements_with_macro()
        if self.forcePDFLaTeX:
            self.setupPDFLaTeX()

