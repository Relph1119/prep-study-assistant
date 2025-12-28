from pdf2md import UltimateStructureExtractor, SyllabusSingleLevelConverter
from split_chapter_knowledgepoints import parse_md_to_pure_json
from fimiliarity_from_outline import OllamaMathExtractor
from judge_rank import KMeansLevelRanker
from match_between_conference_and_outline import MaterialRankMatcher
from test_creation import OrderedExamGenerator
from refine import Refiner


if __name__ == "__main__":
    ## conference PDF转为markdown，适合分出层级，从而划分章节以及后续的知识点等级评定
    conference = UltimateStructureExtractor(device='cuda')
    conference.convert("material/conference.pdf", "temporary_file/conference.md")

    ## outline PDF转为markdown，方便之后生成知识点以及掌握程度的json，生成一次即可，详细见readme
    # outline = SyllabusSingleLevelConverter(device='cuda')
    # outline.convert("material/outline.pdf", "temporary_file/outline.md")

    ## 将学习资料进行章节划分以及更加细粒度的知识点划分，为知识点评定做准备
    parse_md_to_pure_json("temporary_file/conference.md", "temporary_file/sections.json", "temporary_file/knowledge_points.json")

    ## 基于学习大纲生成的知识点掌握程度汇总，基于此进行大纲中所有知识点等级评定（类似于RAG思想）
    fimiliarity_extractor = OllamaMathExtractor(model_name="qwen2.5:1.5b")
    fimiliarity_extractor.process_markdown_to_atomic("temporary_file/outline.md", "temporary_file/outline.json")
    
    ## 基于知识点掌握程度进行 K-means 聚类定级,保存在outline_rank.json
    ranker = KMeansLevelRanker()
    ranker.process("temporary_file/outline.json", "temporary_file/outline_rank.json")

    ## 将学习资料与大纲进行语义匹配，得到学习资料中知识点的等级(学习资料内容可能会和大纲的表述有出入，因此需要这个匹配，那为什么让大模型不基于大纲直接出题呢，因为我们还需要一份学习资料中的内容来进行参考，也是类似RAG的思想)，
    matcher = MaterialRankMatcher(
        rank_json_path="temporary_file/outline_rank.json", 
        material_json_path="temporary_file/knowledge_points.json"
    )
    matcher.match_and_grade("temporary_file/final_graded_material.json")

    ## 基于大模型进行智能命题，生成最终的题库
    tutor = OrderedExamGenerator(model_name="qwen2.5:7b")
    tutor.run("temporary_file/final_graded_material.json", "temporary_file/exam.md")
    ## 对题目进行修正
    refiner = Refiner(model_name="qwen2.5:7b")
    refiner.run("temporary_file/exam.md", "results/exam_final.md")


