from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello from FastAPI backend!"}

app = FastAPI()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)