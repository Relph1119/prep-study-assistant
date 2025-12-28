import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# =================================================================
# 1. 环境与并发配置
# =================================================================
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 双 5090 建议设为 8 线程并发
CONCURRENT_TASKS = 8 

client = OpenAI(
    base_url='http://127.0.0.1:11434/v1', 
    api_key='ollama',
    timeout=300.0 
)

# =================================================================
# 2. 深度 LaTeX 修正与 Unicode 净化 (解决乱码与报错)
# =================================================================
def sanitize_for_md(text):
    if not text or not isinstance(text, str):
        return ""

    # 2.1 【核心修复】解决 UnicodeEncodeError
    # 强制将字符串转换为 utf-8 字节流并忽略掉非法的代理字符，再转回字符串
    text = text.encode('utf-8', 'ignore').decode('utf-8')

    # 2.2 还原物理层面的 Python 转义干扰
    escape_map = {
        '\f': r'\frac', '\t': r'\text', '\v': r'\vec', 
        '\a': r'\alpha', '\b': r'\boldsymbol', '\r': r'\rho'
    }
    for char, raw in escape_map.items():
        text = text.replace(char, raw)

    # 2.3 修正“缝合怪”乱码
    mangled_map = {
        r'\bigcupoldsymbol': r'\boldsymbol',
        r'\boldsymbolegin': r'\begin',
        r'\rhoightarrow': r'\rightarrow',
        r'\bigcu\pigcup': r'\bigcup',
        r'\bigcu\pigcap': r'\bigcap',
        r'\bigcu\pigg': r'\bigg',
        r'\bigcu\pig': r'\big',
        r'\fracrac': r'\frac',
        r'\textext': r'\text',
        r'\texto': r'\to',
        r'\bigcupar': r'\bar',
        r'\bigcupoxed': r'\boxed',
        r'\textimes': r'\times',
        r'\tex\theta': r'\theta',
        r'\fracorall': r'\forall',
        r'\rhoho': r'\rho',
    }
    for mangled, correct in mangled_map.items():
        text = text.replace(mangled, correct)

    # 2.4 修复变量粘连 (如 \boldsymbolx -> \boldsymbol{x})
    text = re.sub(r'\\boldsymbol([a-zA-Z])', r'\\boldsymbol{\1}', text)

    # 2.5 统一包裹定界符
    text = text.replace('$', '').strip()
    if '\\' in text or '^' in text or '_' in text:
        # 长公式或含换行用块级，短内容用行内
        if len(text) > 50 or '\n' in text or 'begin{' in text:
            return f"\n$$\n{text}\n$$\n"
        else:
            return f"${text}$"
    
    return text

# =================================================================
# 3. 命题引擎类 (支持保序)
# =================================================================
class OrderedExamGenerator:
    def __init__(self, model_name="qwen2.5:7b"):
        self.model_name = model_name
        self.SKIP_KEYWORDS = ["常见题型", "基本概念", "概述", "引言", "小结", "练习", "考试大纲"]

    def _should_skip(self, item):
        name = item.get('knowledge_name', '')
        content = item.get('knowledge_content', '')
        if any(kw in name for kw in self.SKIP_KEYWORDS): return True
        if len(content.strip()) < 15: return True
        return False

    def llm_worker(self, index, item):
        """ 记录 index 用于最后排序 """
        prompt = f"""你是一位享誉国际的特级教师。请基于资料进行出题。
【知识点】：{item['knowledge_name']} | 难度：{item['difficulty_level']}
【内容摘要】：{item['knowledge_content'][:1200]}

任务：
1. 识别并纠正 OCR 错误。
2. 识别学科，出一道符合等级要求的题目。
3. 必须提供【答案】和【详细解析】。
4. 严格输出 JSON：{{"subject":"","polished_name":"","question":"","answer":"","analysis":""}}
"""
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            raw = json.loads(response.choices[0].message.content)
            
            return {
                "idx": index,
                "name": sanitize_for_md(raw.get('polished_name', item['knowledge_name'])).replace('$', ''),
                "subject": raw.get('subject', '通用'),
                "level": item['difficulty_level'],
                "q": sanitize_for_md(raw.get('question', '')),
                "a": sanitize_for_md(raw.get('answer', '')),
                "ana": "\n".join([sanitize_for_md(l) for l in raw.get('analysis', '').split('\n')])
            }
        except:
            return None

    def run(self, input_json, output_md):
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        tasks = [(i, item) for i, item in enumerate(data) if not self._should_skip(item)]
        total = len(tasks)
        
        print(f"[*] 🚀 5090 保序模式启动 | 任务数: {total} | 并发数: {CONCURRENT_TASKS}")
        
        start_time = time.time()
        results_pool = []

        with ThreadPoolExecutor(max_workers=CONCURRENT_TASKS) as executor:
            future_to_idx = {executor.submit(self.llm_worker, idx, item): idx for idx, item in tasks}
            
            completed = 0
            for future in as_completed(future_to_idx):
                completed += 1
                res = future.result()
                if res:
                    results_pool.append(res)
                print(f"[{completed}/{total}] 处理完成 (正在同步排序...)")

        # 核心：按原始索引排序，保证章节不乱
        results_pool.sort(key=lambda x: x['idx'])

        # 4. 最终写入 (解决 UnicodeEncodeError)
        print("[*] 正在生成最终 Markdown 文档...")
        md_body = [f"# 🎓 结构化智能精品题库: {os.path.basename(input_json)}\n", f"> 题目总数: {len(results_pool)} 道 | 双 5090 并发模式\n\n---\n\n"]
        
        for i, r in enumerate(results_pool):
            md_body.append(f"## [{i+1}] {r['name']}\n")
            md_body.append(f"> **学科分类**：{r['subject']}  |  **难度等级**：{r['level']}\n\n")
            md_body.append(f"### 📝 题目描述\n{r['q']}\n\n")
            md_body.append(f"### ✅ 正确答案\n**{r['a']}**\n\n")
            md_body.append(f"### 🔍 详解与解析\n{r['ana']}\n\n")
            md_body.append("---\n\n")

        # 【重点】写入时增加 errors='replace'，作为第二重保险
        with open(output_md, 'w', encoding='utf-8', errors='replace') as f_out:
            f_out.write("".join(md_body))
        
        duration = round(time.time() - start_time, 2)
        print(f"\n[+] 导出圆满完成！")
        print(f"    - 总耗时: {duration} 秒")
        print(f"    - 结果文件: {output_md}")
