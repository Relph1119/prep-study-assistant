"""题目生成服务层"""

from typing import List
from app.schemas.question import Question, QuestionGenerateRequest, QuestionGenerateResponse
from app.core.llm import mock_llm


class QuestionService:
    """题目生成服务类"""
    
    def __init__(self):
        self.llm = mock_llm
    
    def generate_questions(self, request: QuestionGenerateRequest) -> QuestionGenerateResponse:
        """
        根据知识点生成题目
        
        Args:
            request: 生成题目请求对象
            
        Returns:
            QuestionGenerateResponse: 生成题目响应对象
        """
        try:
            questions = []
            
            # 为每个知识点生成一道题目
            for knowledge_point in request.knowledge_points:
                question = self.llm.generate_question(knowledge_point)
                questions.append(question)
            
            return QuestionGenerateResponse(
                success=True,
                message=f"成功为 {len(request.knowledge_points)} 个知识点生成题目",
                data=questions
            )
            
        except Exception as e:
            return QuestionGenerateResponse(
                success=False,
                message=f"生成题目失败: {str(e)}",
                data=[]
            )
    
    def validate_knowledge_points(self, knowledge_points: List[str]) -> bool:
        """
        验证知识点列表是否有效
        
        Args:
            knowledge_points: 知识点列表
            
        Returns:
            bool: 是否有效
        """
        if not knowledge_points:
            return False
        
        if len(knowledge_points) > 10:
            return False
        
        # 检查每个知识点是否为空字符串
        for kp in knowledge_points:
            if not kp or not kp.strip():
                return False
        
        return True


# 创建服务实例
question_service = QuestionService()
