import networkx as nx

from TexSoup import TexSoup
from TexSoup.data import BraceGroup

def parse_and_add_nodes(file, g):
    with open(file, 'r') as f:
        contents = f.read()
    soup = TexSoup(contents)
    inputs = [x.contents[0] for x in soup.find_all("input")]
    includes = [x.contents[0] for x in soup.find_all("include")]
    graphics = soup.find_all("includegraphics")
    documentClass = soup.documentclass
    if documentClass:
        classFile = list(filter(lambda x: type(x)==BraceGroup, documentClass.args))[0].contents[0]
        g.add_node(classFile, node="documentclass", tex=False, complete=True)
        g.add_edge(file, classFile)
    bib = soup.bibliography
    if bib:
        bib = bib.contents[0]
        g.add_node(bib, complete=True, tex=False, node='bib')
        g.add_edge(file, bib)
        

    for inputNode in inputs:
        g.add_node(inputNode, complete=False, tex=True, node="input")
        g.add_edge(file, inputNode)
    for includeNode in includes:
        g.add_node(includeNode, complete=False, tex=True, node="include")
        g.add_edge(file, includeNode)
    for graphicsNode in graphics:
        figurePath = list(filter(lambda x: type(x)==BraceGroup, graphicsNode.args))[0].contents[0]
        g.add_node(figurePath, figure=True, tex=False, node="includegraphics")
        g.add_edge(file, figurePath)
        
    # Recursive calls for sub-nodes
    for nodeName in inputs + includes:
        if not g.nodes[nodeName]['complete'] and g.nodes[nodeName]['tex']:
            parse_and_add_nodes(nodeName, g)

    # Set 'complete' to True after processing all sub-nodes
    g.nodes[file]['complete'] = True


def traverse_tex_tree(file):
    G = nx.DiGraph()
    G.add_node(file, complete=True, tex=True, node='root')
    parse_and_add_nodes(file, G)
    return G

