FACT_EXTRACTION_PROMPT = """You are given a question along with the answer. Your task is to analyze the the answer and extract all the facts into a list.

Input Format:

- Question: A question that is being asked based on the context.
- Answer: The current answer to the question.

Output Format:

Return a JSON object with the following structure:

```json
{
  "facts": ["Fact 1", "Fact 2", ...],  // List of facts which are required to answer the question in the Answer
}
```

Instructions:
- The facts indicate some specific number, or relations, or claim or facts to answer the question.
- Ignore those useless information to answer the question.

**Example:**

Input:
- Question: "What is the financial results for fiscal year 2019 of Salesforce?"
- Answer: "Salesforce's financial performance for fiscal year 2019 (ending January 31, 2019) was marked by significant growth: Total Revenue: $13.28 billion, a 26% increase year-over-year. Subscription and Support Revenue: $12.41 billion, up 27% year-over-year."

Output:

```json
{
  "facts": ["Total Revenue: $13.28 billion", "Total Revenue:a 26% increase year-over-year", "Subscription and Support Revenue: $12.41 billion, up 27% year-over-year."],
}
````

Now it is your turn.1

Input:
- Question: "{{question}}"
- Answer: "{{answer}}"

Output:
"""
CHUNK_GROUND_PROMPT = """You are given a context and a question along with a current answer. Your task is to analyze the context to determine if part or all of the current answer can be found within it. If you find matching sentences, return them. If no part of the current answer is found in the context, return `None`. Additionally, if there are other parts of the context that can be used to improve or modify the current answer, return these sentences as extra proof.

Input Format:

- Context: A passage of text that provides information related to the question.
- Question: A question that is being asked based on the context.
- Current Answer: A list of facts in the current answer to the question, which may or may not be fully supported by the context.

Output Format:

Return a JSON object with the following structure:

```json
{
  "found_sentences": ["Sentence 1", "Sentence 2", ...],  // List of full sentences from the context that fully match to one of the facts in the current answer
  "extra_proof": ["Sentence 1", "Sentence 2", ...],  // List of extra sentences from the context that can be used to answer the question.
}
```

Instructions:

1. Identify Matching Sentences:
   - Search the context for sentences that match part or all the facts in the current answer.
   - If matches are found, list them in the `found_sentences` array.
   - Return a full sentence, not only a phrase or few words.
   - The sentence must support one or multiple facts fully in the answer.

2. Identify Extra Proof:
   - If there are additional sentences of the context that can be used to improve the current answer, return them.

3. Return None:
   - If no part of the current answer is found in the context, set `found_sentences` to [].
   - If no more parts of the current contexts can be used to answer the question, set `extra_proof` to [].


**Example:**

Input:
- Context: "The sun rises in the east and sets in the west. The Earth revolves around the sun."
- Question: "Where does the sun rise?"
- Current Answer: ["The sun rises in the east."]

Output:

```json
{
  "found_sentences": ["The sun rises in the east and sets in the west."],
  "extra_proof": []
}
```

Input:
- Context: "The sun rises in the east and sets in the west. The Earth revolves around the sun."
- Question: "Where does the moon rise?"
- Current Answer: "The Moon rises in the eastern part of the sky."

Output:
```json
{
  "found_sentences": [],
  "extra_proof": []
}
```

Now it is your turn. `found_sentences` must be full sentences, end with '.'.

Input:
- Context: "{{chunk}}"
- Question: "{{question}}"
- Current Answer: "{{answer}}"

Output:
"""

IMAGE_GROUND_PROMPT = """You are given some textual contexts, a question, a current answer, and an image. Your task is to verify whether the image is required to obtain the current answer, or if the answer can be obtained from the textual context alone. If the image is required, explain why it is necessary by identifying the specific facts in the image that contribute to the answer.

Input Format:
- Textual Contexts: One or more text passages that may help answer the question.
- Image: An image that provides information related to the question.
- Question: A question that is being asked based on the image.
- Current Answer: The current answer to the question, which may or may not be fully supported by the image.

Output Format:

Return a JSON object with the following structure:

```json
{
  "image_required": "True" | "False",
  "reason": "Explanation of image_required label",
  "matched_facts": ["Fact 1", "Fact 2", ...]  // Facts from the image that are essential to derive the answer
}

```

Instructions:

1. Check if Textual Contexts Alone Are Sufficient:
    - Determine whether the current answer can be entirely inferred from the text alone.
    - If the current answer can be entirely inferred from the text alone and the image is not required, set "image_required" to "False", and leave "matched_facts" [] and explain why the image is not required.

2. Determine if Image Is Required:
    - If the text does not fully support the answer, inspect the image.
    - If the image contains essential facts needed to derive the answer that are not present in the text, set "image_required" to "True".
    - Provide a reason explaining why the text is insufficient and what the image contributes.
    - A list of specific 'matched_facts' found in the image that directly support the answer.

3. What Counts as a “Matched Fact”:
    - A matched fact should be a verifiable claim or detail in the image that is necessary to justify or derive the answer.
    - Do not list illustrative or decorative elements unless they are directly tied to answering the question.



Input:
- Contexts: "{{contexts}}"
- Question: "{{question}}"
- Current Answer: "{{answer}}"
- Image: The image is as follows.
"""

TABLE_GROUND_PROMPT = """You are given some textual contexts, a question, a current answer, and a table. Your task is to verify whether the table is required to obtain the current answer, or if the answer can be obtained from the textual context alone. If the image is required, explain why it is necessary by identifying the specific facts in the table that contribute to the answer.

Input Format:
- Textual Contexts: One or more text passages that may help answer the question.
- Table: An image of the table that provides information related to the question.
- Question: A question that is being asked based on the image.
- Current Answer: The current answer to the question, which may or may not be fully supported by the image.

Output Format:

Return a JSON object with the following structure:

```json
{
  "table_required": "True" | "False",
  "reason": "Explanation of table_required label",
  "matched_facts": ["Fact 1", "Fact 2", ...]  // Facts from the table that are essential to derive the answer
}

```

Instructions:

1. Check if Textual Contexts outside the table Alone Are Sufficient:
    - Determine whether the current answer can be entirely inferred from the text alone.
    - If the current answer can be entirely inferred from the text alone and the table is not required, set "table_required" to "False", and leave "matched_facts" [] and explain why the table is not required.
    - All the texts within <table> and </table> are part of table and not considered as 'Textual Contexts outside the table'.

2. Determine if Table Is Required:
    - If the text does not fully support the answer, inspect the image of the table.
    - If the image of the table contains essential facts needed to derive the answer that are not present in the text, set "table_required" to "True".
    - Provide a reason explaining why the text is insufficient and what the table contributes.
    - A list of specific 'matched_facts' found in the table that directly support the answer.
    - The table might be irrelevant or not required to answer the question. If not required, set "table_required" to "False"

3. What Counts as a “Matched Fact”:
    - A matched fact should be a verifiable claim or detail in the image that is necessary to justify or derive the answer.
    - Do not list illustrative or decorative elements unless they are directly tied to answering the question.

Input:
- Contexts: "{{contexts}}"
- Question: "{{question}}"
- Current Answer: "{{answer}}"
- Table: The image of the table is as follows.
"""

ANSWER_FULL_PROMPT = """You are given a context and a question along with a current answer. Your task is to verify if the entire current answer can be found within the context. If the entire answer is present, return the exact sentences from the context. If the answer cannot be fully found in the context, return [].

Input Format:

- Context: A passage of text that provides information related to the question.
- Question: A question that is being asked based on the context.
- Current Answer: The current answer to the question, which needs to be verified against the context.

Output Format:

Return a JSON object with the following structure:

```json
{
  "facts": ["Fact 1", "Fact 2", ...],              // Individual factual claims from the Current Answer
  "found_sentences": ["Sentence 1", "Sentence 2"], // Sentences from the Context that support the facts
  "verification_result": "result",                 // One of: "Full match", "Partial match", or "No Match"
  "explanation": "explain what are missing for partial match or no match"
}
```

Instructions:

1. Extract facts: Break the Current Answer into distinct facts or claims. Each fact should represent a single piece of information — e.g., a number, a fact, a claim, one relationship, or detail.

2. Match Facts to Context:
   - Search the Context for sentences that support each extracted fact.
   - Determine the verification_result:
       - "Full match": All facts from the Current Answer are found in the Context.
       - "Partial match": Some facts are found, but others are missing.
       - "No Match": None of the facts can be found.

**Example:**

Input:
- Context: ["The sun rises in the east and sets in the west.", "The Earth revolves around the sun."]
- Question: "Where does the sun rise and set?"
- Current Answer: "The sun rises in the east. The sun sets in the west."

Output:
```json
{ "facts": ["The sun rises in the east.", "The sun sets in the west."]
  "found_sentences": ["The sun rises in the east and sets in the west."],
  "verification_result": "Full match"
}
```

Now it is your turn.

Input:
- Context: "{{chunk}}"
- Question: "{{question}}"
- Current Answer: "{{answer}}"

Output:
"""

VQA_FILTER_PROMPT = """You are given a list of questions. Your task is to filter out and exclude any question that is Visual Question Answering (VQA) style.

A question is considered VQA-style if:

1. It refers directly to visual elements (e.g., "in the image", "in the photo", "shown above", "in the logo").
2. The answer can be obtained only by inspecting the pixels of an image (e.g., identifying objects, colors, positions, counting, color, logo, signature).
3. It focuses on purely visual recognition rather than reasoning, retrieval, or external knowledge.

Examples of VQA-style questions:

**Question**: "What is the person doing in the image?"
**VQA-style**: True

**Question**: "How many dogs are in the picture?"
**VQA-style**: True

**Question**: "What is the signature on the Independent Auditors' Report?"
**VQA-style**: True

**Question**: "What is the web address to log into the LH Portal?"
**VQA-style**: True

**Question**: "What company logo is used as an example?"
**VQA-style**: True

**Question**: "What visual style is employed for section dividers?"
**VQA-style**: True

**Question**: "What are the two colors used for the conference theme?"
**VQA-style**: True

**Question**: "What design element is used as a visual placeholder?"
**VQA-style**: True

Examples of Non-VQA-style questions:

**Question**: "What industries are represented in the Tableau usage data provided?"
**VQA-style**: False

**Question**: "Which telecommunications company is associated with customer personalization strategies?"
**VQA-style**: False

**Question**: "What are the main roles and positions involved in the Pulse AP Adoption study at Tableau?"
**VQA-style**: False

**Question**: "What is the increase in appliance sales compared to the prior period?"
**VQA-style**: False

Now it is your turn.

**Question**: {{question}}
**VQA-style**:"""