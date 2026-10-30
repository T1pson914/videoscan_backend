from pwdlib import PasswordHash



password_manager = PasswordHash.recommended()



def hash_password(password: str) -> str:
    return password_manager.hash(password)



def verify_password(entered_password: str, saved_password: str) -> bool:
    return password_manager.verify(entered_password,saved_password)
