import networkx as nx

from TexSoup import TexSoup
from TexSoup.data import BraceGroup

def parse_and_add_nodes(file, g, nodeFilters):
    g.nodes[file]['complete'] = True
    filterFunc = lambda node: list(filter(lambda x: type(x)==BraceGroup, node.args))[0].contents[0]
    with open(file, 'r') as f:
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
            print(f"Working in {nodeName}")
            parse_and_add_nodes(nodeName, g, nodeFilters)

def traverse_tex_tree(file, nodeFilters):
    G = nx.DiGraph()
    G.add_node(file, complete=True, tex=True, nodeType='root')
    parse_and_add_nodes(file, G, nodeFilters)
    return G

            

