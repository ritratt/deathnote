from django.db import models

# Create your models here.
class Deathbook(models.Model):
	user_email = models.EmailField(primary_key = True, unique = True, error_messages = {'unique':'snbjusb'})

	#Fields for write access and operations.
	deathnote_write = models.TextField()
	iv_write = models.CharField(max_length = 255)

	#Fields for read access and operations.
	deathnote_read = models.TextField()
	iv_read = models.CharField(max_length = 255)
	piece_hash = models.CharField(max_length = 255)
	encrypted_piece = models.CharField(max_length = 255)
 
