# -*- coding: UTF-8 -*-
"""
A suite of tests for the HTTP API schemas
"""
import unittest

from jsonschema import Draft4Validator, validate, ValidationError
from vlab_router_api.lib.views import router


class TestRouterViewSchema(unittest.TestCase):
    """A set of test cases for the schemas of /api/1/inf/router"""

    def test_post_schema(self):
        """The schema defined for POST on is valid"""
        try:
            Draft4Validator.check_schema(router.RouterView.POST_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_get_schema(self):
        """The schema defined for GET on is valid"""
        try:
            Draft4Validator.check_schema(router.RouterView.GET_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_delete_schema(self):
        """The schema defined for DELETE on is valid"""
        try:
            Draft4Validator.check_schema(router.RouterView.DELETE_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_images_schema(self):
        """The schema defined for GET on /images is valid"""
        try:
            Draft4Validator.check_schema(router.RouterView.IMAGES_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_post_requires_image(self):
        """The schema defined for POST requires the parameter 'image'"""
        body = {'name': 'myRouter', 'networks': ['net1', 'net2']}
        try:
            validate(body, router.RouterView.POST_SCHEMA)
            schema_valid = False
        except ValidationError:
            schema_valid = True

        self.assertTrue(schema_valid)

    def test_post_requires_networks(self):
        """The schema defined for POST requires the parameter 'networks'"""
        body = {'name': 'myRouter', 'image': '1.0.32'}
        try:
            validate(body, router.RouterView.POST_SCHEMA)
            schema_valid = False
        except ValidationError:
            schema_valid = True

        self.assertTrue(schema_valid)

    def test_post_requires_networks_min_2(self):
        """The schema defined for POST requires the parameter 'networks' have at least 2 elements"""
        body = {'name': 'myRouter', 'image': '1.0.32', 'networks': ['net1']}
        try:
            validate(body, router.RouterView.POST_SCHEMA)
            schema_valid = False
        except ValidationError:
            schema_valid = True

        self.assertTrue(schema_valid)

    def test_post_requires_networks_max_4(self):
        """The schema defined for POST requires the parameter 'networks' have at most 4 elements"""
        body = {'name': 'myRouter', 'image': '1.0.32', 'networks': ['net1', 'net2', 'net3', 'net4', 'net5']}
        try:
            validate(body, router.RouterView.POST_SCHEMA)
            schema_valid = False
        except ValidationError:
            schema_valid = True

        self.assertTrue(schema_valid)


if __name__ == '__main__':
    unittest.main()
