#xiuzheng
import os
import re
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# =================================================================
# 1. 环境配置 (针对双 5090 优化)
# =================================================================
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 并发数：根据 5090 性能，建议 6-8
CONCURRENT_TASKS = 6 

client = OpenAI(
    base_url='http://127.0.0.1:11434/v1', 
    api_key='ollama',
    timeout=300.0 
)

def heavy_clean_latex(text):
    """
    第一步：物理层面的硬性纠错（正则暴力清洗）
    专门解决 \[ \]、\( \) 以及重复拼接的 \fracrac 等问题
    """
    if not text: return ""

    # 1.1 修复常见的 LaTeX 定界符变体 (强制转为 $$ 和 $)
    # 使用 re.DOTALL 确保匹配跨行的公式块
    text = re.sub(r'\\\[\s*(.*?)\s*\\\]', r'\n$$\n\1\n$$\n', text, flags=re.DOTALL)
    text = re.sub(r'\\\( \s*(.*?)\s*\\\)', r' $\1$ ', text)

    # 1.2 修复“缝合怪”乱码与转义错误 (按长度倒序替换)
    corrections = {
        r'\textimes': r'\times',
        r'\fracrac': r'\frac',
        r'\textext': r'\text',
        r'\texto': r'\to',
        r'\bigcupoldsymbol': r'\boldsymbol',
        r'\boldsymbololdsymbol': r'\boldsymbol',
        r'\boldsymbolegin': r'\begin',
        r'old symbol': r'\boldsymbol',
        r'\rhoho': r'\rho',
        r'\tex\theta': r'\theta',
        r'\bigcupar': r'\bar',
        r'\bigcupoxed': r'\boxed',
        r'\bigcu\pigg': r'\bigg',
        r'\bigcu\pig': r'\big',
    }
    for mangled, correct in corrections.items():
        text = text.replace(mangled, correct)

    # 1.3 修复因 Python 转义导致丢失的斜杠 (针对 \f, \t, \b)
    # 注意：这里将 \b 映射回 \boldsymbol 防止误认
    text = text.replace('\f', r'\frac').replace('\t', r'\text').replace('\b', r'\boldsymbol')
    
    # 1.4 修复变量粘连问题 (如 \boldsymbolx -> \boldsymbol{x})
    text = re.sub(r'\\boldsymbol([a-zA-Z])', r'\\boldsymbol{\1}', text)

    return text

class Refiner:
    def __init__(self, model_name="qwen2.5:7b"):
        self.model_name = model_name

    def refine_with_qwen(self, block_text):
        """
        利用 Qwen 执行文数分离与排版优化
        """
        if len(block_text.strip()) < 10:
            return block_text

        # 提示词中增加了对 [ ] 和 ( ) 的明确禁止指令
        prompt = f"""你是一位享誉国际的数学教材编辑。请修正以下 Markdown 段落。

【修正准则】：
1. **文数分离**：严禁将文字内容、列表符号(-)、选项符号(A. B.)放在 $$ 内部。
2. **定界符规范**：
   - 必须使用 $...$ (行内) 或 $$...$$ (独立块)。
   - **严禁**使用 \\[ \\] 或 \\( \\) 这种 LaTeX 原生括号。
3. **符号纠错**：
   - 将 \\textimes 还原为 \\times。
   - 将 \\texto 还原为 \\to。
   - 修正所有 \\fracrac 类似的重复乱码。
4. **清理冗余**：删除所有无意义的 OCR 乱码字符。

【待处理片段】：
{block_text}

【要求】：直接输出修正后的 Markdown。不要输出任何开场白。
"""
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"\n> [!] 修复失败: {e}\n{block_text}"

    def run(self, input_md, output_md):
        if not os.path.exists(input_md):
            print(f"[-] 错误：找不到文件 {input_md}")
            return

        print(f"[*] 正在读取源文档并执行第一轮硬核清洗...")
        with open(input_md, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        # 1. 预清洗：解决物理乱码和定界符格式
        raw_text = heavy_clean_latex(raw_text)

        # 2. 智能切分数据块 (按 ## 标题切分，保证上下文逻辑)
        blocks = re.split(r'\n(?=## )|\n---\n', raw_text)
        total = len(blocks)
        
        print(f"[*] 🚀 5090 并发渲染引擎启动 | 块总数: {total}")
        
        fixed_blocks = [None] * total
        start_time = time.time()

        # 3. 并发调用 Qwen
        with ThreadPoolExecutor(max_workers=CONCURRENT_TASKS) as executor:
            future_to_idx = {executor.submit(self.refine_with_qwen, blocks[i]): i for i in range(total)}
            
            completed = 0
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                fixed_blocks[idx] = future.result()
                completed += 1
                # 打印简洁进度
                print(f"[{completed}/{total}] 修复完成: {idx+1} 号数据块")

        # 4. 最终合并：在合并前再次执行一遍物理纠错，确保 Qwen 的输出也符合标准
        print("[*] 正在执行最终对齐并写入文件...")
        final_content = "\n\n---\n\n".join([heavy_clean_latex(b) for b in fixed_blocks if b])

        with open(output_md, 'w', encoding='utf-8') as f_out:
            f_out.write(final_content)
        
        duration = round(time.time() - start_time, 2)
        print(f"\n[+] 终极修复圆满完成！")
        print(f"    - 处理总块数: {total}")
        print(f"    - 总计耗时: {duration}s")
        print(f"    - 结果保存至: {os.path.abspath(output_md)}")


    