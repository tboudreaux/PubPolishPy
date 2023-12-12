import shutil
import os
import re
from pathlib import Path

from PubPolishPy.graph import traverse_tex_tree

NODEFILTERS = [
        "input",
        "include",
        "bibliography",
        "documentclass",
        "includegraphics",
        ]

class TeXProjectFormatter:
    def __init__(self, originator, basePath, force=False):
        self.iwd = os.getcwd()
        self.originator = originator
        self.projectGraph = traverse_tex_tree(originator, NODEFILTERS)
        self._filerefs = dict()
        self.basePath = basePath
        
        if os.path.exists(basePath):
            if force:
                shutil.rmtree(basePath)
                os.makedirs(basePath)
            else:
                raise OSError(f"Folder {basePath} exists!")
        else:
            os.makedirs(basePath)
    
    def flatten(self):
        basePattern = lambda x: x
        patterns = {
            'bib' : lambda x: x + "(?:.bib)?",
            'documentclass': lambda x : x + "(?:.cls|.class)?"
        }
        for nodeName, nodeData in self.projectGraph.nodes(data=True):
            filename = os.path.basename(nodeName)
            newPath = os.path.join(self.basePath, filename)
            if not nodeData.get('tex', False):
                print(nodeName, newPath)
                self.smart_copy_file(nodeName, newPath)
            else:
                with open(nodeName) as f:
                    content = f.read()
                newNodeName = os.path.join(self.basePath, os.path.basename(nodeName))
                edges = self.projectGraph.edges(nodeName)
                for edge in edges:
                    destNodeType = self.projectGraph.nodes[edge[1]].get('node', None)
                    newFileName = os.path.basename(edge[1])
                    pattern = patterns.get(destNodeType, basePattern)(edge[1])
                    content = re.sub(pattern, newFileName, content)
                with open(newNodeName, 'w') as f:
                    f.write(content)
                    
    @staticmethod
    def smart_copy_file(src, dest, case=False):
        src_path = Path(src)
        dest_path = Path(dest)

        if src_path.is_file():
            dest_path.parent.mkdir(parents=True, exist_ok=True)  
            dest_path.write_bytes(src_path.read_bytes())
            return

        regex_pattern = re.compile(re.escape(src_path.stem) + r'\..+')
        possible_files = [f for f in src_path.parent.iterdir() if f.is_file() and regex_pattern.match(f.name)]

        if possible_files:
            dest_path.parent.mkdir(parents=True, exist_ok=True)  # Create destination directory if it doesn't exist
            dest_file = dest_path.with_name(possible_files[0].name)  # Use the name of the found file for the destination
            dest_file.write_bytes(possible_files[0].read_bytes())
            return

        raise FileNotFoundError(f"No file found for {src}")
