#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: prs_server.py
@time: 2025/7/28 15:37
@project: prep-study-assistant
@desc: 后端项目启动入口代码
"""
import logging

from api import settings, utils
from api.utils import show_configs
from api.utils.log_utils import initRootLogger

initRootLogger("prep-study-assistant")

logging.info(r"""
______               _____ _             _          ___          _     _              _   
| ___ \             /  ___| |           | |        / _ \        (_)   | |            | |  
| |_/ / __ ___ _ __ \ `--.| |_ _   _  __| |_   _  / /_\ \___ ___ _ ___| |_ __ _ _ __ | |_ 
|  __/ '__/ _ \ '_ \ `--. \ __| | | |/ _` | | | | |  _  / __/ __| / __| __/ _` | '_ \| __|
| |  | | |  __/ |_) /\__/ / |_| |_| | (_| | |_| | | | | \__ \__ \ \__ \ || (_| | | | | |_ 
\_|  |_|  \___| .__/\____/ \__|\__,_|\__,_|\__, | \_| |_/___/___/_|___/\__\__,_|_| |_|\__|
              | |                           __/ |                                         
              |_|                          |___/   

""")

logging.info(
    f'project base: {utils.file_utils.get_project_base_directory()}'
)

show_configs()
settings.init_settings()
