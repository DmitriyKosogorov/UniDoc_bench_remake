PDF_MODALITY_PROMPT = """Analyze the provided images from PDF content and identify the following modalities:

1. FIGURE
- Look for labeled visual elements (e.g., "Figure 1", "Fig. 2")
- Identify graphs, charts, diagrams, or plots
- Check for accompanying captions or explanatory text
- Consider the context and purpose of the visual element
- Look for data visualization elements

2. IMAGE
- Identify standalone photographs, or digital renderings
- Look for visual elements without data visualization components
- Check for decorative or illustrative pictures
- Consider the absence of annotations or labels
- Look for natural or artistic visual content

3. DRAWING
- Identify manually or digitally created illustrations
- Look for technical drawings or blueprints
- Check for artistic sketches or illustrations
- Look for hand-drawn or digitally drawn elements

4. TEXT
- Identify paragraphs, sentences, and words
- Look for narrative or descriptive content
- Check for headings, subheadings, and body text
- Consider the formatting and structure
- Look for continuous text blocks

5. TABLE
- Identify structured data in rows and columns
- Look for tabular information
- Check for headers and data cells
- Consider the presence of grid lines or borders
- Look for organized data presentation

6. FORMULA
- Identify mathematical or scientific equations
- Look for mathematical symbols and operators
- Check for chemical formulas or scientific notation
- Consider the presence of variables and constants
- Look for standardized mathematical expressions

For each identified element, provide:
1. The modality types (FIGURE, IMAGE, DRAWING, TEXT, TABLE, or FORMULA)
2. A confidence score (0-1)

Additional Considerations:
- Some elements may belong to multiple modalities (e.g., a figure containing both an image and text)
- Consider the hierarchical relationship between elements
- Pay attention to the document's overall structure and formatting
- Consider the purpose and context of each element
- Look for cross-references or citations between elements
- Only use English

Your response should be structured as a JSON dictionary with the following format directly:
```json
{
    "modalities": ["PRIMARY_MODALITY", "SECONDARY_MODALITY1", "SECONDARY_MODALITY2"],
    "confidence": confidence-score-in-float-number,
}
```

Now, determine the modalities for the following images:"""

PDF_MODALITY_PROMPT_QUESTION = """Analyze the provided images from PDF content and identify the following modalities:

1. FIGURE
2. IMAGE
3. DRAWING
4. TEXT
5. TABLE
6. FORMULA

Your response should be structured as a JSON dictionary with the following format directly:
```json
{
    "modalities": ["PRIMARY_MODALITY", "SECONDARY_MODALITY1", "SECONDARY_MODALITY2"],
    "confidence_modalities": confidence-score-in-float-number,
}
```

Now, determine the modalities for the following images:"""