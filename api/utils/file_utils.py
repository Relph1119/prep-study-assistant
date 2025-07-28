#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: file_utils.py
@time: 2025/7/28 15:25
@project: prep-study-assistant
@desc: 
"""
import os

import yaml

PROJECT_BASE = os.getenv("PROJECT_BASE") or os.getenv("DEPLOY_BASE")


def get_project_base_directory(*args):
    global PROJECT_BASE
    if PROJECT_BASE is None:
        PROJECT_BASE = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                os.pardir,
                os.pardir,
            )
        )

    if args:
        return os.path.join(PROJECT_BASE, *args)
    return PROJECT_BASE


def load_yaml_conf(conf_path):
    if not os.path.isabs(conf_path):
        conf_path = os.path.join(get_project_base_directory(), conf_path)
    try:
        with open(conf_path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise EnvironmentError("loading yaml file config from {} failed:".format(conf_path), e)
