from ragas.testset.graph import KnowledgeGraph
from ragas.testset.graph import Node, NodeType
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from ragas.testset.transforms import default_transforms, apply_transforms
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
import argparse

if __name__ == "__main__":
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name_str", type=str, required=True, help="name of the subdomain"
    )
    parser.add_argument("--database_path", type=str, required=True, help="Database folder path")
    args = parser.parse_args()
    '''
    args={'name_str':'experimental_entry', 'database_path':'/home/user/RAG/UniDoc_bench/UniDoc-Bench/data/experimental'}
    loader = DirectoryLoader(args.database_path, glob="**/*.txt", loader_cls=TextLoader)

    text_splitter = SemanticChunker(OpenAIEmbeddings())
    docs = loader.load()


    kg = KnowledgeGraph()
    for doc in docs[:50000]:
        if "<<tab" in doc.page_content or "<<fig" in doc.page_content:
            kg.nodes.append(
                Node(
                    type=NodeType.DOCUMENT,
                    properties={
                        "page_content": doc.page_content,
                        "document_metadata": doc.metadata,
                    },
                )
            )

    generator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o"))
    generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

    from ragas.testset.transforms.extractors import NERExtractor
    from ragas.testset.transforms.extractors.llm_based import NERPrompt
    from ragas.testset.transforms import KeyphrasesExtractor, Parallel
    from ragas.testset.transforms.relationship_builders import (
        OverlapScoreBuilder,
        JaccardSimilarityBuilder,
    )

    instruction_ner = """Extract the named entities from the given text, limiting the output to the top entities. Ensure the number of entities does not exceed the specified maximum.
    
    **Common Types of Entities:**
    
    1. **Human Name (Person)**
       - Examples: *Elon Musk*, *Marie Curie*
    
    2. **Organization**
       - Examples: *Apple Inc.*, *United Nations*
    
    3. **Location**
       - Examples: *New York*, *Mount Everest*, *Japan*
    
    4. **Product**
       - Examples: *iPhone 15*, *Tesla Model S*, *Coca-Cola*
    
    5. **Event**
       - Examples: *Olympic Games 2024*, *WWDC 2023*, *World War II*
    
    6. **Concept**
       - Examples: *Quantum Computing*, *Climate Change*
    
    7. **Date/Time Expression**
       - Examples: *April 10, 2025*, *Q1 2024*, *yesterday*
    
    8. **Work of Art / Creative Work**
       - Examples: *The Godfather*, *The Mona Lisa*, *Harry Potter*
    
    9. **Facility / Landmark**
       - Examples: *Eiffel Tower*, *Stanford University*, *Golden Gate Bridge*
    
    10. **Numerical/Code Identifiers**
        - Examples: *ISBN 978-3-16-148410-0*, *Product ID 12345*, *AAPL (stock ticker)*
    """

    ner_prompt = NERPrompt()
    ner_prompt.instruction = instruction_ner

    rel_builder = OverlapScoreBuilder(distance_threshold=0.95)
    trans = [
        Parallel(
            KeyphrasesExtractor(max_num=15),
        ),
        Parallel(
            OverlapScoreBuilder(distance_threshold=0.95, property_name="keyphrases"),
        ),
    ]

    apply_transforms(kg, trans)

    output_path = f"YOUR_OUTPUT_PATH/kg/{args.name_str}_database.json"  # e.g., "/path/to/output/kg"
    kg.save(output_path)
