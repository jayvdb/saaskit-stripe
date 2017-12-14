# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.test import TestCase
from django.utils import six

from ..models import Customer
from .helpers import get_test_data


def json_to_djorm(data):
    """Return Stripe ORM object from json.

    Wrapper to take a JSON object returned from stripe
    and handle it with an ORM object.

    :param data: JSON data from stripe
    :type data: :class:`dict`
    """
    if not isinstance(data, dict):
        raise TypeError('data Attribute must be a dict')
    if 'object' not in data:
        raise TypeError('JSON data missing object')

    resource_type = data['object']

    Model = get_djorm_model_from_object_key(resource_type)

    return Model


def get_djorm_model_from_object_key(objkey):
    """Return django ORM model from object key.

    :param objkey: 'object' key from stripe JSON response
    :type objkey: string
    :returns: Django model from app
    """
    if not isinstance(objkey, text_type):
        raise TypeError('argument must be a string')

    app = apps.get_app_config('stripe')
    return app.get_model(objkey)


class TestJSONToObject(TestCase):

    def test_raises_object_missing(self):
        with self.assertRaisesRegexp(TypeError, 'must be a dict'):
            json_to_djorm('Hey')
        with self.assertRaisesRegexp(TypeError, 'must be a dict'):
            json_to_djorm(1)

    def test_raises_non_dict(self):
        with self.assertRaisesRegexp(TypeError, 'JSON data missing object'):
            data = get_test_data('customer/object.json')
            data.pop('object', None)
            json_to_djorm(data)


class TestGetDjormFromObjectKey(TestCase):

    def test_raises_error_if_not_string(self):
        with self.assertRaisesRegexp(TypeError, 'must be a string'):
            get_djorm_model_from_object_key(1)

    def test_raises_error_model_not_exist(self):
        with self.assertRaisesRegexp(
                LookupError,
                "App '\w*' doesn't have a '.*' model.",
        ):
            get_djorm_model_from_object_key('Moo')

    def test_imports_model_correctly(self):
        result = get_djorm_model_from_object_key('Customer')
        self.assertEquals(Customer, result)


class TestCustomer(TestCase):

    def test_create(self):
        self.data = get_test_data('customer/object.json')
