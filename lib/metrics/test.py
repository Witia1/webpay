# -*- coding: utf8 -*-
import json
import urlparse

import mock
from nose.tools import eq_

from django.conf import settings
from lib.metrics import metrics, send, send_request

import test_utils


@mock.patch('lib.metrics.urllib2.urlopen')
@mock.patch.object(settings, 'METRICS_SERVER', 'http://localhost')
class TestMetrics(test_utils.TestCase):

    def test_called(self, urlopen):
        send('install', {})
        eq_(urlopen.call_args[0][0].data, '{}')

    def test_called_data(self, urlopen):
        data = {'foo': 'bar'}
        send('install', data)
        eq_(urlopen.call_args[0][0].data, json.dumps(data))

    def test_called_url(self, urlopen):
        send('install', {})
        url = urlopen.call_args[0][0].get_full_url()
        eq_(urlparse.urlparse(url)[:2], ('http', 'localhost'))

    def test_some_unicode(self, urlopen):
        send('install', {'name': u'Вагиф Сәмәдоғлу'})

    def test_send_request(self, urlopen):
        request = mock.Mock()
        request.META = {'HTTP_USER_AGENT': 'py'}
        send_request('install', request, {})
        eq_(urlopen.call_args[0][0].data, '{"user-agent": "py"}')

    def get_response(self, code):
        response = mock.Mock()
        response.status_code = code
        return response

    def test_error(self, urlopen):
        urlopen.return_value = self.get_response(403)
        eq_(metrics('x', 'install', {}), 403)

    def test_good(self, urlopen):
        urlopen.return_value = self.get_response(200)
        eq_(metrics('x', 'install', {}), 200)

    def test_other(self, urlopen):
        urlopen.return_value = self.get_response(206)
        eq_(metrics('x', 'install', {}), 206)

    def test_uid(self, urlopen):
        metrics('x', 'install', {})
        assert urlopen.call_args[0][0].get_full_url().endswith('x')