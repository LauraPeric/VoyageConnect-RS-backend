from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi

import os

# Init
app = FastAPI()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["voyageconnect"]
user_collection = db["users"]

# Hasiranje
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT konfiguracija
SECRET_KEY = os.getenv("SECRET_KEY", "tajna123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Pydantic modeli
class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    username: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

# Helperi
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# API

@app.get("/")
def read_root():
    instance = os.getenv("INSTANCE", "unknown")
    return {"message": f"Hello from auth-service instance " + instance}


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/register", response_model=UserOut)
async def register(user: UserIn):
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email već registriran")

    hashed_pwd = hash_password(user.password)
    user_doc = {**user.dict(), "password": hashed_pwd}
    await user_collection.insert_one(user_doc)

    return UserOut(username=user.username, email=user.email)

@app.post("/login", response_model=Token)
async def login(user: UserIn):
    user_doc = await user_collection.find_one({"email": user.email})
    if not user_doc or not verify_password(user.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": user_doc["email"]}
    token = create_access_token(token_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

security = HTTPBearer()

@app.get("/verify-token")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"email": user_email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="VoyageConnect API",
        version="1.0.0",
        description="API sa JWT autentifikacijom",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if "security" not in openapi_schema["paths"][path][method]:
                openapi_schema["paths"][path][method]["security"] = []
            # check ima li endpoint ima Depends(security)
            if "verify-token" in path or "some-secured-endpoint" in path:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
