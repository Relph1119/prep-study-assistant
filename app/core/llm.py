"""LLM Mock 实现 - 模拟硅基流动 LLM 返回"""

import random
from typing import Dict, List, Any
from app.schemas.question import Question, Option


class MockLLM:
    """Mock LLM 类，用于模拟硅基流动 LLM 返回结构化题目数据"""
    
    def __init__(self):
        # 预定义的题目模板库
        self.question_templates = {
            "Python基础语法": [
                {
                    "question": "Python是什么类型的语言？",
                    "options": [
                        {"label": "A", "content": "编译型语言"},
                        {"label": "B", "content": "解释型语言"},
                        {"label": "C", "content": "汇编语言"},
                        {"label": "D", "content": "机器语言"}
                    ],
                    "correct_answer": "B",
                    "explanation": "Python是一种解释型语言，代码在运行时由解释器逐行执行。"
                },
                {
                    "question": "Python中用来表示注释的符号是什么？",
                    "options": [
                        {"label": "A", "content": "//"},
                        {"label": "B", "content": "#"},
                        {"label": "C", "content": "/* */"},
                        {"label": "D", "content": "--"}
                    ],
                    "correct_answer": "B",
                    "explanation": "Python使用#符号来表示单行注释，多行注释使用三引号。"
                }
            ],
            "数据类型": [
                {
                    "question": "Python中下列哪个是不可变数据类型？",
                    "options": [
                        {"label": "A", "content": "列表"},
                        {"label": "B", "content": "字典"},
                        {"label": "C", "content": "元组"},
                        {"label": "D", "content": "集合"}
                    ],
                    "correct_answer": "C",
                    "explanation": "元组是不可变数据类型，一旦创建就不能修改其内容。"
                },
                {
                    "question": "Python中用于判断变量类型的函数是？",
                    "options": [
                        {"label": "A", "content": "type()"},
                        {"label": "B", "content": "typeof()"},
                        {"label": "C", "content": "isinstance()"},
                        {"label": "D", "content": "dtype()"}
                    ],
                    "correct_answer": "A",
                    "explanation": "type()函数用于返回变量的数据类型，isinstance()用于判断变量是否为指定类型。"
                }
            ],
            "函数定义": [
                {
                    "question": "Python中定义函数使用哪个关键字？",
                    "options": [
                        {"label": "A", "content": "function"},
                        {"label": "B", "content": "def"},
                        {"label": "C", "content": "func"},
                        {"label": "D", "content": "define"}
                    ],
                    "correct_answer": "B",
                    "explanation": "Python使用def关键字来定义函数，格式为：def function_name(parameters):"
                }
            ],
            "循环结构": [
                {
                    "question": "Python中for循环的基本语法是？",
                    "options": [
                        {"label": "A", "content": "for i in range(10)"},
                        {"label": "B", "content": "for i = 0 to 10"},
                        {"label": "C", "content": "for i in 0..10"},
                        {"label": "D", "content": "for(i=0; i<10; i++)"}
                    ],
                    "correct_answer": "A",
                    "explanation": "Python的for循环使用 for variable in iterable 的语法结构。"
                }
            ]
        }
    
    def generate_question(self, knowledge_point: str) -> Question:
        """
        根据知识点生成题目
        
        Args:
            knowledge_point: 知识点字符串
            
        Returns:
            Question: 生成的题目对象
        """
        # 如果有预定义模板，随机选择一个
        if knowledge_point in self.question_templates:
            template = random.choice(self.question_templates[knowledge_point])
        else:
            # 如果没有预定义模板，生成通用题目
            template = self._generate_generic_question(knowledge_point)
        
        # 创建选项对象
        options = [
            Option(label=opt["label"], content=opt["content"])
            for opt in template["options"]
        ]
        
        # 创建题目对象
        question = Question(
            question=template["question"],
            options=options,
            correct_answer=template["correct_answer"],
            explanation=template["explanation"],
            knowledge_point=knowledge_point
        )
        
        return question
    
    def _generate_generic_question(self, knowledge_point: str) -> Dict[str, Any]:
        """为未知知识点生成通用题目模板"""
        return {
            "question": f"关于{knowledge_point}，下列说法哪个是正确的？",
            "options": [
                {"label": "A", "content": f"{knowledge_point}是编程的基础概念"},
                {"label": "B", "content": f"{knowledge_point}不需要掌握"},
                {"label": "C", "content": f"{knowledge_point}已经过时"},
                {"label": "D", "content": f"{knowledge_point}只适用于高级开发"}
            ],
            "correct_answer": "A",
            "explanation": f"{knowledge_point}是编程学习中的重要知识点，需要认真理解和掌握。"
        }


# 创建全局 LLM 实例
mock_llm = MockLLM()
