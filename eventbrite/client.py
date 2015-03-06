"""Simple Eventbrite client for the HTTP-based API
"""
import datetime
import time
try:
    import http.client as httplib
except ImportError:
    import httplib
import logging
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import sys
from eventbrite import json_lib

# Input transformations
def _datetime_to_string(incoming_datetime):
    return time.strftime("%Y-%m-%d %H:%M:%S", incoming_datetime )

def _string_to_datetime(incoming_string):
    return time.strptime(incoming_string, "%Y-%m-%d %H:%M:%S")

def _boolean_one_or_zero(is_true):
    return (is_true and '1') or '0'

def _boolean_true_or_false(is_true):
    return (is_true and 'true') or 'false'

def _comma_separated_list(input_list):
    return ",".join(input_list)

class EventbriteClient(object):
    """Client for Eventbrite's HTTP-based API"""
    eb_date_string = "%Y-%m-%d %H:%M:%S"
    eventbrite_api_endpoint = 'www.eventbrite.com'
    eventbrite_request_template = 'https://%(host)s/json/%(method)s?%(arguments)s'
    # these method aliases are for backwords compatibility with code
    # that was written before version 0.30 of this client was released
    #  !!WARNING: These calls are being depricated!!
    method_aliases = { 'copy_event': 'event_copy'
                     , 'get_event': 'event_get'
                     , 'get_user': 'user_get'
                     , 'list_event_attendees': 'event_list_attendees'
                     , 'list_event_discounts': 'event_list_discounts'
                     , 'list_organizer_events': 'event_list_organizer'
                     , 'list_user_events': 'user_list_events'
                     , 'list_user_organizers': 'user_list_organizers'
                     , 'list_user_tickets': 'user_list_tickets'
                     , 'list_user_venues': 'user_list_venues'
                     , 'new_discount': 'discount_new'
                     , 'new_event': 'event_new'
                     , 'new_organizer': 'organizer_new'
                     , 'new_ticket': 'ticket_new'
                     , 'new_user': 'user_new'
                     , 'new_venue': 'venue_new'
                     , 'search_events': 'event_search'
                     , 'update_discount': 'discount_update'
                     , 'update_event': 'event_update'
                     , 'update_organizer': 'organizer_update'
                     , 'update_payment': 'payment_update'
                     , 'update_ticket': 'ticket_update'
                     , 'update_user': 'user_update'
                     , 'update_venue': 'venue_update' }

    def __init__(self, tokens=None, user_key=None, password=None):
        """Initialize the client with the given app key and the user key"""
        logger = logging.getLogger(__name__)
        self._https_connection = httplib.HTTPSConnection(self.eventbrite_api_endpoint)
        self._auth_tokens = {}
        # set initialization tokens by name
        if type(tokens) == type(dict()):
            self._auth_tokens.update(tokens)
        # set initialization tokens by order
        else:
            self._auth_tokens['app_key'] = tokens
            # if we get three initialization tokens ( if "password" is set )
            #    use username+password combo for auth
            if password:
                self._auth_tokens['user'] = user_key
                self._auth_tokens['password'] = password
            # else use user_key for authentication
            else:
                self._auth_tokens['user_key'] = user_key

    # dynamic methods handler - call API methods on the local client object
    def __getattr__(self, method):
        # enable backwords compatibility with pre-0.30 API client code
        if method in self.method_aliases:
            method = self.method_aliases[method]
        def _call(*args, **kwargs):
            return self._request(method, args)
        return _call

    def _request(self, method='', params=dict()):
        """Execute an API call on Eventbrite using their HTTP-based API

        method - string  - the API method to call - see https://www.eventbrite.com/doc
        params - dict    - Arguments to pass along as method request parameters

        Returns: A dictionary with a return structure defined at http://developer.eventbrite.com/doc/
        """
        #unpack our params
        if type(params) == type(()) and len(params) > 0: 
            method_arguments = dict(params[0])
        else:
            method_arguments = {}

        # Add authentication tokens
        if 'access_token' not in self._auth_tokens:
            method_arguments.update(self._auth_tokens)

        # urlencode API method parameters
        encoded_params = urlencode(method_arguments)
        
        # construct our request url
        request_url = self.eventbrite_request_template % dict(host=self.eventbrite_api_endpoint, method=method, arguments=encoded_params)
        #self.logger.debug("REQ - %s", request_url)

        # Send a GET request to Eventbrite
        # if using OAuth2.0 for authentication, set additional headers
        if 'access_token' in self._auth_tokens:
            self._https_connection.request('GET', request_url, None, {'Authorization': "Bearer " + self._auth_tokens['access_token']})
        else:
            self._https_connection.request('GET', request_url)

        # extending the timeout window per request (not system-wide) 
        # requires python 2.5 or better:
        if int(sys.version[0]) >= 2 and int(sys.version[2]) >= 5:
            self._https_connection.sock.settimeout(200)

        # Read the JSON response 
        response_data = self._https_connection.getresponse().read()
        #self.logger.debug("RES - %s", response_data)

        # decode our response
        response = json_lib.loads(response_data.decode('utf-8'))
        if 'error' in response and 'error_message' in response['error'] :
            raise EnvironmentError( response['error']['error_message'] )
        return response

    def oauth_handshake( self, tokens ):
        """Exchange an intermediary access_code for an OAuth2.0 access_token

        tokens - dict - 'app_key' = API_key, 'client_secret' = client secret, 'access_code' = access_code

        Returns: an Oauth2.0 access_token, see http://developer.eventbrite.com/doc/authentication/oauth2/
        """
        params = {'grant_type'   : 'authorization_code', 
                  'client_id'    : tokens['app_key'], 
                  'client_secret': tokens['client_secret'], 
                  'code'         : tokens['access_code'] }

        request_url = 'https://%(host)s/oauth/token' % dict(host=self.eventbrite_api_endpoint)
        post_body = urlencode(params)
        headers = {'Content-type': "application/x-www-form-urlencoded"}
        
        self._https_connection.request('POST', request_url, post_body, headers)
        response_data = self._https_connection.getresponse().read()
        response = json_lib.loads(response_data.decode('utf-8'))

        if 'error' in response or 'access_token' not in response :
            raise EnvironmentError( response['error_description'] )

        return response

class EventbriteWidgets:
    @staticmethod
    def eventList( evnts, callback=None, options=None ):
        # a loop for iterating over a collection of events, applying a callback to each element
        if not callback:
            callback = EventbriteWidgets.eventListRow
        #create our default response envelope
        html = ['<div class="eb_event_list">']
        #unpack our events list based on the default response format provided by the event_search, user_list_events, or organizer_list_events API methods
        if( type(evnts) == type(dict()) and 'events' in evnts \
            and type([]) == type(evnts['events']) and callable(callback)):
            if options:
                for evnt in evnts['events']:
                    html.append(callback( evnt['event'], options))
            else:
                for evnt in evnts['events']:
                    html.append(callback( evnt['event'] ))
        else:
            html.append('No events were found at this time.')
        html.append('</div>')
        return '\n'.join(html)

    @staticmethod
    def eventListRow( evnt ):
        #decode the timestamp for start_date
        start_date = _string_to_datetime( evnt['start_date'] )
        #find venue name, default to "online"
        if( 'venue' in evnt and 'name' in evnt['venue'] ):
            venue_name = evnt['venue']['name']
        else:
            venue_name = 'online'
        #generate and return the HTML for this list item
        html = u'<div class="eb_event_list_item" id="evnt_div_%(event_id)d"><span class="eb_event_list_date">%(start_date_str)s</span><span class="eb_event_list_time">%(start_time_str)s</span><a class="eb_event_list_title" href="%(event_url)s">%(event_title)s</a><span class="eb_event_list_location">%(venue_label)s</span></div>' % \
            {"event_id": evnt['id']
            ,"start_date_str": time.strftime('%a, %B %e', start_date)
            ,"event_title": evnt['title']
            ,"start_time_str": time.strftime('%l:%M %P', start_date)
            ,"event_url": evnt['url']
            ,"venue_label": venue_name}
        return html.encode('utf-8')

    @staticmethod
    def ticketWidget(evnt):
        html = u'<div style="width:100%%; text-align:left;"><iframe src="http://www.eventbrite.com/tickets-external?eid=%(event_id)d&ref=etckt" frameborder="0" height="192" width="100%%" vspace="0" hspace="0" marginheight="5" marginwidth="5" scrolling="auto" allowtransparency="true"></iframe><div style="font-family:Helvetica, Arial; font-size:10px; padding:5px 0 5px; margin:2px; width:100%%; text-align:left;"><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/r/etckt">Online Ticketing</a><span style="color:#ddd;"> for </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/event/%(event_id)d?ref=etckt">%(event_title)s</a><span style="color:#ddd;"> powered by </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com?ref=etckt">Eventbrite</a></div></div>' % \
            {'event_id': evnt['id'], 'event_title': evnt['title']}
        return html.encode('utf-8')

    @staticmethod
    def registrationWidget(evnt):
        html = u'<div style="width:100%%; text-align:left;"><iframe src="http://www.eventbrite.com/event/%(event_id)d?ref=eweb" frameborder="0" height="1000" width="100%%" vspace="0" hspace="0" marginheight="5" marginwidth="5" scrolling="auto" allowtransparency="true"></iframe><div style="font-family:Helvetica, Arial; font-size:10px; padding:5px 0 5px; margin:2px; width:100%%; text-align:left;"><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/r/eweb">Online Ticketing</a><span style="color:#ddd;"> for </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/event/%(event_id)d?ref=eweb">%(event_title)s</a><span style="color:#ddd;"> powered by </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com?ref=eweb">Eventbrite</a></div></div>' % \
            {'event_id': evnt['id'], 'event_title': evnt['title']}
        return html.encode('utf-8')

    @staticmethod
    def calendarWidget(evnt):
        html = u'<div style="width:195px; text-align:center;"><iframe src="http://www.eventbrite.com/calendar-widget?eid=%(event_id)d" frameborder="0" height="382" width="195" marginheight="0" marginwidth="0" scrolling="no" allowtransparency="true"></iframe><div style="font-family:Helvetica, Arial; font-size:10px; padding:5px 0 5px; margin:2px; width:195px; text-align:center;"><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/r/ecal">Online event registration</a><span style="color:#ddd;"> powered by </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com?ref=ecal">Eventbrite</a></div></div>' % \
            {'event_id': evnt['id']}
        return html.encode('utf-8')

    @staticmethod
    def countdownWidget(evnt):
        html = u'<div style="width:195px; text-align:center;"><iframe src="http://www.eventbrite.com/countdown-widget?eid=%(event_id)d" frameborder="0" height="479" width="195" marginheight="0" marginwidth="0" scrolling="no" allowtransparency="true"></iframe><div style="font-family:Helvetica, Arial; font-size:10px; padding:5px 0 5px; margin:2px; width:195px; text-align:center;"><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/r/ecount">Online event registration</a><span style="color:#ddd;"> for </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/event/%(event_id)d?ref=ecount">%(event_title)s</a></div></div>' % \
            {'event_id': evnt['id'], 'event_title': evnt['title']}
        return html.encode('utf-8')

    @staticmethod
    def buttonWidget(evnt):
        html = u'<a href="http://www.eventbrite.com/event/%(event_id)d?ref=ebtn" target="_blank"><img border="0" src="http://www.eventbrite.com/custombutton?eid=%(event_id)d" alt="Register for %(event_title)s on Eventbrite" /></a>' % \
            {'event_id': evnt['id'], 'event_title': evnt['title']}
        return html.encode('utf-8')

    @staticmethod
    def linkWidget(evnt, text=False, color='#000000'):
        text = text if text else evnt['title'] 
        html = u'<a href="http://www.eventbrite.com/event/%(event_id)d?ref=elink" target="_blank" style="color:%(link_color)s;">%(link_text)s</a>' % \
            {'event_id': evnt['id']
            ,'link_color': color
            ,'link_text': text}
        return html.encode('utf-8')
