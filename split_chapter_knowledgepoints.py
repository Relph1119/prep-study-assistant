##contentmd2json
import json
import re
import os

def clean_prefix(text):
    """
    清洗标题前缀的函数。
    支持剔除：'一、', '1.1', '1.', '第1章', '(一)', '1、' 等。
    """
    # 1. 定义需要剔除的编号模式
    patterns = [
        r'^第[一二三四五六七八九十百\d]+[章节]\s*',        # 第1章, 第一节
        r'^[一二三四五六七八九十百]+[、，\.．\s]+',       # 一、, 十一、
        r'^\d+(\.\d+)*[、\.．\s]*',                      # 1.1, 1.2.1, 1.
        r'^\d+[、\.．\s]+',                             # 1、, 2 .
        r'^[(（][\d一二三四五六七八九十百]+[）)]\s*'      # (1), （一）
    ]
    
    result = text.strip()
    for p in patterns:
        result = re.sub(p, '', result)
    
    # 移除残留的起始空格或特殊冒号
    result = re.sub(r'^[：:\.\s]+', '', result)
    return result.strip()

def parse_md_to_pure_json(md_path, sections_output, knowledge_output):
    if not os.path.exists(md_path):
        print(f"[-] 错误：未找到文件 {md_path}")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 按照二级标题切割全文
    section_parts = re.split(r'\n(?=## )', content)
    
    sections_list = []
    knowledge_list = []
    
    k_id_counter = 1
    s_id_counter = 1

    print("\n[*] 开始解析结构并提取纯净知识点...")
    print("-" * 40)

    for part in section_parts:
        part = part.strip()
        if not part or part.startswith("# "): 
            continue

        # 提取二级标题名
        lines = part.split('\n')
        s_name_raw = lines[0].replace("## ", "").strip()
        
        # 存入章节列表（此处保留原始名，方便导航）
        sections_list.append({
            "section_id": s_id_counter,
            "section_name": s_name_raw
        })
        print(f"处理章节: {s_name_raw}")
        s_id_counter += 1

        # --- 分层判断逻辑 ---
        sub_parts = re.split(r'\n(?=### )', part)
        
        if len(sub_parts) > 1:
            # 情况 A: 存在三级标题，取三级标题内容
            for sub_block in sub_parts[1:]:
                sub_lines = sub_block.strip().split('\n')
                h3_title_raw = sub_lines[0].replace("### ", "").strip()
                
                # --- 核心改进：清洗三级标题名称 ---
                k_name_clean = clean_prefix(h3_title_raw)
                
                k_content = "\n".join(sub_lines[1:]).strip()
                
                knowledge_list.append({
                    "knowledge_id": k_id_counter,
                    "knowledge_name": k_name_clean,
                    "knowledge_content": self_clean_text(k_content)
                })
                k_id_counter += 1
        else:
            # 情况 B: 没有三级标题，取二级标题本身
            # --- 核心改进：清洗二级标题名称 ---
            k_name_clean = clean_prefix(s_name_raw)
            
            k_content = "\n".join(lines[1:]).strip()
            knowledge_list.append({
                "knowledge_id": k_id_counter,
                "knowledge_name": k_name_clean,
                "knowledge_content": self_clean_text(k_content)
            })
            k_id_counter += 1

    # 保存
    with open(sections_output, 'w', encoding='utf-8') as f1:
        json.dump(sections_list, f1, ensure_ascii=False, indent=4)
    
    with open(knowledge_output, 'w', encoding='utf-8') as f2:
        json.dump(knowledge_list, f2, ensure_ascii=False, indent=4)

    print("-" * 40)
    print(f"[+] 解析完成！")
    print(f"    - knowledge_points.json 中的名称已全部去前缀。")

def self_clean_text(text):
    """ 清除 MD 标记 """
    text = re.sub(r'---', '', text)
    text = re.sub(r'<!--.*?-->', '', text)
    return text.strip()

    