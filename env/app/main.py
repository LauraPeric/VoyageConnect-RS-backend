from fastapi import FastAPI, HTTPException
from app.users import User, hash_password, verify_password, create_access_token, users_db
from datetime import timedelta

app = FastAPI()

# testni endpoint
@app.get("/")
async def root():
    return {"message": "Server radi!"}

# endpoint za registraciju korisnika
@app.post("/register")
async def register(user: User):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)

    users_db[user.email] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
    }
    return {"message": "User successfully registered"}

# endpoint za prijavu korisnika
@app.post("/login")
async def login(user: User):
    user_in_db = users_db.get(user.email)
    if not user_in_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # provjera lozinke
    if not verify_password(user.password, user_in_db["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # kreiranje JWT tokena
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))

    return {"access_token": access_token, "token_type": "bearer"}
