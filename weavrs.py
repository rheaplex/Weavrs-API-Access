# weavr.py - Access the Weavrs API.
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


import datetime
import oauth2 as oauth
import simplejson as json
import sys
import time
import urllib


# How long to delay between each call to the API for bulk operations
call_delay_seconds = 0


################################################################################
# Date and time utilities
################################################################################

one_day = datetime.timedelta(1)
one_week = datetime.timedelta(7)

def datetime_to_date(dt):
    """Floor the datetime to midnight at the start of the date"""
    return datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0)

def format_datetime(dt):
    """Format the datetime object to a string in Weavrs format"""
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


################################################################################
# Weavrs OAuth API Connection
################################################################################

api_weavr_configuration = 'http://www.weavrs.com/api/1/weavr/configuration/'
api_weavr_state = 'http://www.weavrs.com/api/1/weavr/state/'
api_weavr_post = 'http://www.weavrs.com/api/1/weavr/post'
api_weavr_run = 'http://www.weavrs.com/api/1/weavr/run'
api_weavr_location = 'http://www.weavrs.com/api/1/weavr/location'

class WeavrApiConnection(object):
    """A class to wrap up an OAuth connection to the Weavrs API"""
    
    def __init__(self, config, access_token, access_secret):
        """Create an OAuth client from the given token and secret"""
        self.consumer = oauth.Consumer(config.consumer_key,
                                       config.consumer_secret)
        self.token = oauth.Token(access_token, access_secret)
        self.client = oauth.Client(self.consumer, self.token)
    
    def request(self, url, args=None):
        """Request the url using the OAuth client, with the dict args
           urlencoded as the query string if provided"""
        if args:
            url = "%s?%s" % (url, urllib.urlencode(args))
        response, content = self.client.request(url)
        if response['status'] != '200':
            print response
            print content
            raise Exception("Status code %s != 200" % response['status'])
        return response, json.loads(content)


################################################################################
# Weavrs API access
################################################################################

def weavr_created_at(weavr, content = None):
    """Get the datetime.datetime the weavr was created at, fetching content
       from the WeavrApiConnection weavr if content is None"""
    if content == None:
        response, content = weavr.request(api_weavr_configuration)
    created_at_string = content['created_at']
    # Convert to a datetime
    created_at = datetime.datetime.strptime(created_at_string,
                                            "%Y-%m-%dT%H:%M:%SZ" )
    return created_at, content

def weavr_posts_between(weavr, start, end):
    """Get all the posts between start and end datetimes as parsed json"""
    args = {'after':format_datetime(start),
            'before':format_datetime(end),
            'per_page':1000}
    response, content = weavr.request(api_weavr_post, args)
    return content['posts']

def weavr_posts_all(weavr, configuration = None, max_days=100):
    """Get all the posts since the weavr was created"""
    created_at_datetime, configuration = weavr_created_at(weavr, configuration)
    posts = []
    now = datetime.datetime.now()
    day = datetime_to_date(created_at_datetime)
    day_finish = datetime_to_date(now)
    # Make sure we don't exceed the API limit
    max_days_delta = datetime.timedelta(max_days)
    if day_finish - day > max_days_delta:
        day = day_finish - max_days_delta
    print "Getting posts from %s to %s" % (day, day_finish)
    while day <= day_finish:
        print "Getting posts up to: %s" % day
        next_day = day + one_day
        days_posts = weavr_posts_between(weavr, day, next_day)
        print "(%s posts)" % len(days_posts)
        posts += days_posts
        day = next_day
        time.sleep(call_delay_seconds)
    return posts, now

def weavr_runs_between(weavr, start, end):
    """Get the weavr's runs (including posts) between the given dates"""
    args = {'after':format_datetime(start),
            'before':format_datetime(end),
            'posts':'true',
            'per_page':1000}
    response, content = weavr.request(api_weavr_run, args)
    return content['runs']

def weavr_runs_all(weavr, configuration = None, max_days=100):
    """Get all the runs since the weavr was created"""
    created_at_datetime, configuration = weavr_created_at(weavr, configuration)
    runs = []
    now = datetime.datetime.now()
    day = datetime_to_date(created_at_datetime)
    day_finish = datetime_to_date(now)
    # Make sure we don't exceed the API limit
    max_days_delta = datetime.timedelta(max_days)
    if day_finish - day > max_days_delta:
        day = day_finish - max_days_delta
    print "Getting runs from %s to %s" % (day, day_finish)
    while day <= day_finish:
        print "Getting runs up to: %s" % day
        next_day = day + one_day
        days_runs = weavr_runs_between(weavr, day, next_day)
        print "(%s runs)" % len(days_runs)
        runs += days_runs
        day = next_day
        time.sleep(call_delay_seconds)
    return runs, now

def weavr_locations_between(weavr, start, end):
    """Get the weavr's locations between the given dates"""
    args = {'after':format_datetime(start),
            'before':format_datetime(end),
            'per_page':1000}
    response, content = weavr.request(api_weavr_location, args)
    return content['locations']

def weavr_locations_all(weavr, configuration = None, max_days=100):
    """Get all the locations since the weavr was created"""
    created_at_datetime, configuration = weavr_created_at(weavr, configuration)
    locations = []
    now = datetime.datetime.now()
    day = datetime_to_date(created_at_datetime)
    day_finish = datetime_to_date(now)
    # Make sure we don't exceed the API limit
    max_days_delta = datetime.timedelta(max_days)
    if day_finish - day > max_days_delta:
        day = day_finish - max_days_delta
    print "Getting locations from %s to %s" % (day, day_finish)
    while day <= day_finish:
        print "Getting locations up to: %s" % day
        next_day = day + one_day
        days_locations = weavr_locations_between(weavr, day, next_day)
        print "(%s locations)" % len(days_locations)
        locations += days_locations
        day = next_day
        time.sleep(call_delay_seconds)
    return locations, now


################################################################################
# Post formatting
################################################################################

def format_post(stream, post):
    """Print post to stream in tab separated values format"""
    print >>stream, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
        (post['weavr'], post['run'], post['id'], post['post_id'],
         post['blog_post_datetime'], post['category'], post['source'],
         post['emotion'], post['keywords'])

def format_posts(stream, posts):
    """Print a header and each post to stream in tab separated values format"""
    print >>stream, "weavr\trun\tid\tpost_id\tblog_post_datetime\tcategory\tsource\temotion\tkeywords"
    for post in posts:
        format_post(stream, post)
