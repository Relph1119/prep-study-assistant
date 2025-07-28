#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: settings.py
@time: 2025/7/28 15:22
@project: prep-study-assistant
@desc: 
"""
from openai import OpenAI
from dotenv import load_dotenv
from api.utils import get_base_config

databaseConn = None
CHAT_MDL = None
ADMIN_USER = None


def init_settings():
    global databaseConn, CHAT_MDL, ADMIN_USER

    # 加载环境变量
    load_dotenv(dotenv_path='.env')

    LLM = get_base_config("llm")
    api_key = LLM['api_key']

    # 基于openai初始化模型
    CHAT_MDL = OpenAI(
        api_key=api_key,
        base_url=LLM['model_url'],
    )
    ADMIN_USER = get_base_config("admin")
