QUERY_SYN_MM_PROMPT_MAIN = """You are an assistant specialized in creating Multimodal RAG tasks. The task is the following:
Given some natural language contexts and images inside these contexts, you will have to generate questions that can be asked by a user to retrieve information from a large documentary corpus.

**Requirements:**
<requirements>
{{Requirements}}
</requirements>

**Question Template:** This is the Template of your questions. You must use the template to generate the QA.
<template>
{{TEMPLATES}}
</template>

**FORMAT:**

Generate 1 pair of questions and answers per page in a dictionary with the following format, answer ONLY this dictionary NOTHING ELSE:
<format>
{{FORMAT}}
</format>

{{EXPLANATION_INFO}}
Note: If the image can be used to help visualization or illustration only, return an empty list. If you cannot use all the chunks in the answer, return an empty list.
"""

from prompts.answer_type import REQUIREMENTS_IMAGE_ANSWER, EXPLANATION_INFO_IMAGE_ANSWER, FORMAT_IMAGE_ANSWER
from prompts.answer_type import REQUIREMENTS_TABLE_ANSWER, EXPLANATION_INFO_TABLE_ANSWER, FORMAT_TABLE_ANSWER
from prompts.answer_type import REQUIREMENTS_TEXT_ANSWER, EXPLANATION_INFO_TEXT_ANSWER, FORMAT_TEXT_ANSWER
from prompts.answer_type import REQUIREMENTS_IMAGE_plus_TEXT_ANSWER, EXPLANATION_INFO_IMAGE_plus_TEXT_ANSWER, FORMAT_IMAGE_plus_TEXT_ANSWER
from prompts.query_type import REQUIREMENTS_FACTUAL_RETRIEVAL, REQUIREMENTS_COMPARISON, REQUIREMENTS_SUMMARIZATION, REQUIREMENTS_CAUSAL_REASONING

def obtain_user_prompt(answer_type, template, query_type=None):
    user_prompt = QUERY_SYN_MM_PROMPT_MAIN.replace("{{TEMPLATES}}", template)
    if answer_type == "image_as_answer":
        user_prompt = user_prompt.replace("{{Requirements}}", REQUIREMENTS_IMAGE_ANSWER)
        user_prompt = user_prompt.replace("{{EXPLANATION_INFO}}", EXPLANATION_INFO_IMAGE_ANSWER)
        user_prompt = user_prompt.replace("{{FORMAT}}", FORMAT_IMAGE_ANSWER)
        user_prompt += "Remember: The synthesized question must be specific enough to be used to help a RAG system retrieve the document or context containing that image from a large corpus. You will not mention the 'what XYZ in the graph/image/figure' because your question must be general enough to be used as a question to ask in a large corpus. Also, avoid 'what is shown in the image' phrasing, such as 'what color/logo/name in the image.'"
    elif answer_type == "text_as_answer":
        user_prompt = user_prompt.replace("{{Requirements}}", REQUIREMENTS_TEXT_ANSWER)
        user_prompt = user_prompt.replace("{{EXPLANATION_INFO}}", EXPLANATION_INFO_TEXT_ANSWER)
        user_prompt = user_prompt.replace("{{FORMAT}}", FORMAT_TEXT_ANSWER)
        user_prompt += "\n\nHint: Chunk1 and Chunk 2 are related because of '{{hints}}'. You can synthesize question about '{{hints}}' to use both of the chunks."
    elif answer_type == "image_plus_text_as_answer":
        user_prompt = user_prompt.replace("{{Requirements}}", REQUIREMENTS_IMAGE_plus_TEXT_ANSWER)
        user_prompt = user_prompt.replace("{{EXPLANATION_INFO}}", EXPLANATION_INFO_IMAGE_plus_TEXT_ANSWER)
        user_prompt = user_prompt.replace("{{FORMAT}}", FORMAT_IMAGE_plus_TEXT_ANSWER)
        user_prompt += "\n\nHint: Chunk1 and Chunk 2 are related because of '{{hints}}'. You can synthesize question about '{{hints}}' to use both of the chunks."
    elif answer_type == "table_as_answer":
        user_prompt = user_prompt.replace("{{Requirements}}", REQUIREMENTS_TABLE_ANSWER)
        user_prompt = user_prompt.replace("{{EXPLANATION_INFO}}", EXPLANATION_INFO_TABLE_ANSWER)
        user_prompt = user_prompt.replace("{{FORMAT}}", FORMAT_TABLE_ANSWER)
        user_prompt += "Remember: The synthesized question must be specific enough to be used to help a RAG system retrieve the document or context containing that table from a large corpus. You will not mention the 'what XYZ in the table' because your question must be general enough to be used as a question to ask in a large corpus. Also, avoid 'what is shown in the table' phrasing."
    else:  # default
        user_prompt = user_prompt.replace("{{Requirements}}", REQUIREMENTS_IMAGE_plus_TEXT_ANSWER)
        user_prompt = user_prompt.replace("{{EXPLANATION_INFO}}", EXPLANATION_INFO_IMAGE_plus_TEXT_ANSWER)
        user_prompt = user_prompt.replace("{{FORMAT}}", FORMAT_IMAGE_plus_TEXT_ANSWER)
        user_prompt += "\n\nHint: Chunk1 and Chunk 2 are related because of '{{hints}}'. You can synthesize question about '{{hints}}' to use both of the chunks."


    return user_prompt