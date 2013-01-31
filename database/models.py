from django.db import models

class deathbook(models.Model):
	
	def __unicode__(self):
		return self.user_email

	user_email = models.EmailField()#(primary_key = True)
	
	#Fields required only for write access and operations on the note.
	deathnote_write = models.TextField()
	iv_write = models.CharField(max_length = 255)
	
	#Fields required only for read access and operations on the note.
	piece_hash = models.CharField(max_length = 255)
	deathnote_read = models.TextField()
	iv_read = models.CharField(max_length = 255)
