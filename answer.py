import re
import json 
from typing import List
from openai import OpenAI
from tqdm import tqdm
from itertools import product
from openai_api import OpenAIClient
import argparse
from utils import number_to_uppercase_letter
from evaluator import Evaluator

parser = argparse.ArgumentParser()

parser.add_argument('--max_tokens', default=2048, type=int)
parser.add_argument('--fix_rule', default=True, type=bool)
args = parser.parse_args()

base_url = 'http://localhost:11434/v1'
key = 'ollama'
client = OpenAI(
            base_url = base_url,
            api_key = key
        )
model_name = "qwen2.5:7b"
max_tokens = args.max_tokens
stop = ["，", "。", ".", ","]
temperature=0.5
num_completions=8
presence_penalty=0.0

openai_client = OpenAIClient(client=client, model_name=model_name, max_tokens=max_tokens, temperature=temperature, 
             presence_penalty=presence_penalty, stop=stop, num_completions=num_completions)

prompt = ""


    
# 定义规则类
class Rule:
    def __init__(self, rule_id, rule_text):
        self.rule_id = rule_id
        self.rule_text = rule_text
    
    def __repr__(self):
        return f"Rule({self.rule_id})"

# 定义任务类
class Task:
    def __init__(self, question_id, question_text, rule_id=None, answer=None):
        self.question_id = question_id
        self.full_text = question_text
        self.choices = self.extract_choices(question_text)  # 自动提取待选答案
        self.question_text = question_text.split("选择：")[0].strip()
        self.correct_answer = answer  # 正确答案
        self.rule_id = None  # l个相关规则
        self.correct_rule_id = rule_id
        self.answer = None
        
    def get_rule_id(self):
        # print(self.rule_id)
        if isinstance(self.rule_id, List):
            return self.rule_id
        return list(list(zip(*sorted(self.rule_id.items(), key=lambda x: x[1])))[0]) if self.rule_id else []
        
    def extract_choices(self, question_text):
        """
        从问题文本中提取待选答案。
        假设问题文本中的答案选项按照“选择：A. ... B. ... C. ...”的格式排列，
        并且可能有更多选项如E, F, G等。
        """
        pattern = r'([A-Z])\.(.*?)(?=(?:[A-Z]\.|$))'
        matches = re.findall(pattern, question_text, re.S)
        return [match[1].strip() for match in matches]

    def set_answer(self, answer):
        self.answer = answer

    def set_related_rule(self, rule):
        self.rule_id = rule

    def __repr__(self):
        return f"Task(question_id={self.question_id}, question_text='{self.question_text}', choices={self.choices})"
    
    def print_result(self):
        print(f"任务ID: {self.question_id}")
        print(f"问题: {self.question_text}")
        print(f"已选答案: {self.answer}")
        print(f"正确答案: {self.correct_answer}")
                # if choice == task.answer:
        print(f"答案是否正确：{self.answer == self.correct_answer}")
        print(f"待选答案: {self.choices}")
        print(f"已选规则: {self.get_rule_id()}")
        print(f"相关规则: {self.correct_rule_id}")
        print("------")

# 定义数据集类
class Dataset:
    
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks  # 包含多个任务对象

    def complete_tasks(self, rules: List[Rule]):
        """
        根据规则对象，补全任务的正确答案和相关规则属性
        """
        rules_dict = {rule.rule_id: rule.rule_text  for rule in rules}
        
        for tid, task in tqdm(enumerate(self.tasks), total=len(self.tasks)):
            
            # 这里假设有一个方法可以根据问题和规则生成正确答案和相关规则
            if args.fix_rule and task.correct_rule_id:
                task.set_related_rule(task.correct_rule_id)
            else:
                task.set_related_rule(self.related_rules(task, rules))
            # else:
            task.set_answer(self.answer(task, rules_dict))
            task.print_result()
            
            if (tid + 1) % 5 == 0:
                self.evaluate(tid + 1)
            
            

    def answer(self, task: Task, rules):
        # 模拟生成正确答案的逻辑
        task_rules = task.get_rule_id()
        # print(task_rules)
        task_rules_text = []
        for rule_id in task_rules[:10]:
            rule = rules[rule_id]
            task_rules_text.append(rule)
        
        choices = dict()
        
        # deductions = []
        for cid, choice in enumerate(task.choices):
            rules_text = "\n".join(task_rules_text)
        #     deduction = openai_client.deduce(task.question_text, choice, rules_text, num_completions=1)[0]
        #     deductions.append(deduction)
            # judegements = openai_client.judge_answer(task.question_text, choice, rules_text, deduction)
            
            # num_true, num_false = 0, 0
            # for judegement in judegements:
            
            #     num_true += int("是" in judegement)
            #     num_false += int("否" in judegement)
            
            # if num_true > num_false:
            # choices[number_to_uppercase_letter(cid)] = num_true - num_false
        # deduction = openai_client.deduce_agg(task.full_text, task.choices, rules_text, deductions)
        deduction = openai_client.deduce_direct(task.full_text, rules_text)
        
        answer = ""
        # raise RuntimeError()
        
        while not answer:
            answer_maybe = openai_client.select_answer(task.question_text, rules_text, deduction, len(task.choices))[0]
            # print(answer_maybe)
            # raise RuntimeError()
            for letter in [number_to_uppercase_letter(i) for i in range(len(task.choices))]:
                if letter in answer_maybe:
                    answer = letter
        
        
        # choices = list(zip(*sorted(choices.items(), key=lambda x: x[1])))[0]
        # choice = choices[0]
        choice = answer

            
        return choice  # 示例返回值
    

    def related_rules(self, task: Task, rules: List[Rule]):
        
        rela_rules = {}
        
        prod = product(task.choices, rules)
        
        for rule in tqdm(rules, desc=f"Task:{task.question_id}"):
            
            completions = openai_client.judge_helpful_rule(task.full_text, rule.rule_text)
            
            num_true, num_false = 0, 0
            for completion in completions:
                num_true += int("是" in completion)
                num_false += int("否" in completion)
            
            if num_true > num_false:
                rela_rules[rule.rule_id] = num_true - num_false
                
                    
        # 模拟获取相关规则的逻辑
        return rela_rules  # 示例返回值
    
    def evaluate(self, task_num):
        evaluator = Evaluator(self.tasks[:task_num])

        # Calculate the scores
        accuracy = evaluator.accuracy()
        hit_score = evaluator.hit_score()
        final_score = evaluator.final_score()

        # Print the results
        print(f"Accuracy: {accuracy}")
        print(f"Hit Score: {hit_score}")
        print(f"Final Score: {final_score}")


# 从文件加载数据并创建对象
def load_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        rules_data = json.load(f)
    return [Rule(**rule) for rule in rules_data]

def load_tasks(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    return [Task(**task) for task in tasks_data]

# 加载规则和任务数据
rules = load_rules("rules1.json")
dev_tasks = load_tasks("dev.json")
test_tasks = load_tasks("test1.json")

# dev_tasks = dev_tasks[:5]

# 创建数据集对象
dev_dataset = Dataset(dev_tasks)
test_dataset = Dataset(test_tasks)

dev_dataset.complete_tasks(rules)

evaluator = Evaluator(dev_dataset.tasks)

# Calculate the scores
accuracy = evaluator.accuracy()
hit_score = evaluator.hit_score()
final_score = evaluator.final_score()

# Print the results
print(f"Accuracy: {accuracy}")
print(f"Hit Score: {hit_score}")
print(f"Final Score: {final_score}")

# 补全开发集和测试集任务的正确答案和相关规则属性

# test_dataset.complete_tasks(rules)

# # 查看结果
# for task in dev_dataset.tasks:
#     print(f"任务ID: {task.question_id}")
#     print(f"问题: {task.question_text}")
#     print(f"已选答案: {task.answer}")
#     print(f"正确答案: {task.correct_answer}")
#     print(f"待选答案: {task.choices}")
#     print(f"已选规则: {task.get_rule_id()}")
#     print(f"相关规则: {task.correct_rule_id}")
#     print("------")

# for task in test_dataset.tasks:
#     print(f"任务ID: {task.question_id}")
#     print(f"问题: {task.question_text}")
#     print(f"已选答案: {task.answer}")
#     print(f"正确答案: {task.correct_answer}")
#     print(f"待选答案: {task.choices}")
#     print(f"已选规则: {task.get_rule_id()}")
#     print(f"相关规则: {task.correct_rule_id}")
#     print("------")
