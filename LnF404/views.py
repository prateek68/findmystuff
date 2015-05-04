import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt

from lostnfound import settings
from lostndfound.models import LostItem, FoundItem
from lostndfound.utils import search
from LnF404.forms import AddWebsiteForm
from LnF404.models import RecentLostItem, AuthenticationToken

@login_required
def add(request):
    """ Gives a new site id and authentication token
    to the user.
    """

    websites = AuthenticationToken.objects.filter(user = request.user)

    if request.method == 'POST':
        form = AddWebsiteForm(request.user, request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            #add user to the token object
            obj.user = request.user
            obj.save()
            return HttpResponseRedirect(reverse('add_404_website'))
    else:
        # new form for a GET request
        form = AddWebsiteForm(request.user.pk)
    return render(request, '404_apps.html', {'form': form,
     'websites': websites})

@login_required
def refresh_token(request, token_id):
    """ Refreshes the token, in case the user feels that the token has been leaked
    """
    site = get_object_or_404(AuthenticationToken, pk=token_id)
    if site.user == request.user:
        site.save()
        # the overloaded save method will generate a new token
    return HttpResponseRedirect(reverse('add_404_website'))

# this is kept here rather than in a receivers.py file
# as this is the only important thing in this app,
# and it's not big.
@receiver(pre_delete) # the item status should be false before calling delete()
@receiver(post_save)
def update_404_items(sender, **kwargs):
    """ Updates the list of recently lost items.
    """
    if sender != LostItem:
        return

    item = kwargs['instance']
    num  = getattr(settings, 'LnF404_ITEMS_NUMBER', 20)

    if item.status == True:
        RecentLostItem.objects.create(item=item)        # adds the new object
        if RecentLostItem.objects.all().count() > num: 
            RecentLostItem.objects.first().delete()     # ensures the max size

    else:
        # is faster than RecentLostItem.objects.filter(item=item)
        check = item.recentlostitem_set.first()
        if check:
            # delete the object that was found
            check.delete()
            # get all currently lost items
            new_item = LostItem.objects.filter(
                status=True).order_by('-pub_date')
            for x in new_item:
                if not RecentLostItem.objects.filter(item=x).first():
                    # add the first item which is not in the API list
                    new_item = x
                    break
            else:
                #no item found which is currectly active and not in our list
                return
            # add the found object
            RecentLostItem.objects.create(item=new_item)

def confirmIP(request, allotedIP):
    #TODO our nginx at the proxy is not adding forwarded_for header. request IT department
    return True
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    if ip == allotedIP.split(':')[0]:
        return True
    return False

def _build_JSON_response(request, response, quantity, items_to_build=None):
    """ Takes in how many items to consider,
    and builds a dictionary response
    """
    # send appropriate quantity parameter
    response['quantity'] = quantity

    items = items_to_build if items_to_build != None else \
                    RecentLostItem.objects.all().order_by('pk').reverse()

    # create data to send
    for i, link in enumerate(items):

        item  = link.item if isinstance(link, RecentLostItem) else link
        json_item_data = {}
        json_item_data['item-name'] = item.itemname
        json_item_data['location']  = item.location
        json_item_data['info']      = item.additionalinfo
        json_item_data['image']     = bool(item.image)
        json_item_data['image_url'] = request.build_absolute_uri(
                                        item.image.url if \
                                        item.image else static(
                                         'noimage_placeholder.jpg'))

        response[i] = json_item_data

        # doesn't break at 0 even if quantity is None.
        if (i + 1) == quantity: break

    return response

def _authenticate(request, site_id, token):
    if site_id and token: # parameters were readable
        try:
            site = AuthenticationToken.objects.get(pk=site_id)
            site = site if confirmIP(request, site.website_IP) else None
        except AuthenticationToken.DoesNotExist:
            # an app with this app_id was not registered.
            site = None

        if site and site.token == token: # authenticating the app with token
            return True
    return False

# csrf_exempt decorator to allow POST requests
@csrf_exempt
def send_data(request, site_id='0', token='0', quantity = 0):
    """ Sends the requested data
    """
    response    = {'success': 'true'}
    num         = 6     # no. of items to send back

    # a GET request with parameters
    if token == '0':
        dictionary = request.POST if request.method == "POST" else request.GET
    # a GET request with parameters as url path. basically for debugging.
    else:
        dictionary = {'id': site_id,
         'token': token,
         'quantity': quantity if quantity > 0 else num}

    token_id = int(dictionary.get('id', -1))
    token    = str(dictionary.get('token', None))
    quantity = int(dictionary.get('quantity', num))

    if _authenticate(request, token_id, token):
        response = _build_JSON_response(request, response, min([
                        RecentLostItem.objects.all().count(), quantity]))
        return HttpResponse(json.dumps(response),
                            content_type="application/json")

    # if authentication failed, or app was not registered.
    response['success'] = 'false'
    return HttpResponse(json.dumps(response), content_type="application/json")

@csrf_exempt
def send_search_results(request):
    """ Sends the items matching the query
    """

    response = {'success': 'true'}
    dictionary = request.POST if request.method == "POST" else request.GET

    token_id = int(dictionary.get('id', -1))
    token    = str(dictionary.get('token', None))
    query    = str(dictionary.get('query', None))

    if _authenticate(request, token_id, token):
        items       = list(search(query, LostItem.objects, FoundItem.objects))
        quantity    = int(dictionary.get('quantity', len(items)))
        response    = _build_JSON_response(request, response, quantity, items)
        return HttpResponse(json.dumps(response),
                            content_type="application/json")

    # if authentication failed, or app was not registered.
    response['success'] = 'false'
    return HttpResponse(json.dumps(response), content_type="application/json")