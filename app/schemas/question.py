from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional


class QuestionGenerateRequest(BaseModel):
    """生成题目请求模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "knowledge_points": ["Python基础语法", "数据类型"]
            }
        }
    )
    
    knowledge_points: List[str] = Field(..., description="知识点列表", min_length=1, max_length=10)
    
    @field_validator('knowledge_points', mode='before')
    @classmethod
    def validate_knowledge_points(cls, v):
        """验证知识点列表中不包含空字符串"""
        if isinstance(v, list):
            for kp in v:
                if isinstance(kp, str) and not kp.strip():
                    raise ValueError("知识点不能为空字符串")
        return v


class Option(BaseModel):
    """选项模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "A",
                "content": "Python是一种编译型语言"
            }
        }
    )
    
    label: str = Field(..., description="选项标签，如 A、B、C、D")
    content: str = Field(..., description="选项内容")


class Question(BaseModel):
    """题目模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "Python是什么类型的语言？",
                "options": [
                    {"label": "A", "content": "编译型语言"},
                    {"label": "B", "content": "解释型语言"},
                    {"label": "C", "content": "汇编语言"},
                    {"label": "D", "content": "机器语言"}
                ],
                "correct_answer": "B",
                "explanation": "Python是一种解释型语言，代码在运行时由解释器逐行执行。",
                "knowledge_point": "Python基础语法"
            }
        }
    )
    
    question: str = Field(..., description="题目内容")
    options: List[Option] = Field(..., description="选项列表")
    correct_answer: str = Field(..., description="正确答案，如 A、B、C、D")
    explanation: str = Field(..., description="解析")
    knowledge_point: str = Field(..., description="对应的知识点")


class QuestionGenerateResponse(BaseModel):
    """生成题目响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "题目生成成功",
                "data": [
                    {
                        "question": "Python是什么类型的语言？",
                        "options": [
                            {"label": "A", "content": "编译型语言"},
                            {"label": "B", "content": "解释型语言"},
                            {"label": "C", "content": "汇编语言"},
                            {"label": "D", "content": "机器语言"}
                        ],
                        "correct_answer": "B",
                        "explanation": "Python是一种解释型语言，代码在运行时由解释器逐行执行。",
                        "knowledge_point": "Python基础语法"
                    }
                ]
            }
        }
    )
    
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: List[Question] = Field(..., description="生成的题目列表")
