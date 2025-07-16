from fastapi import FastAPI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Query Service"}

@app.get("/test")
def read_root():
    return {"message": "AI Query Service is running"}