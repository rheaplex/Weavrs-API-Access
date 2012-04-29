#!/usr/bin/python
# oauthorize.py - A script to get an OAuth key/secret for a Weavr
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


# Make sure you've set up the config.py file with your prosthetic's keys
# And make sure you copy the Weavr key/secret when you get them!!!


################################################################################
# Imports
################################################################################

import urlparse
import oauth2 as oauth

import os.path
import json
import urllib2
import urllib
import urlparse
import BaseHTTPServer
import webbrowser
import sys

import config


################################################################################
# Weavrs OAuth configuration
################################################################################

API_SERVER = 'www.weavrs.com'

OAUTH_SERVER_PATH = 'http://%s/oauth' % API_SERVER
REQUEST_TOKEN_URL = OAUTH_SERVER_PATH + '/request_token/'
ACCESS_TOKEN_URL = OAUTH_SERVER_PATH + '/access_token/'
AUTHORIZATION_URL = OAUTH_SERVER_PATH + '/authorize/'

CALLBACK_URL = 'http://127.0.0.1:8080/'


################################################################################
# Horrible, horrible globals
# Replace with something sane if this needs to be made more than a script
################################################################################

secret = None

serve = True


################################################################################
# Our local HTTP server, for completing OAuth authentication
################################################################################

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        global serve
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        request_token = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        
        # Get the access token
        oauth_token = request_token.get('oauth_token')
        # Make sure we're not being asked for a favicon or anything
        if not oauth_token:
            return
        token = oauth.Token(oauth_token, secret) #request_token['oauth_token_secret'])
        token.set_verifier(request_token['oauth_verifier'])
        client = oauth.Client(consumer, token)

        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
        access_token = dict(urlparse.parse_qsl(content))

        print "Access Token:"
        print "  oauth_token        = %s" % access_token['oauth_token']
        print "  oauth_token_secret = %s" % access_token['oauth_token_secret']
        serve = False

################################################################################
# Main Flow Of Execution
################################################################################

# Make an OAuth client using the Prosthetic key

consumer = oauth.Consumer(config.consumer_key, config.consumer_secret)
client = oauth.Client(consumer)

# Get request token

resp, content = client.request(REQUEST_TOKEN_URL + '?oauth_callback=' +
                               urllib2.quote(CALLBACK_URL), "GET")
if resp['status'] != '200':
    raise Exception("Invalid response %s." % resp['status'])
request_token = dict(urlparse.parse_qsl(content))
secret = request_token['oauth_token_secret']

# Reditect to OAuth server

auth_url = "%s?oauth_token=%s" %(AUTHORIZATION_URL,
 request_token['oauth_token'])
# Try to play nice with the web browser in Gnome 3.2
try:
    web_client = webbrowser.get('firefox')
    web_client.open_new_tab(auth_url) 
except:
    webbrowser.open_new_tab(auth_url) 

# Run a local web server to receive the authentication results from the browser

httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), RequestHandler)
while serve:
    httpd.handle_request()
