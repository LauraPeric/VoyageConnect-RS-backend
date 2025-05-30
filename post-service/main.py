from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from jose import JWTError, jwt
from bson import ObjectId
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional
import sys

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

@app.get("/")
def read_root():
    instance = os.getenv("INSTANCE", "unknown")
    return {"message": f"Hello from post-service instance " + instance}

@app.get("/crash")
def crash():
    sys.exit(1)  # simulacija pada apl

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


@app.patch("/posts/{id}", response_model=PostOut, tags=["Posts"])
async def update_post(
    id: str = Path(...),
    post_update: PostIn = None,
    user_email: str = Depends(get_current_user)
):
    update_data = post_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    post = await db.posts.find_one({"_id": ObjectId(id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["created_by"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")

    await db.posts.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    updated_post = await db.posts.find_one({"_id": ObjectId(id)})
    updated_post["id"] = str(updated_post["_id"])
    return updated_post

@app.delete("/posts/{id}", status_code=204,  tags=["Posts"])
async def delete_post(
    id: str = Path(...),
    user_email: str = Depends(get_current_user)
):
    post = await db.posts.find_one({"_id": ObjectId(id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["created_by"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    await db.posts.delete_one({"_id": ObjectId(id)})
    return

@app.get("/health")
def health():
    return {"status": "ok"}