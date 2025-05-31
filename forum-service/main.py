from fastapi import FastAPI, Depends, HTTPException, status, Query, Path 
from pydantic import BaseModel, Field
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime
from bson import ObjectId
import os
import sys

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
SECRET_KEY = os.getenv("SECRET_KEY", "velikitajnikljuckojitrebapromjenit")
ALGORITHM = "HS256"

client = AsyncIOMotorClient(MONGO_URL)
db = client.voyageconnect

security = HTTPBearer()

class TopicIn(BaseModel):
    title: str
    description: str

class TopicOut(TopicIn):
    id: str
    created_by: str
    created_at: datetime

class MessageIn(BaseModel):
    topic_id: str
    content: str

class MessageOut(MessageIn):
    id: str
    created_by: str
    created_at: datetime

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")
        return user_email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")


@app.get("/")
def read_root():
    instance = os.getenv("INSTANCE", "unknown")
    return {"message": f"Hello from forum-service instance " + instance}

@app.get("/crash")
def crash():
    sys.exit(1)  # simulacija pada apl

@app.post("/topics", response_model=TopicOut, tags=["Topics"])
async def create_topic(topic: TopicIn, user: str = Depends(get_current_user)):
    data = topic.dict()
    data["created_by"] = user
    data["created_at"] = datetime.utcnow()
    result = await db.forum_topics.insert_one(data)
    data["id"] = str(result.inserted_id)
    return data

@app.get("/topics", response_model=List[TopicOut], tags=["Topics"])
async def get_topics():
    cursor = db.forum_topics.find()
    topics = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        topics.append(TopicOut(**doc))
    return topics

@app.get("/topics/{id}", response_model=TopicOut, tags=["Topics"])
async def get_topic(id: str):
    try:
        topic = await db.forum_topics.find_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Nevažeći ID format")
    if not topic:
        raise HTTPException(status_code=404, detail="Tema nije pronađena")
    topic["id"] = str(topic["_id"])
    return TopicOut(**topic)

@app.patch("/topics/{id}", response_model=TopicOut, tags=["Topics"])
async def update_topic(
    id: str = Path(...),
    topic_update: TopicIn = None,
    user_email: str = Depends(get_current_user)
):
    update_data = topic_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    topic = await db.forum_topics.find_one({"_id": ObjectId(id)})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if topic["created_by"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to edit this topic")

    await db.forum_topics.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    updated_topic = await db.forum_topics.find_one({"_id": ObjectId(id)})
    updated_topic["id"] = str(updated_topic["_id"])
    return updated_topic

@app.delete("/topics/{id}", status_code=204, tags=["Topics"])
async def delete_topic(
    id: str = Path(...),
    user_email: str = Depends(get_current_user)
):
    topic = await db.forum_topics.find_one({"_id": ObjectId(id)})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if topic["created_by"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this topic")

    await db.forum_topics.delete_one({"_id": ObjectId(id)})
    return

@app.post("/messages", response_model=MessageOut, tags=["Messages"])
async def post_message(message: MessageIn, user: str = Depends(get_current_user)):
    doc = message.dict()
    doc["created_by"] = user
    doc["created_at"] = datetime.utcnow()
    result = await db.forum_messages.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@app.get("/messages", response_model=List[MessageOut], tags=["Messages"])
async def get_messages(topic_id: str = Query(...)):
    cursor = db.forum_messages.find({"topic_id": topic_id})
    results = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        results.append(MessageOut(**doc))
    return results

@app.patch("/messages/{id}", response_model=MessageOut, tags=["Messages"])
async def update_message(
    id: str = Path(...),
    message_update: MessageIn = None,
    user_email: str = Depends(get_current_user)
):
    update_data = message_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    message = await db.forum_messages.find_one({"_id": ObjectId(id)})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message["created_by"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to edit this message")

    await db.forum_messages.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    updated_message = await db.forum_messages.find_one({"_id": ObjectId(id)})
    updated_message["id"] = str(updated_message["_id"])
    return updated_message

@app.delete("/messages/{id}", status_code=204, tags=["Messages"])
async def delete_message(
    id: str = Path(...),
    user_email: str = Depends(get_current_user)
):
    message = await db.forum_messages.find_one({"_id": ObjectId(id)})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message["created_by"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this message")

    await db.forum_messages.delete_one({"_id": ObjectId(id)})
    return

@app.get("/health")
def health():
    return {"status": "ok"}
