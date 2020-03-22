import hashlib


class HashOperation():
    #Hash the password with the SHA256
    def hashBasedOnPassword(password):
        result = hashlib.sha256(password.encode()).digest()


        return result