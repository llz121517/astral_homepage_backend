# app/main.py
from fastapi import FastAPI


app = FastAPI(
    title="Astral's Homepage",
    description="A simple personal homepage backend.",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {"message": "Hello from Astral's backend!"}