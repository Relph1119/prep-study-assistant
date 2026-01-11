"""题目生成接口层"""

from fastapi import APIRouter, HTTPException
from app.schemas.question import QuestionGenerateRequest, QuestionGenerateResponse
from app.services.question_service import question_service

router = APIRouter()


@router.post("/questions/generate", response_model=QuestionGenerateResponse)
async def generate_questions(request: QuestionGenerateRequest):
    """
    根据知识点生成题目接口
    
    - **knowledge_points**: 知识点列表，1-10个知识点
    
    返回为每个知识点生成的选择题，包含题目、选项、正确答案和解析。
    """
    try:
        # 调用服务层生成题目
        response = question_service.generate_questions(request)
        
        # 如果生成失败，返回 HTTP 错误
        if not response.success:
            raise HTTPException(status_code=500, detail=response.message)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
