from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pbkdf2 import PBKDF2
import random
import string
import redis


def generatekey(password,IV):
   		key = PBKDF2(password,IV).read(32)
        	return key

def encipher(mode, user_email, note, password):
	
	#Encrypt note.
	iv = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
        key = PBKDF2(password, iv).read(32)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        encrypted_note = cipher.encrypt(note)
	
	#Write encrypted_note to disk.
	note_write_set(user_email, encrypted_note, iv)
	salt = random.randint(0,2**60)
	password_hash = SHA256.new(str(hex(salt)) + password).hexdigest()
	
	#write the hash somewhere along with IV for user authentication.
	write_set(user_email, password_hash, salt)

	#Second encryption to enable bereaved to view deathnote.
	ascii_printable = list(string.printable)
	password_b = ''.join(random.choice(ascii_printable) for i in range(32))
	iv_b = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
	key_b = PBKDF2(password_b, iv_b).read(32)
	cipher_b = AES.new(key_b, AES.MODE_CFB, iv_b)
	encrypted_note_b =  cipher_b.encrypt(note)

	#Key for bereaved. Hash it for storing in database.
	piece = iv_b + password_b
	piece_hash = SHA256.new(piece).hexdigest()

	#Write encrypted_note_b to disk.
	store_b(user_email, encrypted_note_b, piece_hash)

	#Return piece to display on webpage.
	if mode == 'write':
		return piece
	elif mode == 'edit':
		return encrypted_note


def decipher(mode, user_email, password):
	if mode == 'write':
		retrieved_write_get = write_get(user_email)
		hash_correct = retrieved_write_get[0]
		salt = retrieved_write_get[1]
		hash_tocheck = SHA256.new(str(hex(int(salt))) + password).hexdigest() 
		if hash_tocheck == hash_correct:
			retrieved = note_write_get(user_email)
			encrypted_note = retrieved[0]
			iv = retrieved[1]
			key = generatekey(password, iv)
			cipher = AES.new(key, AES.MODE_CFB, iv)
			decrypted_note = cipher.decrypt(encrypted_note)
			return decrypted_note
		else:
			return False

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

def store_b(user_email, dnote, piece_hash):
	db_b = redis.StrictRedis(host='localhost', port=6379, db=3)
	db_b.set(user_email, [dnote, piece_hash, 'ALIVE'])

