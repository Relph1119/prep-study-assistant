## outline_pdf2md
import os
import re
import json
from openai import OpenAI

# =================================================================
# 1. 路径锁定与环境配置 (最高优先级)
# =================================================================
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
current_dir = os.path.dirname(os.path.abspath(__file__))
custom_model_root = os.path.join(current_dir, "models")
if not os.path.exists(custom_model_root): os.makedirs(custom_model_root)

# Pix2Text 模型路径
os.environ["PIX2TEXT_HOME"] = os.path.join(custom_model_root, "pix2text")
os.environ["CNOCR_HOME"] = os.path.join(custom_model_root, "cnocr")
os.environ["CNSTD_HOME"] = os.path.join(custom_model_root, "cnstd")

# =================================================================
# 2. Ollama 本地客户端配置
# =================================================================
client = OpenAI(
    base_url='http://127.0.0.1:11434/v1',
    api_key='ollama', # 本地调用不需要 Key
    timeout=60.0
)

class OllamaMathExtractor:
    def __init__(self, model_name="qwen2.5:7b"):
        self.model_name = model_name

    def decompose_sentence(self, text):
        """
        调用本地 LLM 识别语义并拆分为原子 JSON
        """
        # 注意：Prompt 中 JSON 格式必须使用双大括号 {{ }} 转义
        prompt = f"""你是一位专业的数学教育专家。请将输入的考试要求文本拆解为原子化的知识点。
要求：
1. 识别“掌握程度词汇”作为 'familiarity'（如：理解、掌握、会建立、会求等）。
2. 识别“知识点对象”作为 'content'。
3. 严格输出 JSON 数组格式，不要包含任何多余的开场白。

输入示例：理解函数的概念，掌握函数的表示法。
输出示例：[{{"content": "函数的概念", "familiarity": "理解"}}, {{"content": "函数的表示法", "familiarity": "掌握"}}]

待处理文本：{text}"""

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            raw_content = response.choices[0].message.content.strip()
            # 清理可能的 Markdown 代码块标记
            raw_content = re.sub(r'```json\s*|\s*```', '', raw_content)
            return json.loads(raw_content)
        except Exception as e:
            print(f"      [!] 语义解析失败: {e}")
            return []

    def process_markdown_to_atomic(self, md_path, output_json):
        """
        解析 Markdown 并生成符合你要求的 JSON 结构
        """
        if not os.path.exists(md_path):
            print(f"[-] 错误：未找到文件 {md_path}")
            return

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. 提取文件名作为一级标题 (H1)
        file_match = re.search(r'^#\s*(.*)', content)
        filename = file_match.group(1).strip() if file_match else "Unknown"

        # 2. 按二级标题（章）切割内容
        chapters = re.split(r'\n(?=## )', content)
        
        final_list = []
        global_id = 1

        print(f"[*] 正在为文档 [{filename}] 进行语义原子化处理...")

        for ch in chapters:
            ch = ch.strip()
            if not ch or ch.startswith("# "): continue
            
            # 提取章名和 ID
            ch_lines = ch.split('\n')
            chapter_name = ch_lines[0].replace("## ", "").strip()
            
            # 找到该章下的正文或三级标题
            # 逻辑：找出所有以数字序号（如 1.）开头或者是三级标题（###）的内容
            lines_to_process = []
            for line in ch_lines[1:]:
                # 匹配：1. 这种格式 或者 ### 这种格式
                if re.match(r'^\d+[\.、．]', line.strip()) or line.startswith("### "):
                    lines_to_process.append(line.strip())

            for line in lines_to_process:
                # 去掉三级标题或序号标记
                clean_text = re.sub(r'^(### |\d+[\.、．]\s*)', '', line)
                print(f"    - 处理中: {clean_text[:20]}...")

                # 调用 Ollama 语义识别
                atomic_items = self.decompose_sentence(clean_text)

                for item in atomic_items:
                    # 组装最终你要求的格式
                    final_list.append({
                        "id": global_id,
                        "content": item.get('content', ''),
                        "familiarity": item.get('familiarity', ''),
                        "source_chapter": chapter_name
                    })
                    global_id += 1

        # 保存结果
        with open(output_json, "w", encoding="utf-8") as f_out:
            json.dump(final_list, f_out, ensure_ascii=False, indent=4)

        print(f"\n[+] 处理成功！生成了 {len(final_list)} 条知识点。")
        print(f"[+] 结果保存在: {output_json}")

   