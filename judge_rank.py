# judge_rank

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import json
import os
import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from collections import Counter

# 1. 基础配置
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
embedding_model_path = "BAAI/bge-m3" # 沿用之前的强力模型

class KMeansLevelRanker:
    def __init__(self, model_name=embedding_model_path):
        print(f"[*] 正在加载嵌入模型: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def process(self, input_path, output_path):
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"[*] 正在为 {len(data)} 个知识点生成语义特征向量...")
        
        # 【策略】将“掌握要求”和“知识内容”拼接在一起进行编码
        # 这样编码既包含了动词的权重，也包含了内容本身的复杂度
        texts_to_encode = [f"{item['familiarity']} {item['content']}" for item in data]
        embeddings = self.model.encode(texts_to_encode, show_progress_bar=True)

        # 2. 执行 K-means 聚类 (k=3)
        print("[*] 正在执行 K-means 聚类分析...")
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)

        # 3. 难易度自动映射 (重点)
        # K-means 产生的 0,1,2 标签是随机的，我们需要判断哪个标签代表“高级”
        # 逻辑：计算每个类别的平均文本长度或利用关键词密度来辅助排序
        cluster_scores = []
        for i in range(3):
            # 获取属于该簇的所有文本
            cluster_texts = [texts_to_encode[j] for j, label in enumerate(cluster_labels) if label == i]
            # 计算该簇的“复杂度得分”（这里使用平均长度作为简单代理，长句通常逻辑更深）
            avg_len = sum(len(t) for t in cluster_texts) / len(cluster_texts)
            cluster_scores.append((i, avg_len))
        
        # 按复杂度从低到高排序
        # 简单逻辑：平均长度最短的簇设为初级，最长的设为高级
        sorted_clusters = sorted(cluster_scores, key=lambda x: x[1])
        rank_map = {
            sorted_clusters[0][0]: "初级",
            sorted_clusters[1][0]: "中级",
            sorted_clusters[2][0]: "高级"
        }

        # 4. 组装结果
        ranked_data = []
        stats = Counter()

        for i, item in enumerate(data):
            label = cluster_labels[i]
            level = rank_map[label]
            stats[level] += 1
            
            ranked_data.append({
                "id": item['id'],
                "name": item['content'],
                "familiarity": item['familiarity'],
                "level": level
            })

        # 5. 打印报告
        print("\n" + "📊 知识点等级分布报告 (基于 K-means 语义聚类)")
        print("="*45)
        print(f"🟢 初级 (Junior): {stats['初级']} 个")
        print(f"🟡 中级 (Middle): {stats['中级']} 个")
        print(f"🔴 高级 (Senior): {stats['高级']} 个")
        print(f"📝 总计知识点:   {len(ranked_data)} 个")
        print("="*45)

        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(ranked_data, f_out, ensure_ascii=False, indent=4)
        print(f"[+] 聚类定级成功！文件已保存至: {output_path}")

