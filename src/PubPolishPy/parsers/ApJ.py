import os
import shutil
from pathlib import Path

from PubPolishPy.parsers import TeXProjectFormatter

class TeXApJFormatter(TeXProjectFormatter):
    def __init__(self, originator, basePath="ApJ", **kwargs):
        super().__init__(originator, basePath, **kwargs)
    
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
                
    def migrate(self):
        super().migrate()
        self.copy_additional()
