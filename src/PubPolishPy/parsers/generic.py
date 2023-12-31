import shutil
import os
import re
from pathlib import Path

from abc import ABC, abstractmethod

from PubPolishPy.graph import traverse_tex_tree
from PubPolishPy.plugins import PubPolishPlugin

NODEFILTERS = [
        "input",
        "include",
        "bibliography",
        "documentclass",
        "includegraphics",
        ]


class TeXProjectFormatter(ABC):
    def __init__(self, originator, basePath, force=False):
        self.iwd = os.getcwd()
        self.originator = originator
        self.projectGraph = traverse_tex_tree(originator, NODEFILTERS)
        self._filerefs = dict()
        self.basePath = basePath
        self.plugins = list()
        self.updatedFilePaths = dict()
        
        if os.path.exists(basePath):
            if force:
                shutil.rmtree(basePath)
                os.makedirs(basePath)
            else:
                raise OSError(f"Folder {basePath} exists!")
        else:
            os.makedirs(basePath)
            
    def register_plugin(self, plugin_class):
        if not issubclass(plugin_class, PubPolishPlugin):
            raise TypeError("Plugin must be a subclass of PubPolishPlugin")
        plugin = plugin_class(self)
        self.plugins.append(plugin)

    def migrate(self):
        for plugin in self.plugins:
            plugin.pre_migrate()

        self.migration_logic()
    
        for plugin in self.plugins:
            plugin.post_migrate()

    @abstractmethod
    def migration_logic(self):
        pass

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
                self.smart_copy_file(nodeName, newPath)
            else:
                with open(nodeName) as f:
                    content = f.read()
                newPath = os.path.join(self.basePath, os.path.basename(nodeName))
                edges = self.projectGraph.edges(nodeName)
                for edge in edges:
                    destNodeType = self.projectGraph.nodes[edge[1]].get('node', None)
                    newFileName = os.path.basename(edge[1])
                    pattern = patterns.get(destNodeType, basePattern)(edge[1])
                    content = re.sub(pattern, newFileName, content)
                with open(newPath, 'w') as f:
                    f.write(content)
            self.updatedFilePaths[nodeName] = newPath


    @staticmethod
    def smart_copy_file(src, dest, case_sensitive=False):
        """
        TeX Live defaults to case insesitve file matching since 2018
        So that is the default here.
        """
        src_path = Path(src)
        dest_path = Path(dest)

        if src_path.is_file():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(src_path.read_bytes())
            return

        if case_sensitive:
            regex_pattern = re.compile(re.escape(src_path.stem) + r'\..+')
        else:
            regex_pattern = re.compile(re.escape(src_path.stem) + r'\..+', re.IGNORECASE)
        
        possible_files = [f for f in src_path.parent.iterdir() if f.is_file() if regex_pattern.match(f.name)]


        if len(possible_files) > 0:
            for matched_file in possible_files:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_file = dest_path.with_name(matched_file.name)  # Preserve the original file case
                dest_file.write_bytes(matched_file.read_bytes())
            return

        raise FileNotFoundError(f"No file found for {src}")

class TeXGenericFormatter(TeXProjectFormatter):
    def __init__(self, originator, basePath="TeX_Project", **kwargs,):
        super().__init__(originator, basePath, **kwargs)

    def migration_logic(self):
        pass
