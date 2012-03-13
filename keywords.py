# keywords.py - Dump a weavr's posts' keywords to file.
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

import config
import sys
import urllib
import weavrs


################################################################################
# Edge formatting
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
    print >>stream, '<?xml version="1.0" encoding="UTF-8"?>'
    print >>stream, '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print >>stream, '<graph mode="static" defaultedgetype="undirected">'
    print >>stream, '<nodes>'
    for node in nodes:
        print >> stream, '<node id="%s" label = "%s"/>' % (node, node)
    print >>stream, '</nodes>'
    print >>stream, '<edges>'
    edge_id = 0
    for edge, weight in edges.iteritems():
        print >> stream, '<edge id="%i" source="%s" target="%s" weight="%f" />'\
            % (edge_id, edge[0], edge[1], weight)
        edge_id += 1
    print >>stream, '</edges>'
    print >>stream, '</graph>'
    print >>stream, '</gexf>'


################################################################################
# Tag graph
################################################################################

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: %s oauth-key oauth-secret" % sys.argv[0]
        sys.exit(1)
    access_token = sys.argv[1]
    access_secret = sys.argv[2]
    weavr = weavrs.WeavrApiConnection(config, access_token, access_secret)
    runs, now = weavrs.weavr_runs_all(weavr)
    nodes, edges = keyword_graph(runs)
    stream = open("%s-%s.gexf" % (urllib.quote(runs[0]['weavr']),
                                  now.strftime('%Y-%m-%d-%H-%M-%S')), 'w')
    keyword_graph_to_xml(stream, nodes, edges)
