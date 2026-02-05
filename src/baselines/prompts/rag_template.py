DEFAULT_TEMPLATE="""We have provided context information below. \n"
---------------------
These are contexts in natual language format:
{context_str}
---------------------
"""

STRICT_TEMPLATE="""We have provided context information below.
---------------------
{context_str}
---------------------
You will verify the details in the question such as channel, time and names to make sure you can find an answer in the above context. If not, you should reply: I don't know.
If there is no sufficient information available from the above context such as time conflict or name mismatch, you should reply: I don't know.
Given the above context, provide a direct and concise answer in clear English of this question: {query_str}"""