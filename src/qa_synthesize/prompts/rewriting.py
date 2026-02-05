REWRITE_Q_PROMPT = """You are tasked with rewriting the following question in two different ways, using only the provided Contexts and without hallucinating any information.

**Date** {{current_date}}

**Your tasks:**

1. **Specific Rewrite**: Make the question more specific by adding or substituting keywords that clearly tie the question to the Contexts, such that it would likely only retrieve this document from a large corpus. Maintain the original meaning and ensure the rewritten question still leads to the same correct answer. Only add as few keywords as possible, such as one to make the question specific, not too general.
2. **Obscured Rewrite**: Rewrite the Specific Rewrite question using indirect or paraphrased language to reduce keyword overlapping with the original question, while still staying faithful to the Contexts and retaining all necessary information to make the question answerable. Do not remove essential details. The goal is to reduce lexical overlap, not accuracy.

**Requirements:**
- Do not hallucinate or invent facts not found in the Contexts.
- Do not remove any critical content required to answer the question.
- Avoid any phrasing that refers to the source (e.g., "as shown in the document", "in the context", "in the image", "in figure", "in table", "in diagram", etc.).
- The rewritten questions must be fully standalone and fluent.
- Use only information from the Contexts — do not generalize or speculate.
- Only add essential keywords and avoid adding too many keywords to the question.
- Do not add "regarding ...' to make the scope smaller and more specific.

**After rewriting**, check whether the original answer is still fully correct for both rewritten versions.  
If the original answer becomes partially or fully incorrect, set `"answer_wrong"` to `"True"`, otherwise `"False"`.

**Output Format:**
Return a JSON dictionary with the following keys and definitions:
```json
{
  "specific_question": (string) "A more specific version of the original question that includes clear, uniquely identifying keywords grounded in the provided Contexts. This version should increase the likelihood of retrieving only the relevant document from a large corpus. - Avoid any phrasing that refers to the source (e.g., "as shown in the document", "in the context", "in the image", "in figure", "in table", "in diagram", etc.).",
  "obscured_question": (string) "A paraphrased version of the original question that avoids exact or easily matched keywords, while remaining faithful to the meaning and factual content of the Contexts. This version should be less likely to match based on keyword retrieval alone. - Avoid any phrasing that refers to the source (e.g., "as shown in the document", "in the context", "in the image", "in figure", "in table", "in diagram", etc.).",
  "answer_wrong": "(string; either `"True"` or `"False"`) Indicates whether the original answer is still fully correct for both rewritten questions. Use `"True"` if the rewritten questions cause the original answer to become partially or fully incorrect; otherwise, use `"False"."
}
```

**Example:**
- Original Question: "What is the revenue growth shown in Figure 3 in 2024's report?"
- Transformed Output:
```json
{
  "specific_question": "What is the revenue growth for Company XYZ in 2024?",
  "obscured_question": "How did the XYZ's financial outcomes change in the previous year?",
  "answer_wrong": "False"
}
```

- Original Question: "What is the median differential rate between hurdle rates and costs of capital for cyclical and non-cyclical firms?"
- Transformed Output:
```json
{
  "specific_question": "What is the median differential rate between hurdle rates and costs of capital for cyclical and non-cyclical firms in the S&P 500 according to the Corporate Finance Advisory?",
  "obscured_question": "Within the Corporate Finance Advisory, what is the median gap between required rates of return and capital costs for firms in the S&P 500 that are economically sensitive compared to those in more stable sectors?",
  "answer_wrong": "False"
}
```
"""