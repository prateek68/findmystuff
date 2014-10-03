from django.core.cache import cache

def get_location_choices():
    return cache.get('location_choices')
def set_location_choices(a):
    cache.set('location_choices', a)

def get_location_data():
    return cache.get('limit')
def set_location_data(a):
    cache.set('limit', a)

def get_main_page_markers_string():
    return cache.get('main_page_markers_string')
def set_main_page_markers_string(a):
    cache.set('main_page_markers_string', a)

def get_cache(key):
    return cache.get(key)
def set_cache(key, value):
    cache.set(key, value)

def check_auth(string):
    return bool(cache.get(''.join([string,'_auth'])))
def set_auth(string, boolean):
    set_cache(''.join([string, '_auth']), boolean)