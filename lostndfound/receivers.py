from collections import Counter
import datetime
import re

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from lostnfound import settings
from models import LostItem, FoundItem, Location
from models import time_of_day_choices as time_of_day_choices_
from cached import get_location_data, set_main_page_markers_string
from cached import set_location_data, set_location_choices, set_cache, set_auth
from lostndfound.templatetags.mod_timesince import ago as timesince_self

time_of_day_choices = {a[0]: a[1].lower() for a in time_of_day_choices_}
time_of_day_choices['XXX'] = ''


def add_new_marker(i, x, y):
    """
    creates a new string for generating a marker for the google maps for
    the item 'i' at the 'x' and 'y' coordinates
    """

    content = ''.join([
        "newmarker(%(x)f, %(y)f, \"%(name)s\", \"%(description)s\", ",
        "\"%(time)s\", \"%(time_of_day)s\", \"%(itemtype)s\", \"%(link)s\", ",
        "\"%(imagelink)s\");"])%{
        'x': x,
        'y': y,
        'name': ' '.join(re.findall(r"[\w']+",
                        i.itemname.replace('"','\''))),
        'description': ' '.join(re.findall(r"[\w']+",
                                i.additionalinfo.replace('"','\''))),
        'time': timesince_self(i.time),
        'time_of_day': time_of_day_choices[i.time_of_day] \
                            if isinstance(i, LostItem) else '',
        'itemtype': 'lost' if isinstance(i, LostItem) else 'found',
        'link': '/get_confirm_modal/%s/%d'%(
            'lost' if isinstance(i, LostItem) else 'found',
            i.pk
            ),
        'imagelink': i.image.url if i.image else ''
    }
    return content


@receiver(post_save)
@receiver(post_delete) # should catch both the signals
def update_home_page(sender, **kwargs):
    """
    updates the home page markers and saves it to the cache
    """
    if sender not in [LostItem, FoundItem]: return

    days_old = getattr(settings, 'DAYS_OLD_HOME_PAGE_ITEMS', None) or 30

    # get all the lost and found items
    lost_items=LostItem.objects.all().filter(status=True).filter(
        pub_date__gt=timezone.now()-datetime.timedelta(
                                    days=days_old)).order_by('-pub_date')

    found_items=FoundItem.objects.all().filter(status=True).filter(
        pub_date__gt=timezone.now()-datetime.timedelta(
                                    days=days_old)).order_by('-pub_date')

    # is used for ensuring the items per location limit
    limiterByLocation = Counter([])

    final = ""                      # final string
    limit = get_location_data()     # get location data from cache
    itemsPerLocationLimit = getattr(settings,'ITEMS_PER_LOCATION', None) or 5

    #giving preference to recent lost items
    items = []
    items.extend(list(lost_items))
    items.extend(list(found_items))

    for i in items:

        # skips over if items per location limit has been reached.
        if limiterByLocation[i.location] == itemsPerLocationLimit:
            continue

        if(i.location in limit.keys()):
            # add to item-location counter
            limiterByLocation.update([i.location])

            # this method gives a believably random still viewable look
            # change x according to the number of items in that location.
            d1 = ((limit[i.location][2] - limit[i.location][0])/5)
            d2 =  limiterByLocation[i.location]
            d2 = d2 % d1 if d2 % 2 else d2
            delta = d1 * d2
            x = limit[i.location][0] + delta

            # change y according to the number of items in that location.
            d1 = ((limit[i.location][3] - limit[i.location][1])/5)
            d2 =  limiterByLocation[i.location]
            d2 = d2 if d2 % 2 else d2 % d1
            delta = d1 * d2
            y = limit[i.location][1] + delta

            # create a string for the marker for this item
            # and append it to the final string
            final = '\n'.join([add_new_marker(i, x, y), final])

    # save the final string data in the cache
    set_main_page_markers_string(final)
    # so that we know that we should not
    # fetch items from cache in the log view
    set_auth("log_items", False)


# changes data on adding a new location.
@receiver(post_save, sender=Location)
@receiver(post_delete, sender=Location)
def update_locations(sender, **kwargs):
    """
    updates location choices and location data in the cache.
    Triggered on adding/deleting new locations.
    """
    location_choices = []   # simply saves the names
    location_data = {}      # saves the location data
    for location in Location.objects.all():
        location_choices.append((location.name, location.name))
        location_data[location.name] = (location.x1, location.y1,
                                            location.x2, location.y2)

    # if no locations
    if Location.objects.count == 0:
        location_choices = ("None", "None")
        location_data["None"] = (0, 0, 90, 90)

    # save to cache
    set_location_choices(tuple(location_choices))
    set_location_data(location_data)