# dump.py - Dump a weavr's posts' keywords to file.
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

import codecs
import config
import gexf
import sys
import urllib
import weavrs


################################################################################
# Tag graph
################################################################################

def dump_emotion_edges(runs, now):
    nodes, edges = gexf.emotion_edge_graph(runs)
    stream = codecs.open("%s-emotion-edges-%s.gexf" %
                         (urllib.quote(runs[0]['weavr']),
                          now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.emotion_edge_graph_to_xml(stream, nodes, edges)

def dump_emotion_nodes(runs, now):
    nodes, edges = gexf.emotion_node_graph(runs)
    stream = codecs.open("%s-emotion-nodes-%s.gexf" %
                         (urllib.quote(runs[0]['weavr']),
                          now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.emotion_node_graph_to_xml(stream, nodes, edges)

def dump_keywords(runs, now):
    nodes, edges = gexf.keyword_graph(runs)
    stream = codecs.open("%s-keywords-%s.gexf" %
                  (urllib.quote(runs[0]['weavr']),
                   now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.keyword_graph_to_xml(stream, nodes, edges)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: %s oauth-key oauth-secret" % sys.argv[0]
        sys.exit(1)
    access_token = sys.argv[1]
    access_secret = sys.argv[2]
    weavr = weavrs.WeavrApiConnection(config, access_token, access_secret)
    runs, now = weavrs.weavr_runs_all(weavr)
    dump_emotion_edges(runs, now)
    dump_emotion_nodes(runs, now)
    dump_keywords(runs, now)
