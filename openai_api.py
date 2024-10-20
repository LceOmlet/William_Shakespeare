from typing import List, Dict
from utils import number_to_uppercase_letter

YES_OR_NO_BASE = "你是一个简单的判别模型，在你输出的内容中仅仅可以输出是和否其中的一个。"

DEDUCE_BASE = "给定问题和可能的答案，组合给定的完全正确的规则，经演逐步的绎推理论证和必要的数学运算证明答案的正确性，你的输出将给出完整的演绎结果。" +\
    "为了演绎的稳固性，深入理解规则，只有这些规则是完全正确的。"+\
    "若需选择正确选项，推理正确结论并坚决排除错误选项。否则推理错误选项并坚决排除正确选项。" +\
            "判断答案中是否有规则中明确定义的专有名词（如级别名称，单位名称等），将可能的答案中的一切同义词或程度更低或更高的词视为无效或错误。你的输出将给出完整的演绎结果。"

DEDUCE_ALL_BASE = "给定问题，可能的答案（仅有一个是正确的）和完全正确的规则，以及先前的一些可能包含错误的推导过程，再给出一系列推导过程。" +\
            "为了演绎的稳固性，深入理解规则，只有这些规则是完全正确的。"+\
            "一步步推理以保证一致性，避免引入多重否定和从而增加语义理解难度。" +\
                "判断答案中是否有规则中明确定义的专有名词（如级别名称，单位名称等），将可能的答案中的一切同义词或程度更低或更高的词视为无效或错误。" +\
                "对于每个问题**仅有**一个可选选项，所有选项之间的关系是并列的，彼此相互独立，选项之间没有因果关系。"+\
                    "若多个推理结果认为存在多个可选选项，继续推理，直到排除所有不可选的选项或找到最可选的选项。" +\
            "若需选择正确选项，推理正确结论并坚决排除错误选项，找出唯一正确的选项。否则推理错误选项并坚决排除正确选项，找出唯一的错误选项。" +\
                "你的输出将给出完整的演绎结果。"

CLASSIFICATION_BASE = lambda X:f"判别唯一正确的选项，你的输出内容仅能为：\"分类结果：X\"。X是{', '.join(X)}中的一个。"


class OpenAIClient:
    def __init__(self, client, model_name: str, max_tokens: int, temperature: float,
                 presence_penalty: float, stop: List[str], num_completions: int):
        self.client = client
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.num_completions = num_completions

    def judge_helpful_rule(self, task_text, rule_text: str) -> List[Dict[str, str]]:
        YES_OR_NO_BASE_USER = "给出一个问题和可能的答案，无论该答案是否正确，判断一条规则（联合其他规则并通过简单的计算后）是否对肯定这个答案或是否定这个答案有所帮助。"
        rule_text = "规则：" + rule_text
        prompt = "\n".join([YES_OR_NO_BASE_USER, task_text, rule_text])
        prompt += "\n请仅仅输出是和否两个字中其中一个字。"
        messages = [
            { 
                "role": "system", 
                "content": YES_OR_NO_BASE
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        # print(messages)
        completions = self.get_responses(messages)
        # print(completions)
        return completions
    
    def judge_answer(self, question_text, answer, rules_text: str, reasoning) -> List[Dict[str, str]]:
        YES_OR_NO_BASE_USER = "给定一系列规则，一个问题，某个作答和帮助判断的推理过程，这个作答是否正确。"
        rule_text = "规则：" + rules_text
        answer = "作答：" + answer
        reasoning = "推理过程：" + reasoning
        prompt = "\n".join([YES_OR_NO_BASE_USER, question_text, answer, rule_text, reasoning])
        prompt += "\n 请仅仅输出是和否两个字中其中一个字。"
        messages = [
            { 
                "role": "system", 
                "content": YES_OR_NO_BASE
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        return self.get_responses(messages)
    
    def deduce(self, question_text, answer, rules_text: str, num_completions=None) -> List[Dict[str, str]]:
        DEDUCE_BASE_USER = "给定问题和可能的答案，组合给定的规则，经演逐步的绎推理论证和必要的数学运算证明答案的正确性，你的输出将给出简明且完整的演绎结果。你演绎的每一步应该为确定并简明，并尽可能地不引入无关内容。"
        answer = "作答：" + answer
        rules_text = "规则：" + rules_text
        prompt = "\n".join([DEDUCE_BASE_USER, question_text, answer, rules_text])
        messages = [
            { 
                "role": "system", 
                "content": DEDUCE_BASE
            },
            {
                "role": "user",
                "content": prompt,
            },
            {
                "role": "assistant",
                "content": "根据给出的信息，我们逐步演绎如下：",
            },
        ]
        completions = self.get_responses(messages, num_completions, stop=[])
        return completions
    
    def deduce_agg(self, task_text, rules_text, deductions: List[str]) -> List[str]:
        for idx, deduction in enumerate(deductions):
            choice_of_the_deduction = number_to_uppercase_letter(idx)
            deductions[idx] = choice_of_the_deduction + ". " + deduction
        reasoning = "关于每一个答案的演绎过程：" + "\n".join(deductions)
        rule_text = "规则：" + rules_text
        
        prompt = "\n".join([task_text, rule_text, reasoning])
        
        messages = [
            { 
                "role": "system", 
                "content": DEDUCE_ALL_BASE
            },
            {
                "role": "user",
                "content": prompt,
            },
            {
                "role": "assistant",
                "content": "根据给出的信息，我们逐步演绎如下：",
            },
        ]
        completions = self.get_responses(messages, num_completions=1, stop=[])
        print(completions)
        return completions
    
    def select_answer(self, task_text, rules_text, deduction: str, num_answer: int) -> List[str]:
        
        classification_base = CLASSIFICATION_BASE([number_to_uppercase_letter(i) for i in range(num_answer)])
        
        reasoning = "演绎过程：" + "\n".join(deduction)
        rule_text = "规则：" + rules_text
        
        prompt = "\n".join([task_text, rule_text, reasoning])
        
        messages = [
            { 
                "role": "system", 
                "content": classification_base
            },
            {
                "role": "user",
                "content": prompt,
            },
            {
                "role": "assistant",
                "content": "分类结果：",
            },
        ]
        print(reasoning)
        completions = self.get_responses(messages, num_completions=1, stop=[])
        print(completions)
        return completions

    def get_responses(self, messages: List[Dict[str, str]], num_completions=None, stop=None) -> List[str]:
        # print(num_completions, self.num_completions)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            presence_penalty=self.presence_penalty,
            stop=stop if stop is not None else self.stop,
            n=num_completions if num_completions is not None else self.num_completions,
        )
        return [completion.message.content for completion in response.choices]
