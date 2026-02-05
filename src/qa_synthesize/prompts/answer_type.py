REQUIREMENTS_IMAGE_ANSWER = """
1. The synthesized question must be a single, self-contained question and must not use "and" to connect multiple questions.
2. The answer of the synthesized question will only be found in the image and cannot be found in any sentences in the chunks of the provided contexts.
3. The synthesized question require chunks/contexts to locate the image and cannot mention the image directly.
4. The synthesized question must be specific enough to locate the contexts in a large documentary corpus.
5. You will not mention the 'what XYZ in the graph/image/figure' because your question must be general enough to be used as a question to ask in a large corpus.
6. If you cannot synthesize a question which can only be answered in the image based on the above requirements, then do not synthesize anything.
7. You will also provide the the explanation why the answer can only be found in the provided images and can not be found in the provided chunks/contexts.
8. Avoid “what is shown in the image” phrasing, such as "what color/logo/name in the image."
9. Emphasize reasoning, aggregation, temporal comparison, or retrieval from source data. Imagine the question being asked without the image still making partial sense.
"""

EXPLANATION_INFO_IMAGE_ANSWER = """where '<<fig-aaaaa>>' is the image directly used to find the answer. '<explanation-image>' explains which part or information in the <<fig-aaaaa>> is the answer itself. '<explanation-chunks>' explains why the answer cannot be found in natual language text contexts.  '["answer-chunk1", "answer-chunk2", ...]' are the sentences in each chunk which are used to help with locate the image."""

FORMAT_IMAGE_ANSWER = """
{
    "questions": [
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "image": "<<fig-aaaaa>>",
            "explanation-image": "<explanation-image>",
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "image": "<<fig-aaaaa>>",
            "explanation-image": "<explanation-image>",
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "image": "<<fig-aaaaa>>",
            "explanation-image": "<explanation-image>",
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
    ]
}"""

REQUIREMENTS_TEXT_ANSWER = """
1. The 2-hop synthesized question must be a single, self-contained question and must not use "and" to connect multiple questions.
2. The answer of the synthesized question will only be found in the contexts.
3. The answer of the synthesized question cannot be found in the images.
4. The synthesized question require all the chunks in the contexts to be answered.
5. The synthesized question must be specific enough to locate the contexts in a large documentary corpus.
6. You will also provide the the explanation why the answer can only be found in the provided contexts.
"""

EXPLANATION_INFO_TEXT_ANSWER = """where '<explanation-chunks>' explains why the chunks are required for answering this question and how they formulate a multi-hop question. '["answer-chunk1", "answer-chunk2", ...]' are the sentences in each chunk which are used to answer the question."""

FORMAT_TEXT_ANSWER = """
{
    "questions": [
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
    ]
}"""


REQUIREMENTS_IMAGE_plus_TEXT_ANSWER = """
1. The 2-hop synthesized question require both of the provided contexts and images to answer.
2. The concise answer of the synthesized question will directly require information in the image to answer.
3. The concise answer of the synthesized question will also require information in the natural language contexts to answer.
4. All the chunks in the contexts are required to be used.
5. The synthesized question require contexts to locate the image and cannot mention the image directly.
6. The synthesized question must be specific enough to locate the contexts in a large documentary corpus.
7. You will also provide the the explanation which part of image is used to answer the answer and which sentence in the contexts is used to answer the question.
8. You will not mention the 'what XYZ in the graph' because your question must be general enough to be used as a question to ask in a large corpus.
9. If you cannot synthesize a question based on these requirements or directly use the information in the images, then do not synthesize anything.
10. If the image can be used to help visualization or illustration only, do not synthesize anything. If you cannot use all the chunks in the answer, then do not synthesize the question.
11. The synthesized question must be a single, self-contained question and must not use "and" to connect multiple questions.
"""

EXPLANATION_INFO_IMAGE_plus_TEXT_ANSWER = """where '<<fig-aaaaa>>' is the image directly used to answer the question. '<explanation-image>' explains which detailed information in the <<fig-aaaaa>> is required directly for answering this question and why without this image, the question cannot be fully answered. '<explanation-chunks>' explains why all the chunks are required for answering this question and how they formulate a multi-hop question. '["answer-chunk1", "answer-chunk2", ...]' are the sentences in each chunk which are used to answer the question."""

FORMAT_IMAGE_plus_TEXT_ANSWER = """
{
    "questions": [
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "image": "<<fig-aaaaa>>",
            "explanation-image": "<explanation-image>",
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "image": "<<fig-aaaaa>>",
            "explanation-image": "<explanation-image>",
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "image": "<<fig-aaaaa>>",
            "explanation-image": "<explanation-image>",
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
    ]
}"""

REQUIREMENTS_TABLE_ANSWER = """
1. The synthesized question must be a single, self-contained question and must not use "and" to connect multiple questions.
2. The answer of the synthesized question will only be found in the table (within <table> and </table>) and cannot be found in any sentences outside the <table> and </table> in the chunks of the provided contexts.
3. The synthesized question require chunks/contexts to locate the table and cannot mention the 'table' directly.
4. The synthesized question must be specific enough to locate the contexts in a large documentary corpus.
5. You will not mention the 'what XYZ in the table' because your question must be general enough to be used as a question to ask in a large corpus.
6. If you cannot synthesize a question which can only be answered in the table based on the above requirements, then do not synthesize anything.
7. You will also provide the the explanation why the answer can only be found in the provided tables and can not be found in the other parts of the provided chunks/contexts.
8. Emphasize reasoning, aggregation, temporal comparison, or retrieval from source data. Imagine the question being asked without the table still making partial sense.
"""

EXPLANATION_INFO_TABLE_ANSWER = """where '<<table-aaaaa>>' is the table directly used to find the answer. '<explanation-image>' explains which part or information in the <<tab-aaaaa>> is the answer itself. '<explanation-chunks>' explains why the answer cannot be found in natual language text contexts outside <table> and </table>.  '["answer-chunk1", "answer-chunk2", ...]' are the sentences in each chunk which are used to help with locate the table."""

FORMAT_TABLE_ANSWER = """
{
    "questions": [
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "image": "<<tab-aaaaa>>",
            "explanation-table": "<explanation-table>",
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        },
        {
            "question": "<synthesized-question>",
            "answer": "<answer-of-the-question>",
            "question_type": <chose from "factual_retrieval", "comparison", "summarization", and "causal_reasoning">,
            "image": "<<tab-aaaaa>>",
            "explanation-table": "<explanation-table>",
            "explanation-chunks": "<explanation-chunks>",
            "sentences-chunks-used": {"Chunk1": "sentences-chunk1", "Chunk2": "sentences-chunk2", ...]
        }
    ]
}"""