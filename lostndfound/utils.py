from itertools import chain
from django.db.models import Q
from models import LostItem, FoundItem

def search(query, location1, location2=None, reverse=False):
    """Searches the database for matching queries"""
    filtered1 = location1.filter(status=True).filter(
        Q(itemname__icontains = query) |
        Q(additionalinfo__icontains = query) |
        Q(location__icontains = query))
    if reverse: filtered1 = filtered1.order_by('-time')

    if location2 is None: return filtered1

    filtered2 = location2.filter(status=True).filter(
        Q(itemname__icontains = query) |
        Q(additionalinfo__icontains = query) |
        Q(location__icontains = query))
    if reverse: filtered2 = filtered2.order_by('-time')

    # join the 2 lists blazingly fast
    return chain(filtered1, filtered2)