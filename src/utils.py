import re
import ast
from typing import Dict, Any, Union
import json


def parse_llm_response(response: str) -> Dict[str, Any]:
    """
    Parse an LLM response string into a dictionary using regular expressions and ast.

    Args:
        response (str): The raw response string from the LLM

    Returns:
        Dict[str, Any]: Parsed dictionary from the response
    """
    code_block_pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
    match = re.search(code_block_pattern, response)

    if not match:
        json_pattern = r"\{[\s\S]*?\}"
        match = re.search(json_pattern, response)

    if not match:
        raise ValueError("No dictionary-like structure found in the response")

    json_str = match.group(1) if match.groups() else match.group(0)

    json_str = re.sub(
        r"//.*$", "", json_str, flags=re.MULTILINE
    )  # Remove single-line comments
    json_str = re.sub(
        r"/\*.*?\*/", "", json_str, flags=re.DOTALL
    )  # Remove multi-line comments

    json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

    json_str = re.sub(r"'", '"', json_str)

    try:
        return json.loads(json_str)

    except json.JSONDecodeError:
        try:
            return ast.literal_eval(json_str)
        except (SyntaxError, ValueError) as e:
            raise ValueError(f"Failed to parse response as dictionary: {str(e)}")