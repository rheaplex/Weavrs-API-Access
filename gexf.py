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

import cgi
import time

import weavrs

################################################################################
# Utilities
################################################################################

# http://mail.python.org/pipermail/python-list/2004-September/282520.html

def all_pairs(seq):
    l = len(seq)
    for i in range(l):
        for j in range(i+1, l):
            yield seq[i], seq[j]

def dtepoch(datetime):
    """Convert the datetime to seconds since epoch"""
    return time.mktime(datetime.timetuple())

def dtxsd(dt):
    """Convert the datetime to an xsd:datetime string"""
    return dt.strftime("%Y-%m-%dT%H:%M:%s")


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
            keywords = list(set(post['keywords'].split()))
            node_names.update(keywords)
            for pair in all_pairs(keywords):
                edge = tuple(sorted(pair)) + emotion
                edges[edge] = edges.get(edge, 0) + 1
    return list(node_names), edges

def emotion_edge_graph_to_xml(stream, nodes, edges):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print >>stream, u'<graph mode="static" defaultedgetype="undirected">'
    print >>stream, u'<nodes>'
    for node in nodes:
        print >> stream, u'<node id="%s" label="%s" />' % (node, node)
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
        node_names.update(emotion)
        for post in run['posts']:
            keywords = set(post['keywords'].split())
            for keyword in keywords:
                edges[keyword] = edges.get(keyword, set()).union(emotion)
    return list(node_names), edges

def emotion_node_graph_to_xml(stream, nodes, edges):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print >>stream, u'<graph mode="static" defaultedgetype="undirected">'
    print >>stream, u'<nodes>'
    for node in nodes:
        print >> stream, u'<node id="%s" label="%s" />' % (node, node)
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
            keywords = list(set(post['keywords'].split()))
            node_names.update(keywords)
            for pair in all_pairs(keywords):
                # Make sure a/b and b/a are counted the same
                edge = tuple(sorted(pair))
                edges[edge] = edges.get(edge, 0) + 1
    return list(node_names), edges

def keyword_graph_to_xml(stream, nodes, edges):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print >>stream, u'<graph mode="static" defaultedgetype="undirected">'
    print >>stream, u'<nodes>'
    for node in nodes:
        print >> stream, u'<node id="%s" label="%s" />' % (node, node)
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
# Keywords over time
################################################################################

def run_keyword_edges(run):
    """Return a dict of (a,b):n representing the strength of the edges between
       keywords for the run"""
    edges = dict()
    for post in run['posts']:
            keywords = list(set(post['keywords'].split()))
            for pair in all_pairs(keywords):
                # Make sure a/b and b/a are counted the same
                edge = tuple(sorted(pair))
                edges[edge] = edges.get(edge, 0) + 1
    return edges

def runs_keywords(runs):
    """Get all the keywords for every post of every run"""
    keywords = set()
    for run in runs:
        for post in run['posts']:
            post_keywords = set(post['keywords'].split())
            keywords.update(post_keywords)
    return list(keywords)

class DynamicEdge(object):
    """An Edge with a start and end time"""
    
    def __init__(self, node_from, node_to, time_from, time_to, weight):
        self.node_from = node_from
        self.node_to = node_to
        self.time_from = time_from
        self.time_to = time_to
        self.weight = weight

def keyword_edge_durations(runs):
    """Return a list of dynamic edges for the runs (excluding last run)"""
    runs_in_time_order = list(reversed(runs))
    edges = list()
    current_time = weavrs.parse_datetime(runs_in_time_order[0]['datetime'])
    current_edges = run_keyword_edges(runs_in_time_order[0])
    for run in runs_in_time_order[1:]:
        next_time = weavrs.parse_datetime(run['datetime'])
        for edge_pair, edge_weight in current_edges.iteritems():
            edges.append(DynamicEdge(edge_pair[0], edge_pair[1], current_time,
                                     next_time, edge_weight))
        current_edges = run_keyword_edges(run)
        current_time = next_time
    return edges

def keyword_durations_to_xml(stream, nodes, edges):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    # xsd:dateTime for timeformat
    print >>stream, u'<graph mode="dynamic" defaultedgetype="undirected" timeformat="datetime">'
    print >>stream, u'<nodes>'
    for node in nodes:
        print >> stream, u'<node id="%s" label="%s" />' % (node, node)
    print >>stream, u'</nodes>'
    print >>stream, u'<edges>'
    edge_id = 0
    for edge in edges:
        print >>stream, u'<edge id="%i" source="%s" target="%s" start="%s" end="%s" weight="%f" />'\
            % (edge_id, edge.node_from, edge.node_to, dtxsd(edge.time_from),
               dtxsd(edge.time_to), edge.weight)
        edge_id += 1
    print >>stream, u'</edges>'
    print >>stream, u'</graph>'
    print >>stream, u'</gexf>'


################################################################################
# Locations
################################################################################

def locations_to_xml(stream, locations):
    print >>stream, u'<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, u'<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2" xmlns:viz="http://www.gexf.net/1.1draft/viz">'
    print >>stream, u'<graph mode="static" defaultedgetype="undirected">'
    print >>stream, u'<attributes class="node" mode="static">'
    print >>stream, u'<attribute id="latitude" title="latitude" type="double"/>'
    print >>stream, u'<attribute id="longitude" title="longitude" type="double"/>'
    print >>stream, u'</attributes>'
    print >>stream, u'<nodes>'
    for location in locations:
        name = location['title']
        if name == '':
            name = location['street_address']
        print >>stream, u'<node id="%s" label="%s">' % (location['id'],
                                                        cgi.escape(name))
        print >>stream, u'<attvalue for="latitude" value="%s" />' % \
            location['lat']
        print >>stream, u'<attvalue for="longitude" value="%s" />' % \
            location['lon']
        #print >>stream, u'<viz:position x="%s" y="%s" z="0.0" />' % \
        #    (location['lon'], location['lat'])
        print >>stream, u'</node>'
    print >>stream, u'</nodes>'
    print >>stream, u'</graph>'
    print >>stream, u'</gexf>'
