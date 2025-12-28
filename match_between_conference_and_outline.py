#pipei
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer



class MaterialRankMatcher:
    def __init__(self, rank_json_path, material_json_path):
        # 加载嵌入模型
        print("[*] 正在加载嵌入模型 (BAAI/bge-m3)...")
        self.model = SentenceTransformer('BAAI/bge-m3')
        
        # 加载数据
        with open(rank_json_path, 'r', encoding='utf-8') as f:
            self.rank_data = json.load(f)
        with open(material_json_path, 'r', encoding='utf-8') as f:
            self.materials = json.load(f)
            
        self.index = None

    def build_index(self):
        """ 为 rank.json 中的知识点名称建立向量索引 """
        print(f"[*] 正在为大纲标准 ({len(self.rank_data)}项) 构建索引...")
        # 提取大纲名
        syllabus_names = [item['name'] for item in self.rank_data]
        embeddings = self.model.encode(syllabus_names, show_progress_bar=True)
        
        # 使用 FAISS 构建检索索引
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        print("[+] 索引构建完成。")

    def match_and_grade(self, output_path):
        """ 执行匹配并生成带等级的资料 JSON """
        self.build_index()
        
        final_graded_results = []
        print(f"[*] 开始匹配学习资料内容 (共 {len(self.materials)} 项)...")

        for m_item in self.materials:
            # 1. 对资料名称进行编码
            m_name = m_item['knowledge_name']
            m_vec = self.model.encode([m_name])
            
            # 2. 在大纲索引中寻找最相似的 1 个项
            # D 是距离，I 是对应的索引号
            D, I = self.index.search(np.array(m_vec).astype('float32'), k=1)
            matched_idx = I[0][0]
            matched_syllabus = self.rank_data[matched_idx]

            # 3. 继承等级并构造新字典
            # 我们保留原始资料的所有信息，并加上定级字段
            graded_item = {
                "knowledge_id": m_item['knowledge_id'],
                "knowledge_name": m_name,
                "knowledge_content": m_item['knowledge_content'],
                "difficulty_level": matched_syllabus['level'],
                "matched_standard_name": matched_syllabus['name'],
                "match_confidence": float(1 - D[0][0]/10) # 简单计算匹配置信度
            }
            
            final_graded_results.append(graded_item)

        # 4. 保存为新的 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(final_graded_results, f_out, ensure_ascii=False, indent=4)
        
        print(f"\n[+] 定级任务全部完成！")
        print(f"    - 输入资料: {len(self.materials)} 条")
        print(f"    - 输出结果: {output_path}")

    