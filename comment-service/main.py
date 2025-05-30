from fastapi import FastAPI, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime
import os

app = FastAPI()

# Konfiguracija
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
SECRET_KEY = os.getenv("SECRET_KEY", "velikitajnikljuckojitrebapromjenit")
ALGORITHM = "HS256"

client = AsyncIOMotorClient(MONGO_URL)
db = client.voyageconnect

security = HTTPBearer()

# Pydantic modeli
class CommentIn(BaseModel):
    post_id: str = Field(...)
    content: str = Field(...)
    parent_id: Optional[str] = None  # za odgovore na komentare

class CommentOut(CommentIn):
    id: str
    created_by: str
    created_at: datetime

# JWT tokn
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

@app.post("/comments", response_model=CommentOut)
async def create_comment(comment: CommentIn, user_email: str = Depends(get_current_user)):
    new_comment = comment.dict()
    new_comment.update({
        "created_by": user_email,
        "created_at": datetime.utcnow()
    })
    result = await db.comments.insert_one(new_comment)
    new_comment["id"] = str(result.inserted_id)
    return new_comment

@app.get("/comments", response_model=List[CommentOut])
async def get_comments(post_id: str = Query(...)):
    cursor = db.comments.find({"post_id": post_id})
    comments = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        comments.append(CommentOut(**doc))
    return comments

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

@app.get("/")
def read_root():
    instance = os.getenv("INSTANCE", "unknown")
    return {"message": f"Hello from comment-service instance " + instance}