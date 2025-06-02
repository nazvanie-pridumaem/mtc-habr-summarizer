from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from src.parser import parse_article
from pydantic import BaseModel

app = FastAPI()

class Link(BaseModel):
    link: str

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI backend!"}

@app.post("/summarize")
async def summarize(link: Link):
    response = parse_article(link.link)

    if response:
        return JSONResponse(content=response, status_code=200)
    else:
        return JSONResponse(content=response, status_code=400)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)