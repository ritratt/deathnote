from django import forms
from django.contrib.auth.models import User
class SignForm(forms.Form):
	email = forms.EmailField(error_messages = {'unique':'Duplicate!'})
	password = forms.CharField( widget = forms.PasswordInput(render_value = False), label = "Password")
	deathnote = forms.CharField(widget = forms.Textarea(attrs = {'class':'span11'}))
	ntrustees = forms.IntegerField(label = 'Number of Trustees')
	
	def clean(self):

        	if User.objects.filter(email=self.cleaned_data['email']).exists():
			msg = _(u'Duplicate Error!')
            		self._errors['email'] = ErrorList([msg])
            		del self.cleaned_data['email']
        	return self.cleaned_data
	

class ReadForm(forms.Form):
	email = forms.EmailField(label = "Email of the deceased")
	key_read = forms.CharField(label = "Key given to you by the deceased")

class EditAuthForm(forms.Form):
        email = forms.EmailField(label = "Email of the deceased")
	password = forms.CharField(widget = forms.PasswordInput(render_value = False), label = "Password")
	
class EditForm(forms.Form):
	decrypted_note = forms.CharField(widget = forms.Textarea(attrs = {'class':'spann11'}))

class ReadForm(forms.Form):
	email_deceased = forms.EmailField()
	piece = forms.CharField( widget = forms.PasswordInput(render_value = False), label = 'Piece')
