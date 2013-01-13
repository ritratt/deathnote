from django.shortcuts import render_to_response
from deathnote.forms import SignForm, EditAuthForm, EditForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from deathnote.functions import encipher, decipher

def home(request):
	try:
		response = 'Requested through ' + str(request.META['HTTP_USER_AGENT']) + ' browser.'
		return HttpResponse(response)
	except KeyError:
		return HttpResponse('No idea.')

def note_write(request):
	if request.method == 'POST':
		form = SignForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			deathnote = form.cleaned_data['deathnote']
			password = form.cleaned_data['password']
			piece = encipher(email, deathnote, password)
			return render_to_response('confirmation.htm', {'user':form['email'], 'piece':piece})
	else:
		form = SignForm()
	return render_to_response('home.htm', {'form':form}, context_instance = RequestContext(request))

def note_edit(request):
	if request.method == 'POST':
		form = EditAuthForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			decrypted_note = decipher('write', email, password)
			if decrypted_note:
				form_edit = EditForm({'decrypted_note' : decrypted_note})
				return render_to_response('editnote.htm', {'form':form_edit})
			else:
				return HttpResponse('dafq')
	else:
		form = EditAuthForm()
	return render_to_response('editauth.htm', {'form':form}, context_instance = RequestContext(request))
