import json

domain_dict = {
  "Healthcare": [
    "Patient Care",
    "Medical Records",
    "Pharmaceuticals",
    "Public Health",
    "Clinical Research"
  ],
  "Finance": [
    "Banking",
    "Investment",
    "Insurance",
    "Taxation",
    "Corporate Finance",
    "Financial Planning"
  ],
  "Technology and Software": [
    "Software Development",
    "IT Infrastructure",
    "Cybersecurity",
    "Data Science",
    "Cloud Computing",
    "Networking",
    "Artificial Intelligence"
  ],
  "Commerce and Manufacturing": [
    "Retail and E-Commerce",
    "Supply Chain Management",
    "Manufacturing Processes",
    "Quality Assurance",
    "Procurement"
  ],
  "Customer Relationship Management (CRM)": [
    "Customer Support",
    "Sales Management",
    "Client Onboarding",
    "Customer Analytics",
    "Feedback and Surveys",
    "Loyalty Programs"
  ],
  "Marketing": [
    "Advertising",
    "Digital Marketing",
    "Content Marketing",
    "Market Research",
    "Social Media Marketing",
    "Public Relations"
  ],
  "Scientific Research and Development": [
    "Laboratory Research",
    "Product Innovation",
    "Clinical Trials",
    "Academic Research",
    "Grant Proposals"
  ],
  "Education": [
    "Curriculum Development",
    "Teaching and Instruction",
    "E-Learning",
    "Educational Administration",
    "Higher Education"
  ],
  "Legal": [
    "Contracts and Agreements",
    "Intellectual Property",
    "Litigation",
    "Corporate Law",
    "Privacy and Data Protection"
  ],
  "Arts and Entertainment": [
    "Music",
    "Film and Television",
    "Visual Arts",
    "Literature",
    "Gaming"
  ],
  "Government": [
    "Legislation",
    "Public Administration",
    "Regulations and Compliance",
    "Defense and Security"
  ],
  "Media": [
    "Broadcasting",
    "Journalism",
    "Publishing",
    "Radio and Television",
    "Digital Media"
  ],
  "Entertainment": [
    "Live Shows and Concerts",
    "Theme Parks and Attractions",
    "Streaming Platforms",
    "Comics and Graphic Novels",
    "Celebrity Culture"
  ],
  "Agriculture": [
    "Farming Techniques",
    "Sustainable Agriculture",
    "Crop Management",
    "Livestock Management",
    "Agricultural Trade"
  ],
  "Others": [
  ]
}

domain_dict = json.dumps(domain_dict, indent=4)

question = """You will be given a set of images, all from a single file. Your task is to determine the most appropriate domain and subdomain based on the predefined dictionary below.

**Domain and Subdomain Dictionary:**
{domain_dict}

**Instructions**
1. Select the most relevant domain and subdomain from the dictionary.
2. Ensure that your choice directly relates to the content of the images.


**Output**
1. The response should strictly be in the form ["DOMAIN", "SUBDOMAIN"].
2. The first element must be the domain (one of the keys in the dictionary).
3. The second element must be the corresponding subdomain (one of the values under the selected domain).
4. Do not include extra explanations or text.


Now, determine the domain and subdomain for the following images:
"""

DOMAIN_QUESTION = question.format(domain_dict=domain_dict)