from fastapi import FastAPI
from api.users import router as user_router

app = FastAPI(title="备考学习助手")

app.include_router(user_router)
