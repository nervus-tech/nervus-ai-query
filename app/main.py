from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Query Service"}

@app.get("/test")
def read_root():
    return {"message": "AI Query Service is running"}