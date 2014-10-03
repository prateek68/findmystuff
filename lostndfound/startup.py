import django.db.utils
from models import Location, LostItem

# for the first time that the server is started
def startup_cache():
    """
    Should be called when the app is started for the first time
    """
    try:
        # TODO
        import receivers
        receivers.update_locations(Location)
        receivers.update_home_page(LostItem)
    except (django.db.utils.OperationalError):
        print "If the db is being constructed for the first time,\
         this is normal. else please check"