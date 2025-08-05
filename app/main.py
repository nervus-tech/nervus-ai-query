from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models.query import Base, Query
from datetime import datetime
import logging
from .services.service_discovery import create_eureka_client

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA_NAME = os.getenv("SCHEMA_NAME", "staging_ai_query")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = logging.getLogger(__name__)

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

        # Register with Eureka and start heartbeat
        eureka_client = create_eureka_client()
        if eureka_client.register_with_eureka():
            eureka_client.start_heartbeat()

        yield
    finally:
        db.close()

app = FastAPI(lifespan=lifespan)

@app.get("/test")
def read_root():
    return {"message": "AI Query Service is running"}

@app.get("/health")
def health_check():
    return {"status": "UP", "service": "ai-query"}

@app.get("/actuator/health")
def actuator_health():
    return {"status": "UP"}