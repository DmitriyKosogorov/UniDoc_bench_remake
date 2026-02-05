DATE_PROMPT = """Analyze the given image and determine the year of creation based on its content type:
1. Newspaper: Extract the release year from visible dates or headlines.
2. Article or Papers: Identify the publication year from title, headers or footnotes.
3. Report: Detect the report year from the title page, metadata, or document structure.
4. Form: Find the issuance year from headers, stamps, or submission fields.
5. Notice: Identify the date of issuance or posting from the document.
6. Slides: Determine the presentation year from title slides, footers, or metadata.
7. Poster: Extract the publication or event year from the content or references.
8. Books or Textbooks: Identify the publication year from the copyright page or title page.
9. Notes: Estimate the creation year based on handwriting, context, or dated references.
10. Webpage: Detect the last updated year from visible timestamps or metadata.
11. Record: Identify the recorded year from official stamps, dates, or archival information.
12. Document: Find the creation or issuance year, if present, from headers, footers, or embedded data.

If a specific year is visible in text, timestamps, or objects, provide that year. If no explicit date is present, output "None". 
Output only the detected or estimated year directly."""