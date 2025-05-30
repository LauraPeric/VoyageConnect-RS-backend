from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from jose import JWTError, jwt
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from bson import ObjectId

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["voyageconnect"]
destination_collection = db["destinations"]

SECRET_KEY = os.getenv("SECRET_KEY", "tajna123")
ALGORITHM = "HS256"
security = HTTPBearer()

class DestinationIn(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None  # može biti null

class DestinationOut(DestinationIn):
    id: str
    created_by: str
    created_at: datetime

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
def read_root():
    instance = os.getenv("INSTANCE", "unknown")
    return {"message": f"Hello from destination-service instance {instance}"}

@app.get("/destinations", response_model=List[DestinationOut], tags=["Destinations"])
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

@app.post("/destinations", response_model=DestinationOut, tags=["Destinations"])
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

@app.get("/destinations/{id}", response_model=DestinationOut, tags=["Destinations"])
async def get_destination(id: str):
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

@app.get("/health")
def health():
    return {"status": "ok"}

