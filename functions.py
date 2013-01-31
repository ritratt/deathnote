from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pbkdf2 import PBKDF2
import random
import string
import redis
from userdata.models import Deathbook

	
def generatekey(password, IV):
   		key = PBKDF2(password, IV).read(32)
        	return key

def encipher(mode, user_email, note, password):
	
	#Encrypt note.
	if mode == 'write':
		iv = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
		key = generatekey(password, iv)
		cipher = AES.new(key, AES.MODE_CFB, iv)
		encrypted_note = cipher.encrypt(note)
		encrypted_note = encrypted_note.encode('base64')
		
		#Write encrypted_note to disk.
		note_write_set(user_email, encrypted_note, iv)
		salt = random.randint(0,2**60)
		password_hash = SHA256.new(str(hex(salt)) + password).hexdigest()
		
		
		#write the hash somewhere along with IV for user authentication.
		write_set(user_email, password_hash, salt)

		#Second encryption to enable bereaved to view deathnote.
		ascii_printable = list(string.letters + string.digits + '`~!@#$%^&*()-_=+[{]}\|;:''",<.>/?')
		password_read = ''.join(random.choice(ascii_printable) for i in range(32))
		iv_read = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
		key_read = generatekey(password_read, iv_read)
		cipher_read = AES.new(key_read, AES.MODE_CFB, iv_read)
		encrypted_note_read =  cipher_read.encrypt(note)
		encrypted_note_read = encrypted_note_read.encode('base64')
	
	elif mode == 'read':
		temp_row = Deathbook.objects.get(user_email = user_email)
			
	#Key for bereaved. Hash it for storing in database.
	if mode == 'edit':
		temp_row = Deathbook.objects.get(user_email = user_email)
		piece_hash = temp_row.piece_hash
	elif mode == 'write':
		piece = iv_read + password_read
		piece_hash = SHA256.new(piece).hexdigest()

	#Write encrypted_note_read to disk.
	note_read_set(user_email, encrypted_note_read, piece_hash, iv_read)

	userdata_row = Deathbook(user_email = user_email, deathnote_write = encrypted_note, iv_write = iv,deathnote_read = encrypted_note_read, iv_read = iv_read, piece_hash = piece_hash)
	userdata_row.save()

	#Return piece to display on webpage.
	if mode == 'write':
		return piece
	elif mode == 'edit':
		return encrypted_note
			

def decipher(mode, user_email, password):
	if mode == 'write':
		userdata_row = Deathbook.objects.get(user_email = user_email)
		encrypted_note_write = userdata_row.deathnote_write
		encrypted_note_write = encrypted_note_write.decode('base64')
		iv_write = userdata_row.iv_write
		key = generatekey(password, iv_write)
		cipher = AES.new(key, AES.MODE_CFB, iv_write)
		decrypted_note = cipher.decrypt(encrypted_note_write)
		return decrypted_note
		
	elif mode == 'read':
		userdata_row = Deathbook.objects.get(user_email = user_email)
		piece_hash = userdata_row.piece_hash
		hash_tocheck = SHA256.new(password).hexdigest()
		if not hash_tocheck == piece_hash:
			return False
		encrypted_note_read = userdata_row.deathnote_read
		encrypted_note_read = encrypted_note_read.decode('base64')
		iv_read = userdata_row.iv_read
		key = generatekey(password[16:], iv_read)
		print password[16:]
		cipher = AES.new(key, AES.MODE_CFB, iv_read)
		decrypted_note = cipher.decrypt(encrypted_note_read)
		return decrypted_note

def write_set(user_email, pwd_hsh , salt):
	db_write_set = redis.StrictRedis(host='localhost', port=6379, db=1)
	db_write_set.rpush(user_email, pwd_hsh, salt)

def write_get(user_email):
	db_write_get = redis.StrictRedis(host = 'localhost', port = 6379, db = 1)
	return db_write_get.lrange(user_email, 0, -1)
	
def note_write_set(user_email, encrypted_note, iv):
	db_note_read_set = redis.StrictRedis(host='localhost', port=6379, db = 2)
	if write_get(user_email):
		db_note_read_set.lset(user_email, 0, encrypted_note)
		db_note_read_set.lset(user_email, 1, iv)
	else:
		db_note_read_set.rpush(user_email, encrypted_note, iv)

def note_write_get(user_email):
	db_note_write_get = redis.StrictRedis(host = 'localhost', port = 6379, db = 2)
	return db_note_write_get.lrange(user_email, 0, -1)

def note_read_set(user_email, encrypted_note, piece_hash, iv_read):
	db_note_read_set = redis.StrictRedis(host='localhost', port=6379, db = 3)
	if note_read_get(user_email):
		db_note_read_set.lset(user_email, 0, encrypted_note)
		db_note_read_set.lset(user_email, 1, piece_hash)
		db_note_read_set.lset(user_email, 2, iv_read)
	else:
		db_note_read_set.rpush(user_email, encrypted_note, piece_hash, iv_read)

def note_read_get(user_email):
	db_note_read_get = redis.StrictRedis(host = 'localhost', port = 6379, db = 3)
	return db_note_read_get.lrange(user_email, 0, -1)
