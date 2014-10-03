import django.db.utils
from models import Location, LostItem
import cached

# for the first time that the server is started
def startup_cache():
    """
    Should be called when the app is started for the first time
    """
    import receivers
    receivers.update_locations(Location)
    receivers.update_home_page(LostItem)