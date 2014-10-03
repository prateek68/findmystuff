from itertools import chain
import json
import re

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from lostnfound import settings
from communication import PostToFB, send_mail
from forms import LostItemForm,FoundItemForm, FeedbackForm
from LnF404.models import RecentLostItem
from lostndfound.cached import get_cache, set_cache
from lostndfound.cached import get_main_page_markers_string, check_auth
from models import LostItem,FoundItem, Feedback
import mails
import receivers

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
        'markers':get_main_page_markers_string})

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
            obj.user = request.user
            obj.itemname = ' '.join(re.findall(r"[\w']+",
                                     obj.itemname.replace('"','\'')))
            obj.additionalinfo = ' '.join(re.findall(r"[\w']+",
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
            obj.user = request.user
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
        send_mail(subject, content,
                    settings.EMAIL_HOST_USER, [item.user.email])

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
        send_mail(subject, content,
                    settings.EMAIL_HOST_USER, [item.user.email])

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
    if check_auth('log_items'):
        lost = get_cache('lost')
        found = get_cache('found')
    else:
        lost = LostItem.objects.all().filter(status=True).order_by('-id')
        found = FoundItem.objects.all().filter(status=True).order_by('-id')
        set_cache('lost', lost)
        set_cache('found', found)
        set_cache('log_items_auth', True)

    return render(request, 'log.html', {'lost':lost,'found':found})

def get_confirm_modal(request, itemtype, itemid):
    """
    sends confirmation modal.
    """
    success = True

    if not itemtype in ['lost', 'found']:
        success = False
    try:
        item = LostItem.objects.get(pk=itemid) if itemtype == 'lost' else \
                FoundItem.objects.get(pk=itemid)
    except (LostItem.DoesNotExist, FoundItem.DoesNotExist):
        success = False

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
    if (not request.user.is_authenticated()) or \
            (not request.is_ajax() and not request.method == "POST"):
        return HttpResponse("Please login and go to the main page.")
    form = FeedbackForm()
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
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
        item.status = False # to ensure that it's removed from the api.
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
    items = RecentLostItem.objects.all()[:5]
    return render(request, '404.html', {'items': items})

def search(request):
    """
    sends a json reponse of the ids of the items matching the query.
    """
    response, resp = [], []
    if request.method == "GET":
        query = request.GET.get('query', None)
        scope = request.GET.get('scope', None)

        if query:
            if scope == 'all':

                resp1 = LostItem.objects.filter(status=True).filter(
                    Q(itemname__icontains = query) |
                    Q(additionalinfo__icontains = query) |
                    Q(location__icontains = query))
                resp2 = FoundItem.objects.filter(status=True).filter(
                    Q(itemname__icontains = query) |
                    Q(additionalinfo__icontains = query) |
                    Q(location__icontains = query))

            elif scope == 'self':
                resp1 = request.user.lostitem_set.filter(
                    Q(itemname__icontains = query) |
                    Q(additionalinfo__icontains = query) |
                    Q(location__icontains = query))
                resp2 = request.user.founditem_set.filter(
                    Q(itemname__icontains = query) |
                    Q(additionalinfo__icontains = query) |
                    Q(location__icontains = query))

            else: resp1 = resp2 = []

            resp = list(chain(resp1, resp2))

    for i in resp:
        response.append('-'.join([
            'lost' if isinstance(i, LostItem) else 'found',
            str(i.pk)]))

    return HttpResponse(json.dumps(response),
        content_type ="application/json")
