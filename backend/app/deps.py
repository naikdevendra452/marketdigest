import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pw(p:str)->str:
    return pwd_context.hash(p)

def verify_pw(p:str, hashed:str)->bool:
    return pwd_context.verify(p, hashed)
