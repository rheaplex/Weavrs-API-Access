# gexf.py - Transform a weavr's posts' keywords/emotions into a gexf file.
# Copyright (C) 2012  Rob Myers <rob@robmyers.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


################################################################################
# Imports
################################################################################


################################################################################
# Utilities
################################################################################

# http://mail.python.org/pipermail/python-list/2004-September/282520.html

def all_pairs(seq):
    l = len(seq)
    for i in range(l):
        for j in range(i+1, l):
            yield seq[i], seq[j]


################################################################################
# Emotions
################################################################################

# Keywords as nodes
# Emotions as edges
# Uses number of times keywords occur with the same emotion as edge weight

def emotion_edge_graph(runs):
    """Return a list of node names, and a dict of edge pairs and weights"""
    node_names = set()
    edges = dict()
    for run in runs:
        emotion = (run['emotion'],)
        for post in run['posts']:
            keywords = set(post['keywords'].split())
            node_names.update(keywords)
            for keyword in keywords:
                for other_keyword in keywords:
                    if other_keyword != keyword:
                        # Make sure a/b and b/a are counted the same
                        # (a,b,label)
                        edge = tuple(sorted([keyword, other_keyword])) + emotion
                        edges[edge] = edges.get(edge, 0) + 1
    return list(node_names), edges

def emotion_edge_graph_to_xml(stream, nodes, edges):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print >>stream, u'<graph mode="static" defaultedgetype="undirected">'
    print >>stream, u'<nodes>'
    for node in nodes:
        print >> stream, u'<node id="%s" label = "%s"/>' % (node, node)
    print >>stream, u'</nodes>'
    print >>stream, u'<edges>'
    edge_id = 0
    for edge, weight in edges.iteritems():
        print >>stream, u'<edge id="%i" source="%s" target="%s" weight="%f" label="%s" />'\
            % (edge_id, edge[0], edge[1], weight, edge[2])
        edge_id += 1
    print >>stream, u'</edges>'
    print >>stream, u'</graph>'
    print >>stream, u'</gexf>'

# Emotions as nodes
# Keywords as edges
# No weight, just show if emotions ever have the same keywords
# If this isn't any good we could use how iften they have the same keywords
# Although this might not be very useful

def emotion_node_graph(runs):
    """Return a list of node names, and a dict of edge pairs and weights"""
    node_names = set()
    edges = dict()
    for run in runs:
        emotion = [run['emotion']]
        print emotion
        node_names.update(emotion)
        for post in run['posts']:
            keywords = set(post['keywords'].split())
            print keywords
            for keyword in keywords:
                edges[keyword] = edges.get(keyword, set()).union(emotion)
    return list(node_names), edges

def emotion_node_graph_to_xml(stream, nodes, edges):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print >>stream, u'<graph mode="static" defaultedgetype="undirected">'
    print >>stream, u'<nodes>'
    for node in nodes:
        print >> stream, u'<node id="%s" label = "%s"/>' % (node, node)
    print >>stream, u'</nodes>'
    print >>stream, u'<edges>'
    edge_id = 0
    for keyword, emotions in edges.iteritems():
        for pair in all_pairs(list(emotions)):
            print >>stream, u'<edge id="%i" source="%s" target="%s" label="%s" />' % (edge_id, pair[0], pair[1], keyword)
        edge_id += 1
    print >>stream, u'</edges>'
    print >>stream, u'</graph>'
    print >>stream, u'</gexf>'

################################################################################
# Keywords
################################################################################

def keyword_graph(runs):
    """Return a list of node names, and a dict of edge pairs and weights"""
    node_names = set()
    edges = dict()
    for run in runs:
        for post in run['posts']:
            keywords = set(post['keywords'].split())
            node_names.update(keywords)
            for keyword in keywords:
                for other_keyword in keywords:
                    if other_keyword != keyword:
                        # Make sure a/b and b/a are counted the same
                        edge = tuple(sorted([keyword, other_keyword]))
                        edges[edge] = edges.get(edge, 0) + 1
    return list(node_names), edges

def keyword_graph_to_xml(stream, nodes, edges):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print >>stream, u'<graph mode="static" defaultedgetype="undirected">'
    print >>stream, u'<nodes>'
    for node in nodes:
        print >> stream, u'<node id="%s" label = "%s"/>' % (node, node)
    print >>stream, u'</nodes>'
    print >>stream, u'<edges>'
    edge_id = 0
    for edge, weight in edges.iteritems():
        print >>stream, u'<edge id="%i" source="%s" target="%s" weight="%f" />'\
            % (edge_id, edge[0], edge[1], weight)
        edge_id += 1
    print >>stream, u'</edges>'
    print >>stream, u'</graph>'
    print >>stream, u'</gexf>'


################################################################################
# Locations
################################################################################

def locations_to_xml(stream, locations):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8" xmlns:viz="http://www.gexf.net/1.1draft/viz"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print >>stream, u'<graph mode="static" defaultedgetype="undirected">'
    print >>stream, u'<nodes>'
    for location in locations:
        name = location['title']
        if name == '':
            name = location['street_address']
        print >>stream, u'<node id="%s" label="%s">' % (location['id'], name)
        print >>stream, u'<viz:position x="%s" y="%s" z="0.0"/>' % \
            (location['lon'], location['lat'])
        print >>stream, u'</node>'
    print >>stream, u'</nodes>'
    print >>stream, u'</graph>'
    print >>stream, u'</gexf>'
