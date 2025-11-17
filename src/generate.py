from agents.generators import StudentClientGenerator
from argparse import ArgumentParser
from utils import load_json, get_model_client

if __name__ == "__main__":
    args = ArgumentParser()
    args.add_argument("--lang", type=str, default="en")
    args.add_argument("--api_type", type=str, default="LAB")
    args.add_argument("--model_name", type=str, default="gpt-4o")

    args = args.parse_args()
    model_client = get_model_client(args.model_name, args.api_type)

    character_generator = StudentClientGenerator(model_client, args.lang)

    context = """小B同学是某大学大二学生，性格内向，平时话不多。刚入学时，他还能勉强适应大学生活，但随着时间推移，学业压力和人际关系的复杂让他逐渐感到力不从心。小B的成绩一直中规中矩，但最近一个学期，他的成绩开始下滑，甚至有几门课程接近挂科。他觉得自己很笨，无法像其他同学那样轻松应对学业，这种挫败感让他对学习失去了兴趣。
小B的宿舍生活也不顺利。他常常感到被室友们忽视，尽管大家没有明显的冲突，但他内心总觉得无法融入这个小集体。最近几个月，小B的睡眠质量变得很差，经常失眠，白天则感到极度疲惫，甚至无法集中精力完成作业。他开始逃避社交活动，连每周一次的班级篮球赛也放弃了，而这是他曾经最期待的活动。
更令人担忧的是，小B在日记中写下了许多消极的文字，表达了对生活的厌倦和对未来的迷茫。他觉得自己“一无是处”，甚至在一次深夜的电话中，向好友透露“不知道自己还能坚持多久”。好友虽然感到不安，但也没有太在意，认为这只是小B的一时情绪。"""

    # character_generator.create_character(situation=context)

    character_generator.create_character(topic="学业问题")

    character_generator.create_character()
