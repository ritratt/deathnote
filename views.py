from django.shortcuts import render_to_response
from deathnote.forms import SignForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from pbkdf2 import PBKDF2
import random
from deathnote.functions import encipher

def home(request):
	try:
		response = 'Requested through ' + str(request.META['HTTP_USER_AGENT']) + ' browser.'
		return HttpResponse(response)
	except KeyError:
		return HttpResponse('No idea.')

def deathnote(request):
	if request.method == 'POST':
		form = SignForm(request.POST)
		if form.is_valid():
			encipher(str(form['deathnote']), str(form['password']))
			return HttpResponseRedirect('/')
	else:
		form = SignForm()
	return render_to_response('home.htm', {'form':form}, context_instance = RequestContext(request))


def sign(request):
#	if request.GET
	return HttpResponse(request.GET['name'])
