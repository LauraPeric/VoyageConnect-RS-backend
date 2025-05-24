
from fastapi import FastAPI, HTTPException
import os

app = FastAPI()

@app.get("/")
def read_root():
    instance = os.getenv("INSTANCE", "unknown")
    return { "message": f"Hello from post-service instance " + instance }
