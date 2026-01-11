from fastapi import FastAPI
from app.api.v1.question import router as question_router

app = FastAPI(
    title="备考学习助手",
    description="智能学习工具，提供题目生成等功能",
    version="1.0.0"
)

app.include_router(question_router, prefix="/api/v1", tags=["questions"])

@app.get("/")
async def root():
    return {"message": "备考学习助手 API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
