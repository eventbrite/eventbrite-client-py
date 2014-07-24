import unittest

class TestTheVeryBasics(unittest.TestCase):
    '''This test verifies that the modules can be imported.

    This may seem like a trivial test, but at the moment, we are
    mostly interested in having a test suite to determine if this
    package can be used within Python 3.x. Given that, exercising
    our imports is a lot better than nothing.


    For good measure, we actually instantiate an EventbriteClient
    object, too.'''
    def test_imports(self):
        # OK! Let's import things.
        import eventbrite
        # This implicitly tests eventbrite.json_lib as
        # well. Excellent.
        #
        # Now, let us assert that it is true. This is really just to
        # satisfy pyflakes, which is appalled that we would import
        # something and not use it.
        self.assertTrue(eventbrite)  # assert on it, to satisfy
    

    def test_create_client(self):
        import eventbrite
        eb_client = eventbrite.EventbriteClient(
            {'access_code': 'A non-existent OAuth2 Access Token'})
        # Similarly, assert that eb_client is a real thing, to satisfy
        # linters that look for unused variables.
        self.assertTrue(eb_client)
