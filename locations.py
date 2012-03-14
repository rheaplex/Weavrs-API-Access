# location.py - Dump a weavr's locations to file.
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
# Locations
################################################################################

def dump_locations(locations, now):
    stream = codecs.open("%s-location-nodes-%s.gexf" %
                         (urllib.quote(locations[0]['weavr']),
                          now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.emotion_edge_graph_to_xml(stream, nodes, edges)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: %s oauth-key oauth-secret" % sys.argv[0]
        sys.exit(1)
    access_token = sys.argv[1]
    access_secret = sys.argv[2]
    weavr = weavrs.WeavrApiConnection(config, access_token, access_secret)
    locations, now = weavrs.weavr_locations_all(weavr, None, 1)
    dump_locations(locations, now)
