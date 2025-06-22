import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    password = password.encode('utf-8')
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')

def check_password(input_password, stored_hash):
    input_password = input_password.encode('utf-8')
    stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(input_password, stored_hash)