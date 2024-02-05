import networkx as nx
import os

from TexSoup import TexSoup
from TexSoup.data import BraceGroup
import re
import difflib


def extract_paths(s):
    # Regular expression to match Unix paths
    path_regex = r"/[^ \n\r\t,()<>:\"\\|?*]*[^ \n\r\t,()<>:\"\\|?*:/]"
    potential_paths = re.findall(path_regex, s)
    return [path for path in potential_paths if os.path.exists(path)]

def find_closest_path(target, paths):
    target_filename = os.path.basename(target)
    filenames = [os.path.basename(path) for path in paths]
    close_matches = difflib.get_close_matches(target_filename, filenames)
    if close_matches:
        closest_filename = close_matches[0]
        return paths[filenames.index(closest_filename)]
    else:
        return None

def parse_and_add_nodes(file, g, nodeFilters, root):
    g.nodes[file]['complete'] = True
    filterFunc = lambda node: list(filter(lambda x: type(x)==BraceGroup, node.args))[0].contents[0]
    oFName = os.path.join(root, file) if not file.startswith(root) else file
    with open(oFName, 'r') as f:
        contents = f.read()
    soup = TexSoup(contents)
    for nodeType in nodeFilters:
        nodeElements = soup.find_all(nodeType)
        tex = True if nodeType in ['input', 'include'] else False
        for node in nodeElements:
            nodeContent = filterFunc(node)
            g.add_node(nodeContent, tex=tex, nodeType=nodeType, complete=False)
            g.add_edge(file, nodeContent)
        
    # Recursive calls for sub-nodes
    for nodeName in [x for x,y in g.nodes(data=True) if y['nodeType'] in ['input', 'include']]:
        if not g.nodes[nodeName]['complete'] and g.nodes[nodeName]['tex']:
            parse_and_add_nodes(nodeName, g, nodeFilters, root)

def traverse_tex_tree(file, nodeFilters, root):
    G = nx.DiGraph()
    rootFilePath = os.path.join(root, file)
    G.add_node(rootFilePath, complete=True, tex=True, nodeType='root')
    parse_and_add_nodes(rootFilePath, G, nodeFilters, root)
    return G

            

