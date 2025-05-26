from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from jose import JWTError, jwt
from bson import ObjectId
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["voyageconnect"]
posts = db["posts"]

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tajna123")
ALGORITHM = "HS256"
security = HTTPBearer()

# modeli
class PostIn(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    destination_id: str

class PostOut(PostIn):
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

@app.get("/", tags=["Health"])
def root():
    return {"message": "Post service je live"}


@app.get("/posts", response_model=List[PostOut], tags=["Posts"])
async def get_posts(destination_id: Optional[str] = None):
    query = {"destination_id": destination_id} if destination_id else {}
    docs = await posts.find(query).to_list(100)
    return [
        {
            "id": str(p["_id"]),
            "title": p["title"],
            "content": p["content"],
            "image_url": p.get("image_url"),
            "destination_id": p["destination_id"],
            "created_by": p["created_by"],
            "created_at": p["created_at"]
        }
        for p in docs
    ]

@app.post("/posts", response_model=PostOut, tags=["Posts"])
async def create_post(post: PostIn, user: str = Depends(get_current_user)):
    doc = {
        **post.model_dump(),
        "created_by": user,
        "created_at": datetime.utcnow()
    }
    result = await posts.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@app.get("/posts/{id}", response_model=PostOut, tags=["Posts"])
async def get_post(id: str):
    try:
        post = await posts.find_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Nevažeći ID format")
    if not post:
        raise HTTPException(status_code=404, detail="Post nije pronađen")
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "image_url": post.get("image_url"),
        "destination_id": post["destination_id"],
        "created_by": post["created_by"],
        "created_at": post["created_at"]
    }
