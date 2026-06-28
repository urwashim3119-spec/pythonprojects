print("*********PASSWORD GENERATOR**********")
import random
import string
length=int(input("Enter your password length:"))
char = string.ascii_letters+string.digits+string.punctuation

password=""

for i in range(length):
    password+=random.choice(char)
print("Generated password:",password)
