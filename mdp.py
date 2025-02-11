from passlib.context import CryptContext


password_ctx = CryptContext(schemes=['bcrypt'])
hash_pw = password_ctx.hash("bondJ@mesb0nd")
print(hash_pw)

