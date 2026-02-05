MAIN_DOMAIN_PROMPTS ="""You are an expert in analyzing and classifying images from a single PDF file into a professional domain. Your task is to analyze the given image and determine its most appropriate domain.

The domain specifies the company or organization where the images were released.
Please analyze the images carefully and classify it according to the following domain structure:

1. Healthcare
   - Medical Diagnostics, Medical Treatment, Patient Care Management, Clinical Trial Analysis, Pharmaceuticals
   - Patient Care, Medical Records, Public Health, Clinical Research

2. Finance
   - Banking, Investment, Insurance, Taxation, Corporate Finance, Individual Finance
   - Fraud Detection, Algorithm Trading, Personalized Financial Advice, Risk Management, Regulatory Compliance
   - Asset Management, Hedge Funds, Private Equity, Venture Capital, Insurance, Financial Advisory, Wealth Management

3. Technology and Software
   - Software Development, IT Infrastructure, Cybersecurity, Data Analytics, Cloud Computing
   - Web Design, Programming, UI/UX Design, Testing

4. Commerce and Manufacturing
   - Retail and E-Commerce, Supply Chain Management, Manufacturing Design, Quality Assurance
   - Retail (e.g., Stores, E-commerce, Malls), Wholesale,
   - Manufacturing (e.g., Electronics, Automotive, Textiles, Pharmaceuticals, Ceramics, Machinery and Equipment Manufacturing)
   - Food and Beverage Production, Apparel Manufacturing
   - Chemical Production, Furniture Manufacturing
   - Logistics and Supply Chain Management

5. Customer Relationship Management
   - Customer Support, Sales Management, Client Onboarding, Customer Analytics
   - Customer Service, Sales Forecasting, Project Management

6. Education
   - Curriculum Development, Teaching and Instruction, E-Learning
   - Educational Administration, Higher Education

7. Legal
   - Contracts and Agreements, Intellectual Property, Litigation
   - Corporate Law, Privacy and Data Protection

8. Arts and Entertainment
    - Religion, Live Shows and Concerts, Theme Parks
    - Visual Arts, Performing Arts, Music, Film, Television, Theater
    - Dance, Photography, Literature, Animation, Graphic Design, Fashion, Fine Arts
    - Digital Media, Museums, Galleries, Cultural Heritage, Broadcasting, Event Management
    - Game Design, Stand-up Comedy, Streaming Services, Creative Writing

9. Government and Public Service
    - Law Enforcement, Public Administration, Regulations and Compliance
    - Defense and Security, Environment, Planning
    - Government Agencies, Fire Departments, Emergency Services
    - Military, Urban Planning, Environmental Protection, Civil Rights
    - Public Policy, Public Transportation, Local Government, International Organizations, Nonprofit Organizations, Public Works, Judiciary

10. Media
    - Broadcasting, Journalism, Publishing, Digital Media

11. Agriculture
    - Farming Techniques, Sustainable Agriculture, Crop Management
    - Livestock Management, Agricultural Trade

12. Construction Industry or Real Estate
    - Working Design, Map
    - Residential Construction, Commercial Construction, Industrial Construction, Infrastructure Development
    - Property Development, Property Management, Architecture, Urban Planning, Interior Design
    - Building Materials, Civil Engineering, Land Surveying, Real Estate Appraisal, Facility Management
    - Leasing, Real Estate Law

13. Energy Industry
    - Oil, Natural Gas, Coal, Nuclear Energy, Renewable Energy (Solar, Wind, Hydro, Geothermal, Biomass)
    - Energy Storage, Electricity Generation, Transmission & Distribution, Energy Trading
    - Energy Efficiency, Smart Grid Technology, Hydrogen Energy, Carbon Capture & Storage, Utility Companies, Energy Consulting

14. Transportation Industry
    - Automotive, Aviation, Shipping, Train and Railway
    - Freight and Logistics, Airlines, Shipping Lines, Trucking, Delivery Services
    - Ride-hailing Services (e.g., Uber, Lyft)

15. Engineering and Science
    - Mechanical Engineering, Electrical Engineering, Civil Engineering, Chemical Engineering
    - Computer Engineering, Aerospace Engineering, Biomedical Engineering, Environmental Engineering, Industrial Engineering
    - Physics, Chemistry, Biology, Mathematics, Earth Science, Astronomy, Environmental Science, Materials Science, Social Sciences

16. Others
    - Food and Drink, Lifestyles, Sports

For the given image, please provide:
1. The primary domain (most relevant)
2. Any secondary domains that might be relevant (if applicable)
3. A confidence score (0-1)

Consider the following aspects in your analysis:
- The domain specifies the company or organization where the images were released.
- Visual elements and their context
- Professional or industry-specific indicators
- Text or symbols present in the image
- Overall purpose and setting of the image
- Target audience and usage context
- Only use English

Your response should be structured as a JSON dictionary with the following format:
```
{
    "primary_domain": "Domain Name",
    "secondary_domains": ["Other relevant domain 1", "Other relevant domain 2"],
    "confidence_domain": confidence-score-in-float-number,
} 
```

Now, determine the domain for the following images:"""

MAIN_DOMAIN_PROMPTS_QUESTION = """Please analyze the image carefully and classify it according to the following domain structure. The domain specifies the company or organization where the images were released.

1. Healthcare
2. Finance
3. Technology and Software
4. Commerce and Manufacturing
5. Customer Relationship Management
6. Education
7. Legal
8. Arts and Entertainment
9. Government and Public Service
10. Media
11. Agriculture
12. Construction Industry or Real Estate
13. Energy Industry
14. Transportation
15. Engineering
16. Others

For the given image, please provide:
1. The primary domain (most relevant)
2. Any secondary domains that might be relevant (if applicable)
3. A confidence score (0-1)

Your response should be structured as a JSON dictionary with the following format:
```
{
    "primary_domain": "Domain Name",
    "secondary_domains": ["Other relevant domain 1", "Other relevant domain 2"],
    "confidence_domain": confidence-score-in-float-number,
}
```

Now, determine the domain for the following images:
"""