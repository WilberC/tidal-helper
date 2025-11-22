from passlib.context import CryptContext

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash = pwd_context.hash("testpassword")
    print(f"Successfully generated hash: {hash}")
    print("Verification successful")
except Exception as e:
    print(f"Verification failed: {e}")
