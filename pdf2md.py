# content_pdf2md
# 必须把 os.environ 放在整个文件的最最最顶端，严禁在它们前面写任何 import！
import os

# 1. 强制镜像站（解决连接超时）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 2. 强制模型存放路径（解决模型跑到家目录的问题）
# 获取当前脚本所在目录下的 models 文件夹绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
custom_model_root = os.path.join(current_dir, "models")

if not os.path.exists(custom_model_root):
    os.makedirs(custom_model_root, exist_ok=True)

# 核心：必须在 import pix2text 之前锁定这三个环境变量
os.environ["PIX2TEXT_HOME"] = os.path.join(custom_model_root, "pix2text")
os.environ["CNOCR_HOME"] = os.path.join(custom_model_root, "cnocr")
os.environ["CNSTD_HOME"] = os.path.join(custom_model_root, "cnstd")

import re
import json
import fitz
from pix2text import Pix2Text

# =================================================================
# 1. 路径锁定与环境配置 (模型存放在当前目录 models 下)
# =================================================================
models_dir = os.path.abspath("models")
if not os.path.exists(models_dir): os.makedirs(models_dir)

os.environ["PIX2TEXT_HOME"] = os.path.join(models_dir, "pix2text")
os.environ["CNOCR_HOME"] = os.path.join(models_dir, "cnocr")
os.environ["CNSTD_HOME"] = os.path.join(models_dir, "cnstd")
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

class UltimateStructureExtractor:
    def __init__(self, device='cpu'):
        print(f"[*] 初始化引擎，模型锁定在路径: {models_dir}")
        self.p2t = Pix2Text(
            model_dir=os.environ["PIX2TEXT_HOME"],
            analyzer_config=dict(model_name='mfd', device=device)
        )
        
        # 预设全兼容的编号家族（按匹配从具体到宽泛排序）
        # 特别增强了对 LaTeX 符号在编号中出现的支持
        self.families = [
            {"id": "CH_CHAPTER_LATEX", "name": "第X章类型(含LaTeX)", "regex": r'^第\s*(?:[一二三四五六七八九十百\d]+|\$.*?\$)\s*[章节部]'},
            {"id": "CH_NUM",           "name": "汉字序号(一、)类型", "regex": r'^[一二三四五六七八九十百]+[、，\.．]'},
            {"id": "AR_LEVEL_3",       "name": "三级数字(1.1.1)类型", "regex": r'^\d+\.\d+\.\d+(?!\.\d)'},
            {"id": "AR_LEVEL_2",       "name": "二级数字(1.1)类型",   "regex": r'^\d+\.\d+(?!\.\d)'},
            {"id": "AR_LEVEL_1",       "name": "一级数字(1.)类型",    "regex": r'^\d+[、\.．](?!\d)'},
            {"id": "BRACKET_NUM",      "name": "括号数字((1))类型",   "regex": r'^[(（][\d一二三四五六七八九十]+[）)]'}
        ]
        
        self.FORBIDDEN_H3_PUNCT = r'[:：\-—]|——' # H3禁忌符号

    def _is_two_column(self, page):
        blocks = page.get_text("blocks")
        if not blocks: return False
        w, mid = page.rect.width, page.rect.width / 2
        l, r, c = 0, 0, 0
        for b in blocks:
            x0, _, x1, _ = b[:4]
            if x1 - x0 < 15: continue
            if x1 < mid: l += 1
            elif x0 > mid: r += 1
            else: c += 1
        return c < (l + r) * 0.15 and l > 2 and r > 2

    def _get_family_idx(self, text):
        for idx, f in enumerate(self.families):
            if re.match(f["regex"], text): return idx
        return None

    def _process_logic(self, raw_lines):
        # 1. 动态探测模式
        l1_idx, l2_idx = None, None
        for line in raw_lines:
            clean = line.strip()
            if not clean or '$' in clean: # 只有“第X章”允许含公式，但在识别家族时我们先避开复杂正文
                if not re.match(self.families[0]["regex"], clean): continue
            
            f_idx = self._get_family_idx(clean)
            if f_idx is not None:
                if l1_idx is None:
                    l1_idx = f_idx
                elif l2_idx is None and f_idx != l1_idx:
                    l2_idx = f_idx
            if l1_idx is not None and l2_idx is not None: break

        # 2. 构造输出 (含行内强制回车逻辑)
        md_content = []
        l1_regex = self.families[l1_idx]["regex"] if l1_idx is not None else "FORCE_NO_MATCH"
        l2_regex = self.families[l2_idx]["regex"] if l2_idx is not None else "FORCE_NO_MATCH"

        for i in range(len(raw_lines)):
            curr_line = raw_lines[i].strip()
            if not curr_line: continue
            
            # 修正数字空格
            curr_line = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', curr_line)

            # 判定 L1 (二级标题)
            if re.match(l1_regex, curr_line) and len(curr_line) < 40:
                md_content.append(f"\n## {curr_line}\n")
                continue

            # 判定 L2 (三级标题) - 执行严格条件
            if re.match(l2_regex, curr_line):
                has_forbidden = re.search(self.FORBIDDEN_H3_PUNCT, curr_line)
                has_inner_formula = '$' in curr_line and l2_idx != 0 # 除非模式本身就是第X章，否则不含公式
                is_too_long = len(curr_line) > 30
                
                # 前瞻检测
                next_is_same = False
                if i + 1 < len(raw_lines):
                    next_line = raw_lines[i+1].strip()
                    if re.match(l2_regex, next_line): next_is_same = True
                
                if not has_forbidden and not has_inner_formula and not is_too_long and not next_is_same:
                    md_content.append(f"\n### {curr_line}\n")
                else:
                    md_content.append(f"{curr_line}  \n")
            else:
                md_content.append(f"{curr_line}  \n")
        
        return "".join(md_content), l1_idx, l2_idx

    def convert(self, pdf_path, output_md_path):
        doc = fitz.open(pdf_path)
        filename = os.path.basename(pdf_path)
        raw_text_stream = ""

        print(f"[*] 解析文件中: {filename}")

        for page in doc:
            is_2col = self._is_two_column(page)
            regions = [fitz.Rect(0, 0, page.rect.width/2, page.rect.height), 
                       fitz.Rect(page.rect.width/2, 0, page.rect.width, page.rect.height)] if is_2col else [page.rect]
            
            for rect in regions:
                pix = page.get_pixmap(dpi=200, clip=rect)
                temp = "tmp.png"
                pix.save(temp)
                try:
                    res = self.p2t.recognize(temp, return_text=True)
                    # 动态行内拆分：在发现匹配 H2 或 H3 模式的地方强制换行
                    # 我们暂时无法在不知道模式前拆分，所以在获取全文本后，根据已锁定的模式再次处理
                    raw_text_stream += res + "\n"
                finally:
                    if os.path.exists(temp): os.remove(temp)

        # 临时切分行
        lines = raw_text_stream.split('\n')
        
        # 执行探测与渲染
        content, l1_id, l2_id = self._adaptive_process_with_inline_split(lines)

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(f"# {filename}\n\n")
            f.write(content)
        
        # 最终报告
        print("\n" + "="*50)
        print(f"[*] 文档结构识别报告：")
        print(f"    - 二级标题模式 (##): {self.families[l1_id]['name'] if l1_id is not None else '未发现'}")
        print(f"    - 三级标题模式 (###): {self.families[l2_id]['name'] if l2_id is not None else '未发现'}")
        print("="*50)

    def _adaptive_process_with_inline_split(self, lines):
        """ 包含探测和行内拆分逻辑的综合处理 """
        # 1. 探测模式（同上）
        l1_idx, l2_idx = None, None
        for line in lines:
            clean = line.strip()
            if not clean: continue
            f_idx = self._get_family_idx(clean)
            if f_idx is not None:
                if l1_idx is None: l1_idx = f_idx
                elif l2_idx is None and f_idx != l1_idx: l2_idx = f_idx
            if l1_idx is not None and l2_idx is not None: break

        # 2. 准备正则用于行内拆分
        split_patterns = []
        if l1_idx is not None: split_patterns.append(self.families[l1_idx]["regex"].replace('^', ''))
        if l2_idx is not None: split_patterns.append(self.families[l2_idx]["regex"].replace('^', ''))
        
        new_lines = []
        for line in lines:
            processed_line = line
            for p in split_patterns:
                # 在标点符号后面如果紧跟标题结构，强制换行
                processed_line = re.sub(f'([，。？！、：\s])({p})', r'\1\n\2', processed_line)
            new_lines.extend(processed_line.split('\n'))

        # 3. 按照锁定模式渲染（调用之前的逻辑）
        return self._process_logic(new_lines)



##outline_pdf2md
class SyllabusSingleLevelConverter:
    def __init__(self, device='cpu'):
        print(f"[*] 初始化引擎，模型锁定在路径: {models_dir}")
        self.p2t = Pix2Text(
            model_dir=os.environ["PIX2TEXT_HOME"],
            analyzer_config=dict(model_name='mfd', device=device)
        )
        
        # 预置编号模式族谱（用于自适应锁定）
        self.families = [
            {"id": "CHAPTER", "name": "第X章/节类型(含LaTeX)", "regex": r'^第\s*(?:[一二三四五六七八九十百\d]+|\$.*?\$)\s*[章节部]'},
            {"id": "CH_NUM",  "name": "汉字序号(一、)类型", "regex": r'^[一二三四五六七八九十百]+[、，\.．]'},
            {"id": "AR_MULTI", "name": "多级数字(1.1)类型", "regex": r'^\d+(\.\d+)+'},
            {"id": "AR_SINGLE", "name": "单级数字(1.)类型", "regex": r'^\d+[、\.．\s]'},
            {"id": "BRACKET", "name": "括号数字((1))类型", "regex": r'^[(（][\d一二三四五六七八九十]+[）)]'}
        ]

    def _is_two_column(self, page):
        """ 检测单双栏排版顺序 """
        blocks = page.get_text("blocks")
        if not blocks: return False
        w, mid = page.rect.width, page.rect.width / 2
        l, r, c = 0, 0, 0
        for b in blocks:
            x0, _, x1, _ = b[:4]
            if x1 - x0 < 15: continue
            if x1 < mid: l += 1
            elif x0 > mid: r += 1
            else: c += 1
        return c < (l + r) * 0.15 and l > 2 and r > 2

    def _detect_and_render(self, raw_lines):
        """
        核心自适应逻辑：锁定第一个出现的编号模式作为唯一的 H2
        """
        locked_family_idx = None
        
        # 1. 探测阶段：寻找第一个编号
        for line in raw_lines:
            clean = line.strip()
            if not clean: continue
            
            # 识别属于哪个家族
            for idx, f in enumerate(self.families):
                if re.match(f["regex"], clean):
                    locked_family_idx = idx
                    print(f"[*] 自适应锁定：检测到第一个编号为 [{clean}]，后续所有 [{f['name']}] 将作为二级标题。")
                    break
            if locked_family_idx is not None:
                break

        # 2. 渲染阶段
        md_content = []
        target_regex = self.families[locked_family_idx]["regex"] if locked_family_idx is not None else "FORCE_NO_MATCH"

        for line in raw_lines:
            clean = line.strip()
            if not clean: continue
            
            # 修复可能存在的数字空格
            clean = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', clean)

            # 判定二级标题条件：符合锁定的模式、不含公式、长度合理
            # (注意：如果是第X章这种本身带公式的模式，排除 has_formula 限制)
            has_formula = '$' in clean
            if locked_family_idx == 0: has_formula = False # 模式0允许公式
            
            if re.match(target_regex, clean) and not has_formula and len(clean) < 40:
                md_content.append(f"\n## {clean}\n")
            else:
                # 其余一律视为正文
                md_content.append(f"{clean}  \n")
        
        return "".join(md_content), locked_family_idx

    def convert(self, pdf_path, output_md_path, dpi=200):
        doc = fitz.open(pdf_path)
        filename = os.path.basename(pdf_path)
        all_lines = []

        print(f"[*] 解析大纲中: {filename}")

        for page in doc:
            # 自动分栏检测
            regions = [fitz.Rect(0, 0, page.rect.width/2, page.rect.height), 
                       fitz.Rect(page.rect.width/2, 0, page.rect.width, page.rect.height)] if self._is_two_column(page) else [page.rect]
            
            for rect in regions:
                pix = page.get_pixmap(dpi=dpi, clip=rect)
                temp = "tmp.png"
                pix.save(temp)
                try:
                    res = self.p2t.recognize(temp, return_text=True)
                    # 修复行内粘连标题
                    res = re.sub(r'([，。？！、：\s])(\d+(\.\d+)*[、\.．\s])', r'\1\n\2', res)
                    all_lines.extend(res.split('\n'))
                finally:
                    if os.path.exists(temp): os.remove(temp)

        # 执行自适应处理
        content, pattern_idx = self._detect_and_render(all_lines)

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(f"# {filename}\n\n") # H1 文件名
            f.write(content)
        
        print("\n" + "="*50)
        print(f"[*] 结构识别报告：")
        print(f"    - 二级标题(##) 锁定的模式为: {self.families[pattern_idx]['name'] if pattern_idx is not None else '未发现'}")
        print("="*50)
        print(f"[+] 结构化文件已生成: {output_md_path}")
