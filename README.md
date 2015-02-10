#eventbrite-client.py#

## This project has been deprecated

This project has been deprecate in favor of our newer version. Please begin using the [eventbrite-sdk-python](https://github.com/eventbrite/eventbrite-sdk-python) instead.

##Description##
A simple python-based http client for the Eventbrite API

For the latest information on this project, take a look at:

* [This project's source code repo](http://github.com/eventbrite/eventbrite-client-py/)
* [The Eventbrite API documentation](http://developer.eventbrite.com/doc/)

##Usage Examples##

###Installation###

NOTE:  This package requires a JSON library - by default we check for "simplejson" or use the built-in "json" library provided in python 2.6+

####Installation using easy_install####

    easy_install eventbrite

####Installation using pip####

    pip install eventbrite

###Loading the Eventbrite API Client library code###

    import eventbrite

###Initializing the client###
Your API / Application key is required to initialize the client - http://eventbrite.com/api/key

Set your user_key if you want to access private data - http://eventbrite.com/userkeyapi

    eb_auth_tokens = {'app_key':  'YOUR_APP_KEY',
                      'user_key': 'YOUR_USER_KEY'}
    eb_client = eventbrite.EventbriteClient(eb_auth_tokens)

### Initializing the client with an OAuth2.0 access_token ###

    eb_client = eventbrite.EventbriteClient({'access_code': 'YOUR_OAUTH2_ACCESS_TOKEN'})

###Calling API methods###
See [Eventbrite's API method documentation](http://developer.eventbrite.com/doc/) for more information about the list of available client methods.

Here is an example using the API's [user_list_events](http://developer.eventbrite.com/doc/users/user_list_events/) method:

    response = eb_client.user_list_events()

The [event_get](http://developer.eventbrite.com/doc/events/event_get/) API call should look like this:

    response = eb_client.event_get({'id':1848891083})

### Widgets ###
Rendering an event in html as a [ticketWidget](http://www.eventbrite.com/t/how-to-use-ticket-widget) is easy:

    response = eb_client.event_get({'id':1848891083})
    widget_html = eventbrite.EventbriteWidgets.ticketWidget(response['event'])

##Resources##
* API Documentation - <http://developer.eventbrite.com/doc/>
* API QuickStart Guide - <http://developer.eventbrite.com/doc/getting-started/>
* Eventbrite Open Source - <http://eventbrite.github.com/>
* Eventbrite App Showcase - <http://eventbrite.appstores.com/>
* 0.40 source - <http://github.com/eventbrite/eventbrite-client-py/>
* 0.3x source - <http://github.com/eventbrite/eventbrite-client-py/>
* 0.2x source - <http://github.com/mtai/eventbrite/>
