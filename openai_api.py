from typing import List, Dict
from utils import number_to_uppercase_letter

YES_OR_NO_BASE = "你是一个简单的判别模型，在你输出的内容中仅仅可以输出是和否其中的一个。"

DEDUCE_BASE = "给定需解答的问题和选择，组合给定的完全正确的规则，经演逐步的绎推理论证和必要的数学运算证明答案的正确性，你的输出将给出完整的演绎结果和最终判断。" +\
    "不需要对错误答案进行改正，需明确指出选项的错误，并着重强调是否错误，否则会导致后续判断中，将错误选项与你所改正的正确结论混淆。" +\
    "为了演绎的稳固性，深入理解规则，只有这些规则是完全正确的。"+\
    "若需选择正确选项，推理正确结论并坚决排除错误选项。否则推理错误选项并坚决排除正确选项。" +\
            "判断答案中是否有规则中明确定义的专有名词（如级别名称，单位名称等），将可能的答案中的一切同义词或程度更低或更高的词视为无效或错误。" +\
                "判断概念范畴是否有混淆，如题干和选项中的组织，部门与个人等并非同一范畴。若答案中概念的范畴与问题询问的范畴不同，存在作用域上的混淆，则选项无效和逻辑的一致性错误。" +\
                "严格检查数字是否正确，数字不正确即有误。你的输出将给出完整的演绎结果。"
                
DEDUCE_BASE = '''
给定：

- **需要解答的问题和选项。**
- **完全正确的规则。**

你的任务是：

1. **推理过程：** 根据给定的规则和必要的数学运算，逐步推理论证，证明答案的正确性。

2. **输出完整结果：** 你的输出应给出完整的演绎推理结果和最终判断。

3. **不改正错误答案：** 不需要对错误的选项进行改正。需明确指出选项的错误，并着重强调其错误之处。否则可能导致后续判断中，将错误选项与你改正的正确结论混淆。

4. **深入理解规则：** 为了保证推理的稳固性，深入理解并严格遵循给定的规则，这些规则是完全正确的。

5. **选择正确或错误的选项：**

   - **若需选择正确选项：** 推理出正确的结论，坚决排除错误的选项。
   - **否则：** 推理出错误的结论，坚决排除正确的选项。

6. **术语准确性：** 判断答案中是否使用了规则中明确定义的专有名词（如级别名称、单位名称等）。将答案中使用的任何同义词或程度更低或更高的词视为无效或错误。

7. **概念范畴一致性：** 判断概念范畴是否有混淆，例如题干和选项中的组织、部门与个人等并非同一范畴。若答案中的概念范畴与问题询问的范畴不同，存在作用域混淆，则该选项无效并存在逻辑一致性错误。

8. **数字核对：** 严格检查数字是否正确，数字不正确即为错误。

9. **输出完整推理：** 你的输出应给出完整的演绎推理结果和最终判断。
'''

DEDUCE_ALL_BASE = "给定完全正确的规则，以及先前的一些可能包含错误的推导过程，需解答的问题和选择（仅有一个是正确的）,你的任务是再给出一系列推导过程，最终确认结论对应的选项。" +\
            "不要将题目中的选项内容与推理给出的改正后的内容混淆，需专注于判断选项内容的正确性，否则将改正后的选项与题目中的选项内容混淆后，必然导致推理错误。" +\
            "为了演绎的稳固性，深入理解规则，只有这些规则是完全正确的。"+\
            "一步步推理以保证一致性，避免引入多重否定和从而增加语义理解难度。" +\
                "判断答案中是否有规则中明确定义的术语和专有名词（如级别名称，单位名称等），将可能的答案中的一切同义词或程度更低或更高的词视为无效或错误。" +\
                "对于每个问题**仅有**一个可选选项，所有选项之间的关系是并列的，彼此相互独立，选项之间没有因果关系。"+\
            "若需选择正确选项，推理正确结论并坚决排除错误选项，找出唯一正确的选项。否则推理错误选项并坚决排除正确选项，找出唯一的错误选项。" +\
                "严格检查数字是否正确，数字不正确即有误。" +\
                "遇到全程量词“所有”时，一定检查规则中对应的所有实体均符合题干要求才为正确。" +\
                "你的输出将给出完整的演绎结果。" +\
                    "判断概念范畴是否有混淆，如题干和选项中的组织，部门与个人等并非同一范畴。若答案中概念的范畴与问题询问的范畴不同，存在作用域上的混淆，则选项无效和逻辑的一致性错误。" +\
                    "上述步骤完成后，若多个推理结果认为存在多个可选选项，继续按照上面的步骤检查，直到排除所有不可选的选项或找到最可选的选项。"
                    
DEDUCE_ALL_BASE = '''给定：

- **完全正确的规则。**
- **可能包含错误的先前推导过程。**
- **需要解答的问题和选项（仅有一个是正确的）。**

你的任务是：

1. **推理过程：** 提供一系列推导步骤，最终确认结论对应的选项。

2. **专注选项内容：** 不要将题目中的选项内容与你在推理过程中改正后的内容混淆。需专注于判断原始选项内容的正确性，否则混淆可能导致推理错误。

3. **深入理解规则：** 为了确保推理的稳固性，深入理解并严格遵循给定的规则，这些规则是完全正确的。

4. **逐步推理：** 进行一步一步的推理，以保证逻辑一致性。避免引入多重否定，减少语义理解的难度。

5. **术语准确性：** 判断答案中是否使用了规则中明确定义的术语和专有名词（如级别名称、单位名称等）。将答案中使用的任何同义词或程度更低或更高的词视为无效或错误。

6. **选项独立性：** 对于每个问题**仅有**一个可选选项。所有选项之间的关系是并列的，彼此相互独立，没有因果关系。

7. **选择正确或错误的选项：**

   - **若需选择正确选项：** 推理出正确的结论，坚决排除错误的选项，找出唯一正确的选项。
   - **若需选择错误选项：** 推理出错误的结论，坚决排除正确的选项，找出唯一错误的选项。

8. **数字核对：** 严格检查数字是否正确，数字不正确则视为有误。

9. **全称量词检查：** 遇到全称量词“所有”时，一定要检查规则中对应的所有实体是否均符合题干要求，选项才为正确。

10. **输出完整推理：** 你的输出应给出完整的演绎推理结果。

11. **题干查询范围一致性：** 判断概念范围是否有混淆，例如题干和选项中的组织、部门与个人等并非同一范围。若答案中查询的概念的范围与问题询问的范围不同，存在作用域上的混淆，则该选项无效并存在逻辑一致性错误。

12. **持续检查：** 若经过上述步骤后，仍有多个可能的选项，继续按照上述步骤检查，直到排除所有不可选的选项或找到最符合要求的选项。
'''

CLASSIFICATION_BASE = lambda X:f"判别唯一可选的选项，你的输出内容仅能为：\"分类结果：X\"。X是{', '.join(X)}中的一个。"


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
            # {
            #     "role": "assistant",
            #     "content": "根据给出的信息，我们逐步演绎如下：\n\n",
            # },
        ]
        completions = self.get_responses(messages, num_completions, stop=[])
        return completions
    
    def deduce_agg(self, task_text, answers, rules_text, deductions: List[str]) -> List[str]:
        for idx, deduction in enumerate(deductions):
            choice_of_the_deduction = number_to_uppercase_letter(idx)
            deductions[idx] = choice_of_the_deduction + ". "  + answers[idx] + "：" + deduction
        reasoning = "关于每一个答案的演绎过程：" + "\n```\n" + "\n".join(deductions) + "\n```"
        rule_text = "规则：" + rules_text
        task_text = "需解答的" + task_text
        
        prompt = "\n\n\n".join([rule_text, reasoning, task_text])
        
        messages = [
            { 
                "role": "system", 
                "content": DEDUCE_ALL_BASE
            },
            {
                "role": "user",
                "content": prompt,
            },
            # {
            #     "role": "assistant",
            #     "content": "已获取具体规则、推导过程和问题、选项。内容详尽，无需询问额外信息。根据给出的信息，我们逐步演绎如下：",
            # },
        ]
        print(prompt)
        completions = self.get_responses(messages, num_completions=1, stop=[])
        return completions
    
    def select_answer(self, task_text, rules_text, deduction: str, num_answer: int) -> List[str]:
        
        classification_base = CLASSIFICATION_BASE([number_to_uppercase_letter(i) for i in range(num_answer)])
        
        reasoning = "部分过程：..." + "\n".join(deduction)[-256:]
        rule_text = "规则：" + rules_text
        
        prompt = "\n".join([task_text, rule_text, reasoning, "分类结果："])
        
        messages = [
            { 
                "role": "system", 
                "content": classification_base
            },
            {
                "role": "user",
                "content": prompt,
            },
            # {
            #     "role": "assistant",
            #     "content": "分类结果：",
            # },
        ]
        print(reasoning)
        # raise RuntimeError()
        completions = self.get_responses(messages, num_completions=1, stop=[])
        # print(completions)
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
