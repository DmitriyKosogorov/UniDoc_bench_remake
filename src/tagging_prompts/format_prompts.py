PDF_FORMAT_PROMPT = """Analyze the provided images from PDF contents and identify its format based on the following categories:

1. NEWSPAPERS
- Contains one or multiple articles on current events
- Regular publication format (daily, weekly, etc.)
- Intended for wide public readership.
- Professional journalistic writing style
- Structured layout with columns and sections
- Magazines or a single article are also included in this format
- Articles are written by reporters or editors, often with sources and quotes.

2. TEXTBOOKS
- Educational or instructional content
- Chapters and sections for learning
- Examples and exercises, such as quiz
- Reference materials and appendices
- Learning objectives and summaries

3. WEBPAGE
- Digital-first formatting
- Hyperlinks and navigation elements
- Interactive elements (if preserved in PDF)
- Web-specific formatting
- Often includes web addresses or URLs
- Digital media integration

4. FORM
- Structured template with designated fields or sections for input (e.g., name, date, address)
- Often includes checkboxes, text boxes, or selection options
- Often includes submission instructions
- Designed for data collection
- For example, Job application forms, Tax forms, Medical intake forms, Online contact forms

5. REPORT
- Multiple-page formal analysis or findings presentation
- Structured sections and subsections
- Data-driven content
- Executive summary or abstract or financial report
- Conclusions and recommendations
- Often includes tables, charts, or graphs

6. PAPERS
- In-depth scholarly or professional analysis
- Formal academic writing style
- Extensive research or argumentation
- Often include citations and references
- Often include abstract and introduction
- Often includes methodology and findings
- Often includes conclusions and implications

7. SLIDES
- Purpose: Designed for presentation
- Format: Multiple-page visual presentation format
- Often includes bullet points or concise text
- Often includes supporting images or diagrams
- Often includes limited text per slide
- Often includes speaker notes

8. POSTER
- Purpose: Presented at conferences or symposiums; Advertising an event or program; Informing or educating the public; Explaining a process or data-heavy concept visually.
- Format: Single-page comprehensive overview with Self-contained content
- Designed for display
- Suitable for standalone viewing

9. OTHERS
- Catch-all category for any format not matching above categories
- Notice, Record, Menu, Notes, Handbook, Tutorials
- Default category when format is unclear or mixed

For each PDF, provide:
1. The primary format (from the categories above)
2. A confidence score (0-1)
3. Any secondary format elements present

Additional Considerations:
- Categorize the images into one of the first eight categories first
- If none of the first eight works, then choose "OTHERS"
- Some documents may exhibit characteristics of multiple formats
- Consider the document's intended audience and purpose
- Look for format-specific elements and structures
- Consider the writing style and tone
- Evaluate the document's organization and layout
- Only reply with English

Your response should be structured as a JSON dictionary with the following format directly:
```json
{
    "primary_format": "PRIMARY_FORMAT",
    "secondary_formats": ["SECONDARY_FORMAT1", "SECONDARY_FORMAT2"],
    "confidence_format": confidence-score-in-float-number,
}
```

Now, determine the format for the following images in JSON dictionary:"""

PDF_FORMAT_PROMPT_QUESTION = """Formats are as follows,
1. NEWSPAPERS
2. TEXTBOOKS
3. WEBPAGE
4. FORM
5. REPORT
6. PAPERS
7. SLIDES
8. POSTER
9. OTHERS

Your response should be structured as a JSON dictionary with the following format directly:
```json
{
    "primary_format": "PRIMARY_FORMAT",
    "secondary_formats": ["SECONDARY_FORMAT1", "SECONDARY_FORMAT2"],
    "confidence_format": confidence-score-in-float-number,
}
```

Now, determine the format for the following images in JSON dictionary:"""