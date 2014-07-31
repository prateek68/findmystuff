from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from forms import LostItemForm,FoundItemForm
from models import LostItem,FoundItem
from django.utils import timezone
import datetime
from django.core.mail import send_mail
from lostnfound import settings

#######LAT LONG LIST#############
{"Faculty Residency":(28.5439000, 77.2704000,28.5443000, 77.2709000),"Academic Block":(28.5441000, 77.2722000,28.5448000, 77.2729000)}


def home(request):
    """Home view, displays login mechanism"""
    if request.user.is_authenticated():
        return redirect('done')
    return render_to_response('home.html', {}, RequestContext(request))


@login_required
def done(request):
    #print request
    s=User.objects.get(username=request.user).email
    s1 = s.split('@')[-1]
    if s1 not in settings.ALLOWED_HOSTS:
        User.objects.get(username=request.user).delete()
        return render_to_response('wronglogin.html', {}, RequestContext(request))
    """Login complete view, displays user data"""
    pre = LostItem.objects.all()
    #for ite1 in pre:
	#print "preee",ite1
    return redirect('gmap')
                              

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('home')

@login_required 
def lostitem(request):
	if (request.user!=""):
		if request.method == 'POST':
			lostitem_form=LostItemForm(request.POST,request.FILES)
			if lostitem_form.is_valid():
				lostitem_form.save()
				####FACEBOOK POST########
				#m = Mail()
				s=""
				s=s+lostitem_form.cleaned_data.get('username')+' ('+lostitem_form.cleaned_data.get('email')+') '
				s=s+"has Lost "+lostitem_form.cleaned_data.get('itemname')
				#s=s +"\n"+lostitem_form.cleaned_data.get('additonalinfo')
				s=s+" At "+lostitem_form.cleaned_data.get('location')
				send_mail(s, s,'iiitdfindmystuff@gmail.com', ['crete497valet@m.facebook.com'])
				#print "MAIL SENT"
				return redirect('done')
			return render_to_response('wrongpage.html', {},{})
		else :
			s=User.objects.get(username=request.user)
			lostitem_form={'lostitem_form':LostItemForm({'username':request.user,'email':s.email,'firstname':s.first_name,'lastname':s.last_name,'status':'active','pub_date':timezone.now()})}
			return render_to_response('LostItem.html',lostitem_form,RequestContext(request))
	return render_to_response('wrongpage.html', {},{})
@login_required
def founditem(request):
	if (request.user!=""):
		if request.method == 'POST':
			#print 'in request'
			#print request
			founditem_form=FoundItemForm(request.POST,request.FILES)
			#print 'in request'
			#print founditem_form
			if founditem_form.is_valid():
				#print 'in request'
				founditem_form.save()
				####FACEBOOK POST########
				#m = Mail()
				s=""
				s=s+founditem_form.cleaned_data.get('username')+' ('+founditem_form.cleaned_data.get('email')+') '
				s=s+"has found "+founditem_form.cleaned_data.get('itemname')
				#s=s +"\n"+founditem_form.cleaned_data.get('additonalinfo')
				s=s+" At "+founditem_form.cleaned_data.get('location')
				#m.send_mail(s)
				print s
				send_mail(s, s,'iiitdfindmystuff@gmail.com', ['crete497valet@m.facebook.com'])
				
				return redirect('done')
			return render_to_response('wrongpage.html', {},{})
		else :
			
			s=User.objects.get(username=request.user)
			founditem_form={'founditem_form':FoundItemForm({'username':request.user,'email':s.email,'firstname':s.first_name,'lastname':s.last_name,'status':'active','pub_date':timezone.now()})}
			return render_to_response('FoundItem.html',founditem_form,RequestContext(request))
	return render_to_response('wrongpage.html', {},{})
	

limit = {"Faculty Residency":(28.5439000, 77.2704000,28.5443000, 77.2709000), "Academic Block":(28.5441000, 77.2722000,28.5448000, 77.2729000), "Library Building":(28.5439000, 77.2722000,28.5440000, 77.2726000), "Student Activity Center":(28.5461649, 77.2731461,28.5462649, 77.2735461), "Boys Hostel":(28.5472649, 77.2734461,28.5475949, 77.2739461), "Girls Hostel":(28.5466649, 77.2732461,28.5468949, 77.2736461), "Sports Field":(28.5464649, 77.2720461,28.5480949, 77.2739461), "Parking Area":(28.544490 , 77.271325,28.544890 , 77.27185)}
import random
@login_required
def gmap(request):
	obj=LostItem.objects.all().filter(status='active').filter( pub_date__gt=timezone.now()-datetime.timedelta(days=10))
	ss = ""
	for i in obj:
		#print i
		#print i.email
		#print i.location	
		if(i.location in limit.keys()):
			x = random.uniform(limit[i.location][0], limit[i.location][2])
			y = random.uniform(limit[i.location][1], limit[i.location][3])
			#x = 28.5460459
		 	#y = 77.2714055
			contentString = ""
			contentString += '<div id="content">'+'<div id="siteNotice">'+'</div>'+'<h1 id="firstHeading" class="firstHeading">'+i.itemname+'</h1>'+ \
		  					'<div id="bodyContent">'+ '<p>'+str(i.additonalinfo)+'</p>'+'(Lost on '+str(i.time)+').</p>'+'<p text-align:right ><a href="/found/'+str(i.id)+'"> \<span class="label label-default">Report Found</span></a> '+ '</div>'+ '</div>';
			ss += 'newmarker('+str(x)+','+str(y)+',"'+i.itemname+'",\''+contentString+'\');'
	obj=FoundItem.objects.all().filter(status='active').filter( pub_date__gt=timezone.now()-datetime.timedelta(days=10))
	
	for i in obj:
		#print i
		#print i.email
		#print i.location	
		if(i.location in limit.keys()):
			x = random.uniform(limit[i.location][0], limit[i.location][2])
			y = random.uniform(limit[i.location][1], limit[i.location][3])
			#x = 28.5460459
		 	#y = 77.2714055
			contentString = ""
			contentString += '<div id="content">'+'<div id="siteNotice">'+'</div>'+'<h1 id="firstHeading" class="firstHeading">'+i.itemname+'</h1>'+ \
		  					'<div id="bodyContent">'+ '<p>'+str(i.additonalinfo)+'</p>'+'(Found on '+str(i.time)+').</p>'+'<p text-align:right ><a href="/lost/'+str(i.id)+'"> \ <span class="label label-default">Report Lost</span></a> '+ '</div>'+ '</div>';
			ss += 'newmarker('+str(x)+','+str(y)+',"'+i.itemname+'",\''+contentString+'\');'

	s={'s':ss}	
	#s={'s':'newmarker(28.5460459, 77.2714055,"magus",contentString);'+'newmarker(28.5450479, 77.2734055,"kshitij","hello world");'}
	return render_to_response('done.html',s,RequestContext(request))

def team(request):
	if request.method=='GET':

		return render_to_response('team.html',{},{})



def found(request,found_id):
	if request.method == 'GET' :
				s1="Congratulations ! Found Your Lost Item"
				s="We have found your item. "
				#print request
				s=s+"Please contact "+User.objects.get(username=request.user).first_name+" "+User.objects.get(username=request.user).last_name+" "+" "+User.objects.get(username=request.user).email
				#send_mai(s,LostItem.objects.get(id=found_id).email)
				send_mail(s1, s,"iiitdfindmystuff@gmail.com", [LostItem.objects.get(id=found_id).email])
				p=LostItem.objects.get(id=found_id)
				p.status='inactive'
				p.save()
				
				return redirect('gmap')

	return render_to_response('wrongpage.html', {},{})
def lost(request,lost_id):
	if request.method == 'GET' :
				s1="Found the owner of Lost Item"
				s="The item belongs to "+User.objects.get(username=request.user).first_name+" "+User.objects.get(username=request.user).last_name+". "
				s=s+"Please contact at "+User.objects.get(username=request.user).email
				#send_mai(s,FoundItem.objects.get(id=lost_id).email)
				send_mail(s1, s,"iiitdfindmystuff@gmail.com", [FoundItem.objects.get(id=lost_id).email])
				#LostItem.objects.get(id=found_id).delete()
				p=FoundItem.objects.get(id=lost_id)
				p.status='inactive'
				p.save()
				
				return redirect('gmap')
				

	return render_to_response('wrongpage.html', {},{})
def reopenfound(request,found_id):
	if request.method=='GET':
		p=FoundItem.objects.get(id=found_id)
		p.status='active'
		p.save()
	
	return redirect('gmap')
	
def reopenlost(request,lost_id):
	if request.method=='GET':
		p=LostItem.objects.get(id=lost_id)
		p.status='active'
		p.save()
	
	return redirect('gmap')
@login_required
def history(request):
	lost=LostItem.objects.all().filter(username=request.user).filter(status='inactive').order_by('-id')
	found=FoundItem.objects.all().filter(username=request.user).filter(status='inactive').order_by('-id')
	lostactive=LostItem.objects.all().filter(username=request.user).filter(status='active').order_by('-id')
	foundactive=FoundItem.objects.all().filter(username=request.user).filter(status='active').order_by('-id')
	s={'lost':lost,'found':found,'lostactive':lostactive,'foundactive':foundactive}
	return render_to_response('history.html',s,RequestContext(request))
@login_required
def log(request):
	lost=LostItem.objects.all().filter(status='active').order_by('-id')
	found=FoundItem.objects.all().filter(status='active').order_by('-id')
	s={'lost':lost,'found':found}
	return render_to_response('log.html',s,RequestContext(request))