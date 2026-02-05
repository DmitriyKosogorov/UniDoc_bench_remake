REQUIREMENTS_FACTUAL_RETRIEVAL = """
You will synthesize questions which require retrieving a fact or entity from the chunks or images.
The following are subtypes you can choose from:
   - Definition / Explanation: Asks for the meaning of a term or concept.
   - Procedural / How-to: Describes a process or method.
   - Entity Lookup: Asks for names, locations, dates, numbers, etc.
   - Attribute Extraction: Asks about specific properties or features of an entity.
"""

REQUIREMENTS_COMPARISON = """
You will synthesize questions which require comparing two or more entities, processes, events, or objects to identify similarities, differences, or preferences in multiple chunks or images.
The following are subtypes you can choose from:
   - Difference Comparison: Highlights contrasting aspects between entities.
   - Relative Attribute Comparison: Compares entities based on a specific dimension (e.g. size, performance, cost).
   - Single image comparison: make comparisons for two entities or numbers in one image.
   - Preference Justification: Asks for a reasoned preference between two options.
"""

REQUIREMENTS_SUMMARIZATION = """
You will synthesize questions which require condensing information from multiple chunks into a shorter, coherent version while preserving key information.
The following are subtypes you can choose from:
   - Extractive Summarization: Selects key sentences or phrases directly from multiple chunks and images.
   - Visual Summarization: Summarizes content from charts, graphs, or infographics only.
   - Multimodal Summarization: Integrates text and image content into a unified summary.
"""

REQUIREMENTS_CAUSAL_REASONING = """
You will synthesize questions which require identifying causal relationships, underlying mechanisms, or logical justifications behind events, claims, or outcomes based on the provided contexts and images.
The following are subtypes you can choose from:
   - Causal Reasoning: Identifies reasons or causes behind a specific event or outcome.
   - Multi-hop Reasoning: Requires combining evidence from multiple chunks to infer the answer.
   - Goal / Intention Inference: Asks for the intent or goal behind an action.
   - Temporal Reasoning: Involves sequencing or understanding the timing of events.
"""

