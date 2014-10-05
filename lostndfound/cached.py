from django.core.cache import cache

# specifically get/set the location choices.
def get_location_choices():
    return cache.get('location_choices')
def set_location_choices(a):
    cache.set('location_choices', a)

# specifically get/set the locations data
def get_location_data():
    return cache.get('location_data')
def set_location_data(a):
    cache.set('location_data', a)

# specifically get/set the string for the main page markers
def get_main_page_markers_string():
    return cache.get('main_page_markers_string')
def set_main_page_markers_string(a):
    cache.set('main_page_markers_string', a)

# general methods for accessing the cache
def get_cache(key):
    return cache.get(key)
def set_cache(key, value):
    cache.set(key, value)

def check_auth(string):
    """
    For checking whether a value is authentic.
    If false, the data needs to be refreshed.
    """
    return bool(cache.get(''.join([string,'_auth'])))
def set_auth(string, boolean):
    """Set authentic value for a key"""
    set_cache(''.join([string, '_auth']), boolean)