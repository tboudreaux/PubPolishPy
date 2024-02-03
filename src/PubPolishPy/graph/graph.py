import networkx as nx
import os

from TexSoup import TexSoup
from TexSoup.data import BraceGroup

def parse_and_add_nodes(file, g, nodeFilters, root):
    g.nodes[file]['complete'] = True
    filterFunc = lambda node: list(filter(lambda x: type(x)==BraceGroup, node.args))[0].contents[0]
    with open(file, 'r') as f:
        contents = f.read()
    soup = TexSoup(contents)
    for nodeType in nodeFilters:
        nodeElements = soup.find_all(nodeType)
        tex = True if nodeType in ['input', 'include'] else False
        for node in nodeElements:
            nodeContent = os.path.join(root, filterFunc(node))
            g.add_node(nodeContent, tex=tex, nodeType=nodeType, complete=False)
            g.add_edge(file, nodeContent)
        
    # Recursive calls for sub-nodes
    for nodeName in [x for x,y in g.nodes(data=True) if y['nodeType'] in ['input', 'include']]:
        if not g.nodes[nodeName]['complete'] and g.nodes[nodeName]['tex']:
            parse_and_add_nodes(nodeName, g, nodeFilters, root)

def traverse_tex_tree(file, nodeFilters, root):
    G = nx.DiGraph()
    G.add_node(os.path.join(root, file), complete=True, tex=True, nodeType='root')
    parse_and_add_nodes(os.path.join(root,file), G, nodeFilters, root)
    return G

            

