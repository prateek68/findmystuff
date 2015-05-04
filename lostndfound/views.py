from itertools import chain
import json
import re

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from lostnfound import settings
from communication import PostToFB, send_mail
from forms import LostItemForm,FoundItemForm, FeedbackForm
from LnF404.models import RecentLostItem
from lostndfound.cached import get_cache, set_cache, set_auth
from lostndfound.cached import get_main_page_markers_string, check_auth
from models import LostItem,FoundItem, Feedback
import mails
import receivers
from utils import search as search_database

def logout(request):
    """Logs out user"""
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

def gmap(request):
    """
    Home page of the app.
    Shows the google map with recently lost found items
    """
    return render(request, 'done.html',{
        'markers':get_main_page_markers_string()})

@login_required
def lostitem(request):
    """
    Shows the form for adding a lost item. Handles the post data of the form
    """
    lostitem_form = LostItemForm()
    if request.method == 'POST':
        lostitem_form=LostItemForm(request.POST, request.FILES)
        if lostitem_form.is_valid():
            obj = lostitem_form.save(commit=False)
            # add reference to user
            obj.user = request.user
            # to ensure that strings generated for markers are properly escaped.
            obj.itemname = ' '.join(re.findall(r"[\w.?!']+",
                                     obj.itemname.replace('"','\'')))
            obj.additionalinfo = ' '.join(re.findall(r"[\w.?!']+",
                                        obj.additionalinfo.replace('"','\'')))
            obj.save()

            PostToFB(mails.FB_LOST_ITEM_POST%{
                    'name': ' '.join([obj.user.first_name,
                                         obj.user.last_name]),
                    'email': obj.user.email, 'itemname': obj.itemname,
                    'location': obj.location, 'details': obj.additionalinfo
                })

            messages.success(request,
                                "Your item has been added to the portal.")
            return redirect('home')

        messages.error(request,
                    "There was something wrong in the information provided.")

    return render(request, 'LostItem.html', {'lostitem_form': lostitem_form})

@login_required
def founditem(request):
    """
    Shows the form for reporting a found item.
    Handles the post data of the form.
    """
    founditem_form = FoundItemForm()
    if request.method == 'POST':
        founditem_form=FoundItemForm(request.POST, request.FILES)
        if founditem_form.is_valid():
            obj = founditem_form.save(commit=False)
            # add reference to user
            obj.user = request.user
            # to ensure that strings generated for markers are properly escaped.
            obj.itemname = ' '.join(re.findall(r"[\w']+",
                                    obj.itemname.replace('"','\'')))
            obj.additionalinfo = ' '.join(re.findall(r"[\w']+",
                                    obj.additionalinfo.replace('"','\'')))
            obj.save()

            PostToFB(mails.FB_FOUND_ITEM_POST%{
                    'name': ' '.join([obj.user.first_name, obj.user.last_name]),
                    'email': obj.user.email, 'itemname': obj.itemname,
                    'location': obj.location, 'details': obj.additionalinfo
                })

            messages.success(request,
                "Your item has been added to the portal.")
            return redirect('home')

        messages.error(request,
            "There was something wrong in the information provided.")

    return render(request, 'FoundItem.html', {
        'founditem_form': founditem_form})


def team(request):
    """
    Displays the team developer page.
    """
    return render(request, 'team.html')

@login_required
def found(request,found_id):
    """
    This is the implementation via which users can say
    that they've found something that some user had
    reported lost.
    """
    if request.method == 'GET':
        item = get_object_or_404(LostItem, pk = found_id)

        subject = mails.EMAIL_FOUND_YOUR_ITEM_SUBJECT%{
                                    'itemname': item.itemname}
        content = mails.EMAIL_FOUND_YOUR_ITEM%{
            'self_name': item.user.first_name, 'itemname': item.itemname,
            'name': ' '.join([request.user.first_name,
                                 request.user.last_name]),
            'email': request.user.email, 'link': reverse('reopenlost',
                                                 kwargs={'lost_id': found_id})
        }
        # send email to the person who had lost the item.
        send_mail(subject, content,
                    settings.EMAIL_HOST_USER, [item.user.email])

        # this is to remove the item from the main page.
        item.status = False
        item.found_by = request.user
        item.save()

    else:
        messages.warning(request,
            "There was something wrong in the request you sent.")
    return redirect('home')

@login_required
def lost(request,lost_id):
    """
    This is the implementation via which users can claim
    a reported found item as theirs.
    """
    if request.method == 'GET' :
        item = get_object_or_404(FoundItem, pk = lost_id)

        subject = mails.EMAIL_FOUND_OWNER_SUBJECT%{'itemname': item.itemname}
        content = mails.EMAIL_FOUND_OWNER%{
            'self_name': item.user.first_name, 'itemname': item.itemname,
            'name': ' '.join([request.user.first_name,
                                request.user.last_name]),
            'email': request.user.email, 'link': reverse('reopenfound',
                                                 kwargs={'found_id': lost_id})
        }
        # send email to the person who had found the item.
        send_mail(subject, content,
                    settings.EMAIL_HOST_USER, [item.user.email])

        # change status to remove item from the home page and from the API
        item.status = False
        item.lost_by = request.user
        item.save()

    else:
        messages.warning(request,
            "There was something wrong in the request you sent.")
    return redirect('home')


@login_required
def reopenfound(request,found_id):
    """
    Allows a user to repoen their items
    that they had reported found before
    """
    if request.method=='GET':
        item = get_object_or_404(FoundItem, pk = found_id)
        if not item.user == request.user:
            messages.warning(request, "It seems that it isn't your item.")
            return redirect('home') 
        item.status = True
        item.lost_by = None
        item.save()
        messages.success(request,
                        "Your item has been added again to the portal.")
    else:
        messages.warning(request,
            "There was something wrong in the request you sent.")
    return redirect('home')

@login_required
def reopenlost(request,lost_id):
    """
    Allows a user to repoen their items
    that they had reported lost before
    """
    if request.method=='GET':
        item = get_object_or_404(LostItem, pk = lost_id)
        if not item.user == request.user:
            messages.warning(request, "It seems that it isn't your item.")
            return redirect('home')
        item.status = True
        item.found_by = None
        item.save()
        messages.success(request,
            "Your item has been added again to the portal.")
    else:
        messages.warning(request,
            "There was something wrong in the request you sent.")
    return redirect('home')

@login_required
def history(request):
    """
    Shows the list of items that the user has reported.
    """
    lost = request.user.lostitem_set.filter(
                                        status=False).order_by('-id')
    found = request.user.founditem_set.filter(
                                        status=False).order_by('-id')
    lostactive = request.user.lostitem_set.filter(
                                           status=True).order_by('-id')
    foundactive = request.user.founditem_set.filter(
                                            status=True).order_by('-id')
    return render(request, 'history.html',{
        'lost':lost, 'found':found,
        'lostactive':lostactive, 'foundactive':foundactive
        })

def log(request):
    """
    Shows the list of all reported items.
    Fetches it from the cache. 
    """
    if check_auth('log_items'):    # retrieve from cache if data is authentic
        lost = get_cache('lost')
        found = get_cache('found')
    else:
        lost = LostItem.objects.all().filter(status=True).order_by('-id')
        found = FoundItem.objects.all().filter(status=True).order_by('-id')
        # save to the cache
        set_cache('lost', lost)
        set_cache('found', found)
        # set auth of log_items
        set_auth('log_items', True)

    return render(request, 'log.html', {'lost':lost,'found':found})

def get_confirm_modal(request, itemtype, itemid):
    """
    sends confirmation modal according to item.
    """
    success = True

    # check type
    if not itemtype in ['lost', 'found']:
        success = False
    try:
        item = LostItem.objects.get(pk=itemid) if itemtype == 'lost' else \
                FoundItem.objects.get(pk=itemid)
    except (LostItem.DoesNotExist, FoundItem.DoesNotExist):
        success = False     # item does not exist

    if not success:
        itemtype = ''
        itemid = ''
        itemname = ''
        item = None

    return render(request, 'confirm_modal.html', {
        'success':success, 'itemtype': itemtype, 'itemid':itemid,
        'itemname':item.itemname if item else ''})

def feedback(request):
    """
    sends the feedback modal.
    """
    logged_in = True

    # CHECKS:
    #   i) user is logged in
    #   ii) request is either ajax for requesting feedback modal
    #   iii) request is a POST request for submitting feedback
    # else error
    if (not request.user.is_authenticated()) or \
            (not request.is_ajax() and not request.method == "POST"):
        return HttpResponse("Please login and go to the main page.")

    form = FeedbackForm()
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user         # add user
            obj.save()
            messages.success(request, "Thank you for your valuable feedback.")
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'feedback.html',{
        'form': form, 'logged_in': logged_in })

@login_required
def deletelost(request, lost_id):
    """
    deletes a reported lost item.
    """
    item = get_object_or_404(LostItem, pk=lost_id)
    if item.user == request.user:
        # IMP: make status False to ensure that it's removed from the api.
        # Also the hacky way of using update is used, rather than save
        # since I want to avoid sending any unnecessary signals now.
        LostItem.objects.filter(pk=item.pk).update(
            status=False)
        item = get_object_or_404(LostItem, pk=lost_id)
        item.delete()
        messages.success(request,
                            "Your item has been deleted from the portal.")
    else:
        messages.warning(request, "It seems that it isn't your item.")
    return HttpResponseRedirect(reverse('home'))

@login_required
def deletefound(request, found_id):
    """
    deletes a reported found item.
    """
    item = get_object_or_404(FoundItem, pk=found_id)
    if item.user == request.user:
        item.delete()
        messages.success(request,
                        "Your item has been deleted from the portal.")
    else:
        messages.warning(request, "It seems that it isn't your item.")
    return HttpResponseRedirect(reverse('home'))

def handle404(request):
    """
    Handles the app's 404 errors.
    """
    items = RecentLostItem.objects.all()[:5]    # simulates the API response.
    return render(request, '404.html', {'items': items})

def search(request):
    """
    sends a json reponse of the ids of the items matching the query.
    """
    # response is the final list of 'name-pk' to be sent
    # filtered in the filtered list of matching items
    response, filtered = [], []
    if request.method == "POST":
        query = request.POST.get('query', None)  # extract search query
        scope = request.POST.get('scope', None)  # extract scope

        # search for the query to match for:
        #   1) name of the item
        #   2) additional information within the item
        #   3) location where the item was reported lost or found
        if query and scope in ['all', 'self']:
            (find_location1, find_location2) = (LostItem.objects,
                    FoundItem.objects) if scope == 'all' else \
                    (request.user.lostitem_set, request.user.founditem_set)
            filtered = search_database(query, find_location1, find_location2)

    # create response
    for i in filtered:
        response.append('-'.join([
            'lost' if isinstance(i, LostItem) else 'found',
            str(i.pk)]))

    return HttpResponse(json.dumps(response),
        content_type ="application/json")

def autocomplete_search(request):
    """
    Sends name of the items, and the url to request more information
    when the user is reporting a new item lost/found
    """
    response = []
    if request.method == "GET":
        query = request.GET.get('query', None)
        query_type = request.GET.get('type', None)

        if (not all([query, query_type])) or query_type not in ['lost', 'found']:
            return HttpResponse(json.dumps(response),
                content_type="application/json")

        to_search = LostItem.objects if query_type=='lost' else FoundItem.objects
        search_result = search_database(query, to_search, reverse=True)[:5]

        for x in search_result:
            response.append({
                    'itemname': x.itemname,
                    'url': reverse('autocomplete_info', kwargs={
                                'pk': x.pk, 'category': query_type})
                })

    return HttpResponse(json.dumps(response), content_type="application/json")

def autocomplete_info(request, category, pk):
    """
    Returns a modal containing all the information, as well as the url to
    get the confirm modal.
    """
    to_search = LostItem if category == 'lost' else FoundItem
    result = to_search.objects.filter(pk=pk)
    result = result[0] if result else None
    return render(request, 'autocomplete_info.html', {
                    'item': result,
                    'confirm_modal_link': reverse('get_confirm_modal',
                        kwargs={
                            'itemtype': category,
                            'itemid': result.pk
                        }) if result else None
                    })

def fb_privacy_policy(request):
    """
    Shows the privacy policy of the facebook app.
    """
    return render(request, 'fb_privacy_policy.html')

def fb_login(request):
    """
    Login via fb, and give the access token in the console. The developer
    should copy the token from the console and set the access token in the 
    server and restart it every 2 months or so.
    """
    app_id = settings.FACEBOOK_APP_ID
    return render(request, 'fb_login.html', {
        'app_id':app_id})