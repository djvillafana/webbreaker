from unittest import TestCase
import mock
import webinspectapi
#from webinspectapi.webinspectapi import WebInspectApi as webinspectapi

from webbreaker.webinspectjitscheduler import WebInspectJitScheduler as WJS


class TestWebInspectJitScheduler(TestCase):
    # convert_size_to_count should take a list of
    # size:count, and given a specific size, return
    # the associated count. If no match, return none
    def test___convert_size_to_count_large__(self):
        endpoints = []
        size_list = [['medium', 1], ['large', 2]]
        size_needed = 'large'
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)

        converted_value = scheduler.__convert_size_to_count__()
        self.assertEqual(converted_value, 2, "Failed to convert size large to scan count 2.")

    def test___convert_size_to_count_medium__(self):
        endpoints = []
        size_list = [['medium', 1], ['large', 2]]
        size_needed = 'medium'
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)

        converted_value = scheduler.__convert_size_to_count__()
        self.assertEqual(converted_value, 1, "Failed to convert size medium to scan count 1.")

    def test___convert_size_to_count_none__(self):
        endpoints = []
        size_list = [['medium', 1]]
        size_needed = 'large'
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)

        converted_value = scheduler.__convert_size_to_count__()
        self.assertIsNone(converted_value, "Should have found NONE for scan count.")

    # is_endpoint_available should call a specific endpoint and get back
    # a list of all scans. If the count of scans with a status of
    # running is less than the provided max size, return true. Else false.
    @mock.patch.object(webinspectapi, "list_scans")
    def test___is_endpoint_available_true__(self, mock_list_scans):
        endpoints = []
        size_list = [['medium', 1], ['large', 2]]
        size_needed = 'large'
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)

        mock_list_scans.return_value = MockWebInspectResponse(success=True,
                                                              data=[{'Status': 'Running'}, {'Status': 'Complete'}])
        available = scheduler.__is_endpoint_available__(endpoint=['http://1a.com', 1], max_concurrent_scans=2)

        self.assertTrue(available, msg='endpoint should have been available - only 1 scan running and max is 2')

    @mock.patch.object(webinspectapi, "list_scans")
    def test___is_endpoint_available_false__(self, mock_list_scans):
        endpoints = []
        size_list = [['medium', 1], ['large', 2]]
        size_needed = 'large'
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)

        mock_list_scans.return_value = MockWebInspectResponse(success=True,
                                                              data=[{'Status': 'Running'}, {'Status': 'Running'}])
        available = scheduler.__is_endpoint_available__(endpoint=['http://1a.com', 1], max_concurrent_scans=2)

        self.assertFalse(available, msg='endpoint should not have been available - 2 scans running and max is 2')

    @mock.patch.object(webinspectapi, "list_scans")
    def test___is_endpoint_available_unknown__(self, mock_list_scans):
        endpoints = []
        size_list = [['medium', 1], ['large', 2]]
        size_needed = 'large'
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)

        mock_list_scans.return_value = MockWebInspectResponse(success=False,
                                                              data=[{'Status': 'Running'}, {'Status': 'Running'}])
        available = scheduler.__is_endpoint_available__(endpoint=['http://1a.com', 1], max_concurrent_scans=2)

        self.assertFalse(available, msg='endpoint should not have been available - api call was not successful')

    # get_possible_endpoints should return a list of which of the endpoints provided
    # during initialization are matches to the size needed.
    # if none are matches, an empty list should be returned.
    def test___get_possible_endpoints_medium__(self):
        endpoints = [['http://1a.com', 1], ['http://2a.com', 2], ['http://2b.com', 2], ['http://1b.com', 1]]
        size_list = [['medium', 1], ['large', 2]]
        size_needed = 'medium'
        expected_result = [['http://1a.com', 1], ['http://1b.com', 1]]
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)
        result = scheduler.__get_possible_endpoints__(1)

        self.assertEqual(result, expected_result, 'should have found 2 medium endpoints')

    def test___get_possible_endpoints_large__(self):
        endpoints = [['http://1a.com', 1], ['http://2a.com', 2], ['http://2b.com', 2], ['http://1b.com', 1]]
        size_list = [['medium', 1], ['large', 2]]
        size_needed = 'large'
        expected_result = [['http://2a.com', 2], ['http://2b.com', 2]]
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)
        result = scheduler.__get_possible_endpoints__(2)

        self.assertEqual(result, expected_result, 'should have found 2 large endpoints')

    def test___get_possible_endpoints_3__(self):
        endpoints = [['http://1a.com', 1], ['http://2a.com', 2], ['http://2b.com', 2], ['http://1b.com', 1]]
        size_list = [['medium', 1], ['large', 2]]
        size_needed = 'not-a-real-size'
        scheduler = WJS(endpoints=endpoints, size_list=size_list, size_needed=size_needed)

        result = scheduler.__get_possible_endpoints__(3)
        self.assertEqual(result, [], 'should have found 0 possible endpoints')


class MockWebInspectResponse(object):
    def __init__(self, success, message='OK', response_code=-1, data=None):
        self.message = message
        self.success = success
        self.response_code = response_code
        self.data = data

