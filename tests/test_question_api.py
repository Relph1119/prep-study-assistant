"""题目生成接口单元测试"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestQuestionAPI:
    """题目生成接口测试类"""
    
    def test_generate_questions_success(self):
        """测试正常请求返回 200"""
        request_data = {
            "knowledge_points": ["Python基础语法", "数据类型"]
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # 验证响应结构
        assert response_data["success"] is True
        assert "message" in response_data
        assert "data" in response_data
        assert len(response_data["data"]) == 2
        
        # 验证题目结构
        question = response_data["data"][0]
        assert "question" in question
        assert "options" in question
        assert "correct_answer" in question
        assert "explanation" in question
        assert "knowledge_point" in question
        
        # 验证选项结构
        options = question["options"]
        assert len(options) == 4
        for option in options:
            assert "label" in option
            assert "content" in option
            assert option["label"] in ["A", "B", "C", "D"]
        
        # 验证正确答案在选项中
        correct_labels = [opt["label"] for opt in options]
        assert question["correct_answer"] in correct_labels
    
    def test_generate_questions_empty_knowledge_points(self):
        """测试输入为空时返回 422"""
        request_data = {
            "knowledge_points": []
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_generate_questions_missing_knowledge_points(self):
        """测试缺少 knowledge_points 字段时返回 422"""
        request_data = {}
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_generate_questions_too_many_knowledge_points(self):
        """测试知识点数量超过限制时返回 422"""
        request_data = {
            "knowledge_points": [f"知识点{i}" for i in range(11)]
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_generate_questions_empty_string_knowledge_point(self):
        """测试包含空字符串知识点时返回 422"""
        request_data = {
            "knowledge_points": ["Python基础语法", "", "数据类型"]
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_generate_questions_single_knowledge_point(self):
        """测试单个知识点生成题目"""
        request_data = {
            "knowledge_points": ["Python基础语法"]
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["success"] is True
        assert len(response_data["data"]) == 1
        assert response_data["data"][0]["knowledge_point"] == "Python基础语法"
    
    def test_generate_questions_unknown_knowledge_point(self):
        """测试未知知识点生成通用题目"""
        request_data = {
            "knowledge_points": ["未知知识点测试"]
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["success"] is True
        assert len(response_data["data"]) == 1
        question = response_data["data"][0]
        assert "未知知识点测试" in question["question"]
        assert question["correct_answer"] == "A"
    
    def test_generate_questions_response_structure(self):
        """测试响应字段完整且结构正确"""
        request_data = {
            "knowledge_points": ["函数定义"]
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # 验证顶级字段
        required_fields = ["success", "message", "data"]
        for field in required_fields:
            assert field in response_data
        
        # 验证题目字段
        question = response_data["data"][0]
        required_question_fields = ["question", "options", "correct_answer", "explanation", "knowledge_point"]
        for field in required_question_fields:
            assert field in question
            assert isinstance(question[field], str) if field != "options" else True
        
        # 验证选项字段
        for option in question["options"]:
            required_option_fields = ["label", "content"]
            for field in required_option_fields:
                assert field in option
                assert isinstance(option[field], str)
    
    def test_root_endpoint(self):
        """测试根路径接口"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json() == {"message": "备考学习助手 API"}
    
    def test_docs_endpoint(self):
        """测试文档接口可访问"""
        response = client.get("/docs")
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])
