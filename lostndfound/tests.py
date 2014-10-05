"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from models import LostItem, FoundItem, Location
import cached
import datetime
import receivers
import lostndfound.views

class CheckCache(TestCase):
    def setUp(self):
        self.location = Location.objects.create(name="some_place", x1=1, x2=52, y1=15, y2=16)
        self.user = User.objects.create(username="test_user", email='a@b.com', first_name="some", last_name="person")
        self.factory = RequestFactory()

    def create_lost_item(self):
        self.lost = LostItem.objects.create(user = self.user, itemname="lost1", location=self.location.name, additionalinfo="somthing", time=datetime.date.today(), time_of_day = 'XXX')

    def create_found_item(self):
        self.found = FoundItem.objects.create(user = self.user, itemname="found1", location=self.location.name, additionalinfo="somthing", time=datetime.date.today())

    def create_location(self):
        self.location1 = Location.objects.create(name="temp location", x1=1, x2=2, y1=3, y2=4)

    def test_adding_lost_item_updates_markers_string_in_cache(self):
        cached.set_main_page_markers_string("")
        self.assertFalse(cached.get_main_page_markers_string()) # cache should be empty at first
        self.create_lost_item()
        self.assertTrue(cached.get_main_page_markers_string())  # cache should contain data

    def test_adding_found_item_updates_markers_string_in_cache(self):
        cached.set_main_page_markers_string("")
        self.assertFalse(cached.get_main_page_markers_string()) # cache should be empty at first
        self.create_found_item()
        self.assertTrue(cached.get_main_page_markers_string())  # cache should contain data

    def test_deleting_lost_item_updates_markers_string_in_cache(self):
        cached.set_main_page_markers_string("")
        self.create_lost_item()
        self.lost.delete()
        self.assertFalse(cached.get_main_page_markers_string()) # cache should be empty now

    def test_deleting_lost_item_updates_markers_string_in_cache(self):
        cached.set_main_page_markers_string("")
        self.create_found_item()
        self.found.delete()
        self.assertFalse(cached.get_main_page_markers_string()) # cache should be empty now

    def test_changing_status_of_lost_item_should_change_markers_string(self):
        self.create_lost_item()
        check1 = cached.get_main_page_markers_string()
        self.lost.status = False
        self.lost.save()
        check2 = cached.get_main_page_markers_string()
        self.assertNotEqual(check1, check2)

    def test_changing_status_of_found_item_should_change_markers_string(self):
        self.create_found_item()
        check1 = cached.get_main_page_markers_string()
        self.found.status = False
        self.found.save()
        check2 = cached.get_main_page_markers_string()
        self.assertNotEqual(check1, check2)

    def test_log_items_auth_should_be_false_at_startup(self):
        self.assertFalse(cached.check_auth('log_items'))

    def test_log_items_auth_should_change_on_adding_lost_item(self):
        cached.set_auth('log_items', True)
        self.assertTrue(cached.check_auth('log_items'))
        self.create_lost_item()
        self.assertFalse(cached.check_auth('log_items'))

    def test_log_items_auth_should_change_on_adding_found_item(self):
        cached.set_auth('log_items', True)
        self.assertTrue(cached.check_auth('log_items'))
        self.create_found_item()
        self.assertFalse(cached.check_auth('log_items'))

    def test_that_accessing_log_view_updates_cache(self):
        self.create_lost_item()
        self.create_found_item()

        cached.set_cache("lost", "")
        cached.set_cache("found", "")
        self.assertFalse(cached.check_auth('log_items'))
        self.assertFalse(cached.get_cache('lost'))
        self.assertFalse(cached.get_cache('found'))

        request = self.factory.get('/log/')
        lostndfound.views.log(request)
        lostndfound.views.log(request)

        # I have to call the view twice. There is nothing wrong with this
        # The first call will also call the startupcache method, which will
        # set the auth of log_items to False. However, subsequent calls to 
        # view work as expected.

        self.assertTrue(cached.check_auth('log_items'))
        self.assertTrue(cached.get_cache('lost'))
        self.assertTrue(cached.get_cache('found'))

    def test_log_items_auth_should_change_on_changing_item_status(self):
        cached.set_auth('log_items', True)
        self.create_lost_item()
        self.lost.status = False
        self.lost.save()
        self.assertFalse(cached.check_auth('log_items'))

        cached.set_auth('log_items', True)
        self.create_found_item()
        self.found.status = False
        self.found.save()
        self.assertFalse(cached.check_auth('log_items'))

        cached.set_auth('log_items', True)
        self.create_lost_item()
        self.lost.status = True
        self.lost.save()
        self.assertFalse(cached.check_auth('log_items'))

        cached.set_auth('log_items', True)
        self.create_found_item()
        self.found.status = True
        self.found.save()
        self.assertFalse(cached.check_auth('log_items'))

        cached.set_auth('log_items', True)
        self.lost.delete()
        self.assertFalse(cached.check_auth('log_items'))

        cached.set_auth('log_items', True)
        self.found.delete()
        self.assertFalse(cached.check_auth('log_items'))

    def test_adding_location_changes_location_data_in_cache(self):
        check1 = cached.get_location_data()
        self.create_location()
        check2 = cached.get_location_data()
        self.assertNotEqual(check1, check2)

    def test_adding_location_changes_location_choices_in_cache(self):
        check1 = cached.get_location_choices()
        self.create_location()
        check2 = cached.get_location_choices()
        self.assertNotEqual(check1, check2)

    def test_deleting_location_changes_location_data_in_cache(self):
        self.create_location()
        check1 = cached.get_location_data()
        self.location1.delete()
        check2 = cached.get_location_data()
        self.assertNotEqual(check1, check2)

    def test_deleting_location_changes_location_choices_in_cache(self):
        self.create_location()
        check1 = cached.get_location_choices()
        self.location1.delete()
        check2 = cached.get_location_choices()
        self.assertNotEqual(check1, check2)

    def test_set_auth_and_check_auth_of_cached_work(self):
        cached.set_auth('temp', True)
        self.assertTrue(cached.check_auth('temp'))

        cached.set_auth('temp', False)
        self.assertEqual(cached.check_auth('temp'), False)

        from django.core.cache import cache
        cache.delete('temp')