from fastapi import FastAPI, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime
from bson import ObjectId
import os

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
SECRET_KEY = os.getenv("SECRET_KEY", "velikitajnikljuckojitrebapromjenit")
ALGORITHM = "HS256"

client = AsyncIOMotorClient(MONGO_URL)
db = client.voyageconnect

security = HTTPBearer()

### MODELI

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

### AUTH

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

### ENDPOINTI

@app.post("/topics", response_model=TopicOut)
async def create_topic(topic: TopicIn, user: str = Depends(get_current_user)):
    data = topic.dict()
    data["created_by"] = user
    data["created_at"] = datetime.utcnow()
    result = await db.forum_topics.insert_one(data)
    data["id"] = str(result.inserted_id)
    return data

@app.get("/topics", response_model=List[TopicOut])
async def get_topics():
    cursor = db.forum_topics.find()
    topics = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        topics.append(TopicOut(**doc))
    return topics

@app.get("/topics/{id}", response_model=TopicOut)
async def get_topic(id: str):
    try:
        topic = await db.forum_topics.find_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Nevažeći ID format")
    if not topic:
        raise HTTPException(status_code=404, detail="Tema nije pronađena")
    topic["id"] = str(topic["_id"])
    return TopicOut(**topic)

@app.post("/messages", response_model=MessageOut)
async def post_message(message: MessageIn, user: str = Depends(get_current_user)):
    doc = message.dict()
    doc["created_by"] = user
    doc["created_at"] = datetime.utcnow()
    result = await db.forum_messages.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@app.get("/messages", response_model=List[MessageOut])
async def get_messages(topic_id: str = Query(...)):
    cursor = db.forum_messages.find({"topic_id": topic_id})
    results = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        results.append(MessageOut(**doc))
    return results

@app.get("/", tags=["Health"])
def root():
    return {"message": "forum service je live"}