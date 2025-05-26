from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from jose import JWTError, jwt
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os

# Init FastAPI
app = FastAPI()

# MongoDB konekcija
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["voyageconnect"]
destination_collection = db["destinations"]

# JWT konfiguracija
from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from jose import JWTError, jwt
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os

# Init FastAPI
app = FastAPI()

# MongoDB konekcija
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["voyageconnect"]
destination_collection = db["destinations"]

# JWT konfiguracija
SECRET_KEY = os.getenv("SECRET_KEY", "tajna123")
ALGORITHM = "HS256"
security = HTTPBearer()


# Pydantic modeli
class DestinationIn(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None  # može bit null

class DestinationOut(DestinationIn):
    id: str
    created_by: str
    created_at: datetime

# JWT verifikacija
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token")


# GET za sve destinacije
@app.get("/destinations", response_model=List[DestinationOut])
async def get_destinations():
    destinations = await destination_collection.find().to_list(100)
    return [
        {
            "id": str(d["_id"]),
            "name": d["name"],
            "description": d["description"],
            "image_url": d.get("image_url"),
            "created_by": d["created_by"],
            "created_at": d["created_at"],
        }
        for d in destinations
    ]

# POST  za novu destinaciju
@app.post("/destinations", response_model=DestinationOut)
async def create_destination(data: DestinationIn, user: str = Depends(get_current_user)):
    new_dest = {
        "name": data.name,
        "description": data.description,
        "image_url": data.image_url,
        "created_by": user,
        "created_at": datetime.utcnow()
    }
    result = await destination_collection.insert_one(new_dest)
    new_dest["id"] = str(result.inserted_id)
    return new_dest

# GET destinacija po IDju
@app.get("/destinations/{id}", response_model=DestinationOut)
async def get_destination(id: str):
    from bson import ObjectId
    try:
        dest = await destination_collection.find_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return {
        "id": str(dest["_id"]),
        "name": dest["name"],
        "description": dest["description"],
        "image_url": dest.get("image_url"),
        "created_by": dest["created_by"],
        "created_at": dest["created_at"],
    }

@app.get("/")
def root():
    return {"message": "Destination service je live"}
ALGORITHM = "HS256"

# Pydantic modeli
class DestinationIn(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None  # može bit null

class DestinationOut(DestinationIn):
    id: str
    created_by: str
    created_at: datetime

# JWT verifikacija
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token")


# GET za sve destinacije
@app.get("/destinations", response_model=List[DestinationOut])
async def get_destinations():
    destinations = await destination_collection.find().to_list(100)
    return [
        {
            "id": str(d["_id"]),
            "name": d["name"],
            "description": d["description"],
            "image_url": d.get("image_url"),
            "created_by": d["created_by"],
            "created_at": d["created_at"],
        }
        for d in destinations
    ]

# POST  za novu destinaciju
@app.post("/destinations", response_model=DestinationOut)
async def create_destination(data: DestinationIn, user: str = Depends(get_current_user)):
    new_dest = {
        "name": data.name,
        "description": data.description,
        "image_url": data.image_url,
        "created_by": user,
        "created_at": datetime.utcnow()
    }
    result = await destination_collection.insert_one(new_dest)
    new_dest["id"] = str(result.inserted_id)
    return new_dest

# GET destinacija po IDju
@app.get("/destinations/{id}", response_model=DestinationOut)
async def get_destination(id: str):
    from bson import ObjectId
    try:
        dest = await destination_collection.find_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return {
        "id": str(dest["_id"]),
        "name": dest["name"],
        "description": dest["description"],
        "image_url": dest.get("image_url"),
        "created_by": dest["created_by"],
        "created_at": dest["created_at"],
    }

@app.get("/")
def root():
    return {"message": "Destination service je live"}
