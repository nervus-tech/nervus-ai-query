from fastapi import FastAPI
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models.query import Base, Query
from datetime import datetime

load_dotenv()
app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA_NAME = os.getenv("SCHEMA_NAME", "staging_ai_query")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        # Create schema if it doesn't exist
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        db.commit()
        
        # Set search path to use the schema
        db.execute(text(f"SET search_path TO {SCHEMA_NAME}"))
        db.commit()
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        # Check if data exists
        if db.query(Query).count() == 0:
            # Seed sample queries
            query1 = Query(query_text="What is AI?", response="AI is artificial intelligence.", timestamp=datetime.now())
            query2 = Query(query_text="How does machine learning work?", response="Machine learning involves training models.", timestamp=datetime.now())
            db.add(query1)
            db.add(query2)
            db.commit()
            print(f"Seeded 2 queries into {SCHEMA_NAME} schema")
        else:
            print(f"Queries already seeded in {SCHEMA_NAME} schema, skipping...")
        yield
    finally:
        db.close()

app = FastAPI(lifespan=lifespan)

async def startup_event():
    db = SessionLocal()
    try:
        # Create schema if it doesn't exist
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        db.commit()
        
        # Set search path to use the schema
        db.execute(text(f"SET search_path TO {SCHEMA_NAME}"))
        db.commit()
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        # Check if data exists
        if db.query(Query).count() == 0:
            # Seed sample queries
            query1 = Query(query_text="What is AI?", response="AI is artificial intelligence.", timestamp=datetime.now())
            query2 = Query(query_text="How does machine learning work?", response="Machine learning involves training models.", timestamp=datetime.now())
            db.add(query1)
            db.add(query2)
            db.commit()
            print(f"Seeded 2 queries into {SCHEMA_NAME} schema")
        else:
            print(f"Queries already seeded in {SCHEMA_NAME} schema, skipping...")
    finally:
        db.close()

@app.get("/test")
def read_root():
    return {"message": "AI Query Service is running"}