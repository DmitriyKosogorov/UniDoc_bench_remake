TEMPLATES_REPORT = """
**Factual Retrieval:**
    1. What was the [Metric] of [Entity] in [Time Period]/[Report or Doc]?
        - Example: What was the total revenue of Company A in the most recent fiscal year?
    2. Which [Entity Features] changed at [Entity] in [Time Period]/[Report or Doc]?
        - Example: Which leadership positions changed at Westwater Resources, Inc. in the reporting period?
    3. What was the largest/smallest/highest/lowest [Spending/Value] of [Entity] on [Category]?
        - Example: What was the largest single spending of MGM Resorts International on executive compensation in USD?
    4. How much did [Entity] spend/earn on [Category] (in [Currency]) during [Time Period]?
        - Example: How much did Pfizer spend on marketing in USD during 2022?
    5. What trend is reported in [Metric] for [Entity] over the past [N] years?
        - Example: What trend is reported in operating income for Zoom over the past 3 years?
    6. What is the projected [Metric] for [Entity] in [Future Time Period]?
        - Example: What is the projected revenue for NVIDIA in 2025?
    7. When/Where did [Entity/Event/Policy] happen or become active?
        - Example: When did Intel announce its new sustainability plan?
    8. Who is the [Role/Position] at [Entity] as of [Date/Time Period]?
        - Example: Who is the CEO of Microsoft as of 2025?
    9. How/What is [Term/Concept] defined in [Context/Industry/Field/Domain]?
        - Example: How is artificial intelligence defined in patient healthcare?
    10. How do you [Action/Process] in [Context/Field]?
        - Example: How do you calculate the ROI for a marketing campaign?
    11. What steps/process are involved in [Action/Process]?
        - Example: What is the Approval Process for replace the existing vinyl-framed windows of the Historic center located at 2146-2148 SE 12th Avenue?

**Comparison:**
    1. Which [Entity Type/Company] had a higher/lower [Metric]: [Entity1], [Entity2] or [Entity3], in [Time Period]?
        - Example: Which organization had a higher net income: A, B, or C, in FY2022?
    2. How much more did [Entity1] spend on [Metric Category] compared to [Entity2] in [Time Period]?
        - Example: How much more did Company A spend on R&D compared to Company B in 2022?
    3. How did [Metric] change for [Entity] from [Time A] to [Time B]?
        - Example: How did total debt change for Apple from 2021 to 2022?
    4. Which [Entity Type] experienced the most significant increase/decrease in [Metric] between [Time Period A] and [Time Period B]?
        - Example: Which country experienced the most significant increase in GDP between 2019 and 2020?
    5. What was the difference between [Company/Entity A] and [Company/Entity B] (in [Time Period/Contexts])?
        - Example: What was the difference in market share between Company X and Company Y in report od 2023?
    6. How does [Metric] for [Company A] compare to [Metric] for [Company B] in [Time Period/Contexts]?
        - Example: How does revenue for Tesla compare to revenue for Ford in 2022?
    7. Which [Entity] is better suited for [Task/Purpose] based on [Metric or Attribute] in [Time Period/Context]?
        - Example: Which company is better suited for long-term investment based on revenue stability in FY2022?

**Summarization:**
    1. What are the key points/findings/statements from the [Document on Topic] (regarding [Issue/entity])?
        - Example: What are the key findings from the 2023 quarterly earnings reports on the U.S. retail sector?
    2. Summarize the trends/key points/findings in [Document on Topic] about [Metric] over [Time Period]?
        - Example: Can you summarize the trend about smartphone adoption rates over the past decade?
    3. How would you summarize the overall impact of [Factor] on [Entity]'s [Metric] over [Time Period]?
        - Example: How would you summarize the overall impact of the economic downturn on General Motors’ sales in 2022?
    4. List the top [N] [Products/Services] contributing to [Entity]’s [Metric] in [Time Period].
        - Example: List the top 3 products contributing to Apple’s revenue in 2023.
    5. What are the top [N] [Factors/Events] identified for [Entity] in [Report/Document]?
        - Example: What are the top 5 risk factors identified for Meta in its latest financial filing?
    6. What risks or challenges or opportunities were identified for [Entity] in [Document]?
        - Example: What risks were identified for Amazon in its 2024 shareholder letter?
    7. What is the overall result/performance of [Entity] in [Report/Document]?
        - Example: What is the overall performance of Netflix in its 2022 financial result?

**Causal / Reasoning/ Why Questions:**
    1. Why did [Entity/Event] result in [Outcome]?
        - Example: Why did Apple’s Q2 profits decline in 2023?
    2. How did [Factor A] contribute to [Outcome B]?
        - Example: How did rising inflation contribute to reduced consumer spending?
    3. What was the goal behind [Entity]’s decision to [Action]?
        - Example: What was the goal behind Google acquiring DeepMind?
    4. Why did [Entity] implement [Policy/Strategy]?
        - Example: Why did Meta implement its remote work policy?
    5. What happened before/after [Event]?
        - Example: What happened after the launch of the iPhone 14?
    6. In what sequence did the following events occur: [Event A], [Event B], [Event C]?
        - Example: In what sequence did the policy changes, product recall, and public apology happen?
"""

TEMPLATES_LEGAL = """
**Factual Retrieval:**
    1. What are the key provisions or obligations in the [Contract/Agreement/Policy] between [Parties]?
        - Example: What are the confidentiality obligations in the employment contract between John Doe and XYZ Ltd.?
    2. Which laws or regulations apply to [Activity/Transaction] under [Jurisdiction]?
        - Example: Which data protection laws apply to cross-border data transfers under EU law?
    3. What are the legal requirements for [Process/Action] in [Jurisdiction/Context]?
        - Example: What are the legal requirements for terminating an employment contract in California?
    4. How is liability allocated in [Contract/Agreement] regarding [Issue]?
        - Example: How is liability allocated in the software licensing agreement between ABC Corp and DEF Ltd.?
    5. What precedent or case law governs [Legal Issue] in [Jurisdiction]?
        - Example: What case law governs non-compete agreements in New York State?
    6. What are the timelines or deadlines specified in [Legal Document/Procedure]?
        - Example: What are the statutory deadlines for filing an appeal in civil litigation in Texas?
    7. When was [Law/Regulation/Policy] enacted or last updated?
        - Example: When was the General Data Protection Regulation (GDPR) enacted?
    8. Who is responsible for compliance with [Law/Regulation] at [Organization]?
        - Example: Who is the Data Protection Officer at Acme Inc. as of 2024?
    9. How is [Legal Term/Concept] defined under [Jurisdiction] or in [Contract]?
        - Example: How is “force majeure” defined under the 2019 International Chamber of Commerce contract?
    10. How do you initiate [Legal Procedure] in [Jurisdiction]?
        - Example: How do you initiate arbitration proceedings under ICC rules?
    11. What steps must be followed to comply with [Regulation/Requirement]?
        - Example: What steps must be followed to comply with anti-money laundering regulations in the UK?

**Comparison:**
    1. Which jurisdiction has stricter [Law/Regulation] regarding [Topic]: [Jurisdiction A], [Jurisdiction B], or [Jurisdiction C]?
        - Example: Which jurisdiction has stricter data privacy laws: California, GDPR (EU), or Brazil?
    2. How do the dispute resolution clauses in [Contract A] and [Contract B] differ?
        - Example: How do the arbitration clauses in Amazon’s vendor agreement differ from those in eBay’s?
    3. What are the differences between [Law/Regulation A] and [Law/Regulation B] concerning [Topic]?
        - Example: What are the differences between the CCPA and GDPR in terms of consumer rights?
    4. How has the interpretation of [Legal Concept] evolved between [Case A] and [Case B]?
        - Example: How has the interpretation of “reasonable care” evolved between Smith v. Jones and Brown v. Davis?
    5. Which [Contract/Policy] provides greater protection for [Party] in [Context]?
        - Example: Which employment contract provides greater protection for the employee regarding severance?
    6. How do compliance requirements for [Industry A] compare to [Industry B]?
        - Example: How do data protection requirements compare between healthcare and financial services?
    7. Which legal strategy was more effective in [Case A] versus [Case B]?
        - Example: Which defense strategy was more effective in the two patent infringement cases?

**Summarization:**
    1. What are the main points or obligations outlined in the [Contract/Policy/Regulation]?
        - Example: What are the main obligations outlined in the GDPR for data controllers?
    2. Summarize the findings or rulings in [Legal Case/Decision] related to [Issue].
        - Example: Summarize the key rulings in the Supreme Court’s 2023 intellectual property case.
    3. How has [Law/Regulation] impacted [Industry/Entity] since its implementation?
        - Example: How has GDPR impacted tech companies since 2018?
    4. List the common legal risks identified in [Industry/Contract Type].
        - Example: List common legal risks identified in SaaS agreements.
    5. What challenges or compliance issues have been reported regarding [Regulation/Policy]?
        - Example: What compliance challenges have banks faced under the new AML regulations?
    6. What opportunities or benefits does [Law/Policy] offer to [Entity/Industry]?
        - Example: What opportunities does the new data localization law offer to cloud service providers?
    7. What is the current status or outcome of [Legal Proceeding/Investigation]?
        - Example: What is the current status of the antitrust investigation into Google’s advertising practices?

**Causal / Reasoning / Why Questions:**
    1. Why was [Law/Regulation/Policy] enacted or amended?
        - Example: Why was the California Consumer Privacy Act enacted?
    2. How did [Legal Action/Policy] influence [Outcome/Event]?
        - Example: How did the introduction of GDPR influence corporate data governance practices?
    3. What motivated [Entity] to pursue [Legal Action/Strategy]?
        - Example: What motivated Facebook to settle the data privacy lawsuit in 2021?
    4. Why did [Regulator/Court] rule in favor of/opposed to [Party]?
        - Example: Why did the court rule against the plaintiff in the breach of contract case?
    5. What were the consequences of [Legal Decision/Event]?
        - Example: What were the consequences of the Supreme Court ruling on patent eligibility?
    6. In what order did the key events in [Legal Case/Process] occur?
        - Example: In what order did the complaint filing, mediation, and trial take place in the employment dispute?
"""

TEMPLATES_COMMERCE_MANUFACTURING = """
**Factual Retrieval:**
    1. What are the specifications/features of [Product/Component] used by [Company]?
        - Example: What are the key specifications of the latest Intel microprocessor?
    2. Which quality standards or certifications does [Factory/Plant] comply with?
        - Example: Which ISO certifications does the Samsung semiconductor plant hold?
    3. What was the throughput/capacity of [Production Line/Facility] during [Time Period]?
        - Example: What was the daily production capacity of the Tesla battery factory in June 2024?
    4. How long does the [Manufacturing/Assembly] process take for [Product]?
        - Example: How long does the assembly process take for a Dell laptop model?
    5. What are the main causes of defects or failures in [Product/Component]?
        - Example: What are the primary causes of failure in lithium-ion batteries manufactured by Panasonic?
    6. What is the lead time for [Component/Product] from supplier to manufacturing site?
        - Example: What is the average lead time for semiconductor wafers from TSMC to Intel fabs?
    7. When was the [New Machine/Automation System] installed or upgraded at [Facility]?
        - Example: When was the new robotic arm system installed at Ford’s Michigan plant?
    8. Who manages the [Supply Chain/Quality Control/Logistics] at [Company]?
        - Example: Who is the head of supply chain management at DHL as of 2024?
    9. How is [Process/Technology] implemented in [Manufacturing/Logistics]?
        - Example: How is lean manufacturing applied in automotive assembly lines?
    10. How do you perform [Quality Check/Inventory Audit/Shipment Scheduling] in [Industry/Operation]?
        - Example: How do you perform a quality control audit in semiconductor manufacturing?
    11. What are the steps involved in [Order Fulfillment/Inventory Restocking/Product Recall]?
        - Example: What are the steps involved in recalling defective smartphones in retail?

**Comparison:**
    1. Which [Supplier/Factory/Product] has better [Quality/Yield/Delivery Time]: [Entity1], [Entity2], or [Entity3]?
        - Example: Which supplier delivers components with the lowest defect rate: Foxconn, Pegatron, or Flex?
    2. How does the production efficiency of [Plant A] compare to [Plant B]?
        - Example: How does the output per hour at Tesla’s Fremont plant compare to the Shanghai Gigafactory?
    3. What are the differences in logistics strategies between [Company A] and [Company B]?
        - Example: What are the differences in last-mile delivery strategies between Amazon and FedEx?
    4. How did the defect rate change for [Product] before and after [Process Change/Equipment Upgrade]?
        - Example: How did the smartphone defect rate change after Samsung implemented automated inspection?
    5. Which product model has the shortest assembly time: [Model A], [Model B], or [Model C]?
        - Example: Which Dell laptop model requires the least assembly time?
    6. How do the supply chain risks for [Product A] compare to [Product B]?
        - Example: How do supply chain risks for electric vehicles compare to traditional cars?
    7. Which logistics provider has better on-time delivery performance for [Region/Industry]?
        - Example: Which logistics provider had better on-time delivery rates in Europe in 2023?

**Summarization:**
    1. What are the key findings from the [Quality Report/Inspection] of [Facility/Product]?
        - Example: What are the key findings from the quality inspection report for Intel’s latest chip fabrication plant?
    2. Summarize the main challenges faced in [Supply Chain/Manufacturing] during [Event/Period].
        - Example: Summarize the main supply chain disruptions faced by automotive manufacturers during the 2023 chip shortage.
    3. How has the implementation of [Technology/Process] impacted [Production/Logistics]?
        - Example: How has the adoption of AI-driven demand forecasting impacted Amazon’s warehouse operations?
    4. List the top [N] causes of delays in [Manufacturing/Supply Chain/Delivery].
        - Example: List the top 3 causes of delays in the supply chain for consumer electronics in 2023.
    5. What risks or bottlenecks were identified in [Manufacturing Process/Distribution Network]?
        - Example: What bottlenecks were identified in Tesla’s battery production line?
    6. What are the main opportunities for efficiency improvement in [Operation/Process]?
        - Example: What opportunities exist to improve inventory turnover in e-commerce warehouses?
    7. What is the overall status/performance of [Facility/Product Line] after [Change/Event]?
        - Example: What is the overall production performance of Samsung’s semiconductor plant after automation upgrades?

**Causal / Reasoning/ Why Questions:**
    1. Why did [Production Delay/Quality Issue] occur in [Facility/Product Line]?
        - Example: Why did the production delay happen at Intel’s Arizona fab in 2023?
    2. How did [New Technology/Process] contribute to improved [Yield/Throughput]?
        - Example: How did the implementation of 5G connectivity improve factory automation efficiency?
    3. What was the reason behind [Company] choosing [Supplier/Technology]?
        - Example: What was the reason behind Apple choosing TSMC for its A-series chip manufacturing?
    4. Why did [Logistics Issue/Event] impact delivery times in [Region]?
        - Example: Why did port congestion cause shipment delays for electronics in the West Coast U.S.?
    5. What happened before/after [Equipment Upgrade/Product Recall]?
        - Example: What happened after Ford recalled defective airbags in 2022?
    6. In what sequence did the following events occur: [Supply Chain Disruption], [Production Halt], [Product Launch]?
        - Example: In what sequence did the semiconductor shortage, plant shutdown, and product launch happen at Nvidia?
"""

TEMPLATES_EDUCATION = """
**Factual Retrieval:**
    1. What are the key components of [Teaching Method/Strategy] used in [Course/Subject]?
        - Example: What are the key components of the flipped classroom method in high school math?
    2. Which learning outcomes are targeted by [Curriculum/Instructional Unit] in [Grade Level]?
        - Example: Which learning outcomes are targeted by the 9th-grade biology curriculum in California?
    3. What assessment types are used to measure [Skill/Competency] in [Course/Program]?
        - Example: What assessment types are used to measure critical thinking skills in undergraduate philosophy?
    4. How much time is allocated to [Topic/Module] in the [Curriculum/Instructional Plan]?
        - Example: How much time is allocated to teaching essay writing in the 10th-grade English curriculum?
    5. What teaching aids or technologies are employed in [Instructional Method/Classroom]?
        - Example: What teaching technologies are used in blended learning environments for language classes?
    6. What is the recommended class size for effective [Teaching Method/Activity]?
        - Example: What is the recommended class size for project-based learning in middle school science?
    7. When was [Curriculum/Instructional Program] last revised or updated?
        - Example: When was the national K-12 science curriculum last updated in 2022?
    8. Who developed or authored [Curriculum/Instructional Resource]?
        - Example: Who developed the Common Core State Standards for mathematics?
    9. How is [Pedagogical Concept/Strategy] defined or applied in [Educational Context]?
        - Example: How is differentiated instruction defined in elementary education?
    10. How do you implement [Teaching Technique/Assessment] in [Subject/Classroom]?
        - Example: How do you implement formative assessment in a high school history class?
    11. What steps are involved in designing [Curriculum/Instructional Unit]?
        - Example: What steps are involved in designing a science curriculum for middle school students?

**Comparison:**
    1. Which [Teaching Method/Assessment Type] is more effective for improving [Skill/Outcome]: [Method A], [Method B], or [Method C]?
        - Example: Which teaching method is more effective for improving reading comprehension: phonics, whole language, or balanced literacy?
    2. How do [Curriculum A] and [Curriculum B] differ in their approach to [Subject/Skill]?
        - Example: How do the Next Generation Science Standards differ from the previous state standards in teaching scientific inquiry?
    3. What are the differences in student engagement between [Instructional Strategy A] and [Instructional Strategy B]?
        - Example: What are the differences in student engagement between flipped classrooms and traditional lectures?
    4. How did student performance change after adopting [Teaching Method/Curriculum]?
        - Example: How did math test scores change after introducing project-based learning in grade 7?
    5. Which [Curriculum/Instructional Program] covers more [Topics/Competencies] in [Subject]?
        - Example: Which 8th-grade science curriculum covers more topics on ecology?
    6. How do teacher training programs in [Region A] compare to those in [Region B]?
        - Example: How do teacher professional development programs in Finland compare to those in the United States?
    7. Which assessment format better predicts student success in [Course/Grade]?
        - Example: Which assessment format better predicts student success in introductory college biology: multiple-choice or essays?

**Summarization:**
    1. What are the key findings from the [Research Study/Evaluation] on [Teaching Method/Curriculum]?
        - Example: What are the key findings from the 2023 study on the effectiveness of blended learning in middle school?
    2. Summarize the main trends in [Student Performance/Instructional Practices] over [Time Period].
        - Example: Summarize the main trends in student literacy rates over the past decade.
    3. How has the adoption of [Curriculum/Teaching Strategy] impacted [Student Outcomes/Engagement]?
        - Example: How has the adoption of inquiry-based science instruction impacted student engagement in high schools?
    4. List the top [N] challenges faced in implementing [Curriculum/Instructional Program].
        - Example: List the top 3 challenges faced in implementing remote learning during the COVID-19 pandemic.
    5. What opportunities for improvement were identified in [Teaching Practice/Program Evaluation]?
        - Example: What opportunities for improvement were identified in the evaluation of elementary math interventions?
    6. What are the most effective strategies for addressing [Learning Barrier/Need]?
        - Example: What are the most effective strategies for addressing dyslexia in early readers?
    7. What is the overall impact of [Educational Policy/Program] on [School/District/Student Group]?
        - Example: What is the overall impact of the new STEM curriculum on student enrollment in high schools?

**Causal / Reasoning/ Why Questions:**
    1. Why did [Teaching Method/Policy] lead to improved [Student Outcome/Engagement]?
        - Example: Why did the flipped classroom approach improve student engagement in math classes?
    2. How did [Curriculum Change/Instructional Strategy] influence [Student Performance/Behavior]?
        - Example: How did the introduction of social-emotional learning affect student behavior in elementary schools?
    3. What was the rationale behind adopting [Educational Program/Policy]?
        - Example: What was the rationale behind adopting competency-based education in the district?
    4. Why did [School/Teacher] implement [Technology/Teaching Technique]?
        - Example: Why did the school implement adaptive learning software in reading classes?
    5. What happened before/after the introduction of [Curriculum/Policy]?
        - Example: What happened after the district introduced later school start times?
    6. In what sequence did the following educational reforms occur: [Reform A], [Reform B], [Reform C]?
        - Example: In what sequence did the adoption of Common Core, standardized testing changes, and teacher evaluation reforms happen?
"""

TEMPLATES_ENERGY = """
**Factual Retrieval:**
    1. What equipment or systems are described in the documentation for [Facility/Project]?
        - Example: What energy storage systems are used in the Moss Landing facility?
    2. Which safety or environmental protocols are required under [Regulation/Permit]?
        - Example: Which environmental protocols are outlined in the offshore drilling permit for Shell?
    3. What is the operating capacity or technical rating of [Component/Unit] at [Location]?
        - Example: What is the rated capacity of the transmission line from Hoover Dam to Las Vegas?
    4. What materials, fuels, or technologies are used in [Energy Process/System]?
        - Example: What cooling method is used in Duke Energy’s nuclear reactors?
    5. What are the design constraints or limitations noted in [Blueprint/Design Document]?
        - Example: What design constraints are listed for the floating wind turbine prototype off the Maine coast?
    6. What is the timeline or sequence of events described in [Log/File/Project Plan]?
        - Example: What timeline is given for turbine maintenance in the April 2024 wind farm report?
    7. When was [Component/Infrastructure] installed, upgraded, or decommissioned?
        - Example: When was the substation near Bakersfield upgraded to handle higher load capacity?
    8. Who is responsible for [Inspection/Approval/Repair] in the context of [Facility or Regulatory Area]?
        - Example: Who is the designated site inspector for Chevron’s deepwater platform in the Gulf?
    9. How is [Process/System] carried out according to [Guide/Protocol]?
        - Example: How is high-voltage testing performed during substation commissioning?
    10. How do you initiate [Procedure/Compliance Action] under [Jurisdiction or Program]?
        - Example: How do you initiate an interconnection request under California’s Rule 21?
    11. What steps are required to verify [Status/Compliance/Performance] of [System or Project]?
        - Example: What steps are required to verify performance of grid-scale battery installations?

**Comparison:**
    1. Which [Technology/System/Practice] is more suitable for [Condition/Goal]: [Option A], [Option B], or [Option C]?
        - Example: Which energy storage system is more suitable for rapid discharge: flywheels, lithium-ion batteries, or flow batteries?
    2. How do safety protocols differ between [Operation A] and [Operation B]?
        - Example: How do safety requirements differ between onshore and offshore drilling operations?
    3. What are the key differences between [Infrastructure Design A] and [Design B] in [Context]?
        - Example: What are the key differences between HVDC and HVAC systems in long-distance power transmission?
    4. How did system performance change before and after [Retrofit/Upgrade/Event]?
        - Example: How did the efficiency of the solar farm change after panel reconfiguration in 2023?
    5. Which [Procedure/System/Unit] shows better performance or reliability under [Conditions]?
        - Example: Which backup generation system performs better in cold weather: diesel generators or natural gas turbines?
    6. How do regulatory expectations differ between [Region A] and [Region B] for [Activity]?
        - Example: How do emissions reporting requirements differ for methane leaks in Canada vs. the U.S.?
    7. Which incident response protocol led to faster resolution: [Event A] or [Event B]?
        - Example: Which outage event had a faster restoration timeline: the 2021 Texas grid failure or the 2020 California wildfire event?

**Summarization:**
    1. What are the key points, findings, or instructions outlined in [Technical/Regulatory Document]?
        - Example: What are the key findings in the 2024 wind turbine inspection checklist for Block Island?
    2. Summarize the challenges or corrective actions listed in [Maintenance Report/Incident Log].
        - Example: Summarize the root causes and responses in the transformer failure report at the PG&E facility.
    3. What operational risks or failures are discussed in [Field Report/Safety Audit]?
        - Example: What operational risks are documented in the offshore drilling platform audit from March 2024?
    4. List the main constraints, delays, or setbacks described in [Project Timeline/Progress Update].
        - Example: List the main construction delays in the Desert Sunlight solar expansion.
    5. What opportunities or solutions were proposed in [Proposal/Feasibility Study]?
        - Example: What grid flexibility solutions are proposed in the 2023 storage integration study by NREL?
    6. What are the recurring themes or patterns across [Multiple Logs/Reports]?
        - Example: What recurring failure patterns are observed across 2023 wind turbine inspection logs?
    7. What is the general status or outcome of [Energy Operation/Policy Enforcement/Infrastructure Deployment]?
        - Example: What is the current status of the HVDC transmission line from Wyoming to California?

**Causal / Reasoning / Why Questions:**
    1. Why did [System/Project] fail, stall, or underperform in [Context/Period]?
        - Example: Why did the geothermal plant in Nevada fail to meet its expected output in 2022?
    2. How did [Environmental/Technical/Regulatory Factor] contribute to [Operational Outcome/Event]?
        - Example: How did regulatory delays affect construction of offshore wind platforms off the New Jersey coast?
    3. What motivated [Agency/Operator] to implement [Change/Action]?
        - Example: What motivated FERC to revise interconnection procedures for energy storage systems?
    4. Why did [Protocol/Design] shift from [Approach A] to [Approach B]?
        - Example: Why did transmission planners shift from N-1 to probabilistic reliability models?
    5. What were the consequences of [Incident/Decision/Policy] for [Stakeholder or System]?
        - Example: What were the consequences of the oil pipeline rupture in North Dakota for tribal water systems?
    6. In what sequence did the following events or changes occur: [System Failure], [Policy Response], [Technical Upgrade]?
        - Example: In what sequence did the 2021 blackout, ERCOT reform, and new demand response programs unfold in Texas?
"""

TEMPLATES_CONSTRUCTION = """
**Factual Retrieval:**
    1. What materials or construction methods are specified for [Component/Structure] in [Document/Plan]?
        - Example: What materials are specified for foundation reinforcement in the structural drawing for Building A?
    2. Which codes, standards, or safety protocols apply to [Process/Material]?
        - Example: Which fire safety standards apply to insulation installation in multi-story buildings?
    3. What are the dimensions, tolerances, or load limits listed for [Component/System]?
        - Example: What are the load-bearing tolerances for the steel beams specified in the basement floor plan?
    4. What tools or equipment are required for [Construction Task or Survey Activity]?
        - Example: What tools are listed for horizontal alignment verification in highway surveying?
    5. What sequence of steps or workflow is outlined in [Procedure/Checklist/Method Statement]?
        - Example: What is the sequence for rebar placement and concrete pouring in the slab construction method?
    6. What location coordinates or elevation data are recorded for [Site/Feature]?
        - Example: What is the recorded elevation of plot corner 3 in the boundary survey?
    7. When was [Task/Inspection/Phase] completed, scheduled, or delayed?
        - Example: When was the plumbing rough-in inspection completed on Floor 2 of Building C?
    8. Who is assigned responsibility for [Task/Approval/Area] in the project plan or field notes?
        - Example: Who is the assigned contractor for structural framing on the west wing?
    9. How is [Term/Practice/Process] defined or implemented in the construction context?
        - Example: How is “cold joint” defined and addressed in concrete pouring documentation?
    10. How do you execute [Field Task/Verification/Survey Procedure] according to the field manual?
        - Example: How do you execute cross-sectioning for terrain slope measurement using total station?
    11. What steps are required to obtain approval for [Permit/Design/Variation]?
        - Example: What steps are required to get municipal approval for construction over a utility easement?

**Comparison:**
    1. Which [Construction Material/Method] is more suitable for [Goal/Condition]: [Option A], [Option B], or [Option C]?
        - Example: Which roofing method is more suitable for a coastal environment: EPDM, TPO, or metal panels?
    2. How do [Blueprint A] and [Blueprint B] differ in layout, materials, or structural design?
        - Example: How does the framing layout differ between the initial and revised floor plan of Building 5?
    3. What are the differences in workflow or resourcing between [Project A] and [Project B]?
        - Example: What are the differences in project timelines and subcontractor scheduling between Phase I and Phase II?
    4. How did the site measurements change before and after [Excavation/Backfill/Survey Update]?
        - Example: How did the site contour data change after the first round of grading in March?
    5. Which construction method leads to fewer delays or defects for [Structure Type]?
        - Example: Which method leads to fewer defects in retaining walls: cast-in-place or precast block systems?
    6. How do inspection requirements vary between [Jurisdiction A] and [Jurisdiction B]?
        - Example: How do foundation inspection protocols differ between San Francisco and Los Angeles counties?
    7. Which project management approach proved more efficient in [Case A] vs. [Case B]?
        - Example: Which coordination model worked better in school construction: centralized GC control or decentralized trade-led sequencing?

**Summarization:**
    1. What are the key requirements or specifications listed in [Drawing/Spec Sheet/Field Log]?
        - Example: What are the key anchorage requirements in the shear wall design detail?
    2. Summarize the status or findings from [Site Visit/Inspection/Meeting Notes].
        - Example: Summarize the findings from the electrical system walkthrough on July 6.
    3. What problems, risks, or issues are noted in [Project Update/Field Report]?
        - Example: What risks are identified in the July 2024 update for the underground utility trenching?
    4. List the critical tasks or dependencies for [Phase/Structure/Timeline] in the project plan.
        - Example: List the critical path dependencies for topping out the structural core of Tower A.
    5. What corrective actions or change orders are described in [Field Memo/RFI Response]?
        - Example: What corrective actions are detailed in response to RFI #204 about HVAC duct rerouting?
    6. What trends or recurring issues are reported in [Daily Logs/Progress Notes]?
        - Example: What recurring delays are noted in the concrete delivery logs for June 2024?
    7. What is the overall progress or outcome described in [Construction Summary/Closeout Docs]?
        - Example: What is the overall outcome of the civil works closeout report for the parking structure?

**Causal / Reasoning / Why Questions:**
    1. Why did [Design Choice/Method] lead to [Outcome/Issue] in [Project/Area]?
        - Example: Why did the choice of light-gauge steel studs lead to delays during interior wall framing?
    2. How did [Weather/Site/Design Factor] contribute to [Delay/Change/Failure]?
        - Example: How did unexpected groundwater levels contribute to delays in footing excavation?
    3. What was the rationale for adopting [Construction Approach/Material/Technology] in [Context]?
        - Example: What was the rationale for switching to modular construction in the dormitory expansion project?
    4. Why did [Inspector/Engineer] reject [Component/Procedure] in [Review/Inspection]?
        - Example: Why did the inspector reject the elevator shaft concrete pour on June 12?
    5. What were the consequences of [Error/Omission/Design Issue] for [Task or Schedule]?
        - Example: What were the consequences of the survey datum error on structural alignment in Zone 3?
    6. In what sequence did [Tasks/Delays/Inspections] occur for [Phase/Area]?
        - Example: In what sequence did the slab prep, rebar inspection, and pour occur for Podium Level 1?
"""

TEMPLATES_FINANCE = """
**Factual Retrieval:**
    1. What indicators, policies, or tools are described in the discussion of [Economic Topic/Financial Strategy]?
        - Example: What inflation indicators are cited in the ECB’s policy blog from June?
    2. Which markets, sectors, or instruments are emphasized in relation to [Trend/Event/Goal]?
        - Example: Which sectors are favored in the 2025 sustainable investing outlook?
    3. What key positions or exposures are taken by [Investor/Desk/Division] in response to [Condition/Event]?
        - Example: What position changes did the multi-asset team make in response to rising real yields?
    4. What assumptions, constraints, or parameters are specified in [Scenario/Strategy/Model]?
        - Example: What assumptions are used in the stress testing scenario for oil price shocks?
    5. When was [Policy/Event/Adjustment] implemented, and what immediate actions followed?
        - Example: When did the Bank of Japan change its yield curve control stance?
    6. Who oversees or initiates [Financial Decision/Policy/Investment Move] in the described context?
        - Example: Who approves short-term borrowing requests in the global treasury function?
    7. How is [Strategy/Instrument/Term] defined or operationalized in this context?
        - Example: How is "duration-neutral tilt" defined in the Q3 fixed income note?
    8. How do you carry out or execute [Action/Transaction/Plan] in [Financial Context]?
        - Example: How do you implement a covered call overlay in an income-focused portfolio?
    9. What are the procedural steps or controls listed for [Financial Task/Compliance/Change]?
        - Example: What steps are required to evaluate bond ladder rollovers in rising rates?

**Comparison:**
    1. How do [Strategies/Regions/Instruments] compare in terms of [Risk/Performance/Conditions]?
        - Example: How do TIPS and gold compare for inflation protection in the current macro setup?
    2. Which asset class, sector, or product is better suited for [Objective/Environment]?
        - Example: Which is better for income stability in retirement: dividend ETFs or bond ladders?
    3. What are the structural or tactical differences between [Financial Approaches]?
        - Example: What are the key differences between liability-driven investment and balanced allocation strategies?
    4. How did [Metric/Position/Exposure] change between [Period A] and [Period B]?
        - Example: How did corporate cash allocation to floating-rate debt shift over 2023?
    5. How do regulatory or monetary responses differ between [Jurisdictions]?
        - Example: How does Fed liquidity provision compare to ECB emergency facilities post-crisis?

**Summarization:**
    1. What are the key findings or takeaways from [Brief/Update/Policy/Strategy]?
        - Example: What are the key points in the tactical asset allocation update from July?
    2. Summarize the main market movements, themes, or risks discussed in [Note/Newsletter/Memo].
        - Example: Summarize the interest rate risk themes highlighted in the October bond outlook.
    3. What portfolio, liquidity, or policy adjustments are recommended or implemented?
        - Example: What rebalancing steps were taken in the client model portfolios in Q1?
    4. List the major economic risks or opportunities discussed in [Period/Event/Note].
        - Example: What macro risks are cited ahead of the U.S. election cycle?
    5. What are the key operational or structural features of [Product/Plan/Tool]?
        - Example: What are the structural features of the new drawdown facility described in the treasury toolkit?

**Causal / Reasoning / Why Questions:**
    1. Why did [Entity/Desk/Advisor] make [Move/Shift/Decision] in response to [Condition/Event]?
        - Example: Why did the balanced portfolio reduce international equity in Q2?
    2. How did [Macro Event/Regulatory Shift] influence [Positioning/Allocation/Operations]?
        - Example: How did the Basel III revisions alter corporate liquidity buffers?
    3. What drove the shift from [Approach A] to [Approach B] in [Context]?
        - Example: What drove the shift from risk-parity to volatility-targeting in multi-asset allocation?
    4. Why was [Instrument/Policy/Vehicle] introduced or phased out?
        - Example: Why was the internal netting structure retired in the 2024 treasury overhaul?
    5. What sequence of factors or events led to [Market Reaction/Portfolio Impact/Policy Result]?
        - Example: What sequence of events led to capital outflows from EM debt in late 2023?
"""

TEMPLATES_HEALTHCARE = """
**Factual Retrieval:**
    1. What symptoms, findings, or conditions were documented in [Patient Note/Clinical Record]?
        - Example: What symptoms were documented in the admission note for Patient ID 1384?
    2. Which medications or treatments were administered to [Patient/Group] during [Encounter/Trial Phase]?
        - Example: Which antibiotics were prescribed during the patient’s second hospital stay?
    3. What diagnostic tests were performed and what were the findings in [Case/Record]?
        - Example: What imaging tests were done for the patient with chest pain, and what were the results?
    4. What adverse events were reported in [Trial/Procedure]?
        - Example: What adverse events occurred during Phase II of the mRNA vaccine trial?
    5. What is the function or mechanism of [Device/Drug/Procedure] described in [Document]?
        - Example: What is the mechanism of the insulin pump described in the technical manual?
    6. What inclusion/exclusion criteria are used in [Study/Protocol]?
        - Example: What are the exclusion criteria in the Alzheimer’s disease clinical trial protocol?
    7. When was [Drug/Device/Procedure] approved, deployed, or used in [Case/Setting]?
        - Example: When was the automated blood pressure monitor used during the outpatient visit?
    8. Who performed or supervised [Procedure/Diagnosis/Trial] in [Document/Record]?
        - Example: Who performed the spinal tap on the patient admitted on March 5th?
    9. How is [Medical Term/Procedure] defined or described in [Document/Context]?
        - Example: How is “early-onset sepsis” defined in the neonatal care guideline?
    10. How do you perform [Procedure/Test] in [Setting]?
        - Example: How do you perform a 6-minute walk test in a pulmonary rehabilitation program?
    11. What steps or protocols are involved in [Clinical Pathway/Device Use]?
        - Example: What steps are involved in calibrating the portable ECG monitor for home use?

**Comparison:**
    1. Which [Treatment/Test/Intervention] showed higher efficacy or fewer side effects: [Option A], [Option B], or [Option C]?
        - Example: Which antidepressant had fewer reported side effects: sertraline, fluoxetine, or bupropion?
    2. How do diagnostic criteria differ between [Condition A] and [Condition B]?
        - Example: How do diagnostic criteria differ between Crohn’s disease and ulcerative colitis?
    3. What are the key differences in trial design between [Study A] and [Study B]?
        - Example: What are the differences in dosage schedules between Study 001 and Study 002 for the COVID booster?
    4. How did patient outcomes differ before and after [Treatment/Intervention]?
        - Example: How did patient mobility scores change before and after hip replacement?
    5. Which imaging modality is more accurate for detecting [Condition]?
        - Example: Which is more accurate for detecting pulmonary embolism: CT angiography or V/Q scan?
    6. How do device usage protocols differ across [Settings/Models]?
        - Example: How do calibration steps differ between the Gen-3 and Gen-4 glucose monitors?
    7. Which regulatory pathway was faster for [Drug/Device]: [Route A] or [Route B]?
        - Example: Which approval pathway was faster for the cancer drug: accelerated approval or breakthrough therapy?

**Summarization:**
    1. What are the key clinical findings or assessments from [Note/Encounter]?
        - Example: What are the key clinical findings from the ED discharge summary for Patient 5428?
    2. Summarize the results of [Trial/Procedure/Case Study].
        - Example: Summarize the results of the Phase III trial of the RSV vaccine.
    3. How did [Patient/Group] respond to [Treatment/Medication] over [Time Period]?
        - Example: How did the patient respond to corticosteroids during their 2-week ICU stay?
    4. List the major symptoms, treatments, and outcomes recorded in [Patient Record/Report].
        - Example: List the major symptoms and treatments noted in the oncology case report.
    5. What complications, limitations, or concerns were noted in [Procedure/Device Use/Trial]?
        - Example: What complications were reported during the laparoscopic cholecystectomy procedure?
    6. What are the key eligibility, enrollment, and outcome stats reported in [Study Summary]?
        - Example: What are the key enrollment stats in the CRISPR gene therapy trial?
    7. What is the overall prognosis or assessment given in [Report/Encounter]?
        - Example: What is the overall assessment in the neurologist’s consult note for the MS patient?

**Causal / Reasoning / Why Questions:**
    1. Why did [Patient/Group] develop [Condition/Event] after [Treatment/Exposure]?
        - Example: Why did the patient develop liver toxicity after the second dose of isoniazid?
    2. How did [Factor/Intervention] contribute to [Outcome/Improvement/Complication]?
        - Example: How did early mobilization contribute to faster recovery in post-surgical patients?
    3. What was the rationale behind choosing [Treatment/Device/Protocol] in [Case]?
        - Example: What was the rationale for using biologics instead of steroids in this Crohn’s patient?
    4. Why was [Device/Trial Arm] discontinued or modified during [Study/Procedure]?
        - Example: Why was the placebo arm discontinued during the Phase II trial?
    5. What occurred before/after [Clinical Event/Procedure/Change]?
        - Example: What happened after the patient's oxygen saturation dropped below 85%?
    6. In what sequence did the following clinical events occur: [Symptom A], [Intervention B], [Outcome C]?
        - Example: In what sequence did fever onset, antibiotic administration, and WBC normalization occur?
"""

TEMPLATES_ENG_SCI = """
**Factual Retrieval:**
    1. What are the key components, inputs, or modules used in [System/Design]?
        - Example: What are the key propulsion components used in the Falcon 9 launch system?
    2. Which standards or protocols govern [Process/Device] in [Field]?
        - Example: Which IEEE standards apply to Wi-Fi signal modulation in telecom systems?
    3. What are the parameters or performance characteristics of [Device/Model]?
        - Example: What are the voltage and power ratings for the STM32F4 microcontroller?
    4. What experimental setup or simulation configuration is described in [Document/Study]?
        - Example: What experimental setup was used to measure aerodynamic drag in the wind tunnel tests?
    5. What equations, models, or formulas are used to analyze [Phenomenon]?
        - Example: What equations are used to model thermal expansion in metal rods?
    6. What are the failure modes or safety limits noted for [Component/Material]?
        - Example: What are the fatigue limits of 7075-T6 aluminum alloy under cyclic loading?
    7. When was [Instrument/System/Tool] calibrated, tested, or deployed?
        - Example: When was the onboard navigation system on the satellite last tested?
    8. Who developed or validated [Algorithm/Model/Tool]?
        - Example: Who developed the Kalman filter algorithm used in aircraft tracking?
    9. How is [Process/Concept] defined or implemented in [Field or System]?
        - Example: How is entropy defined and calculated in statistical mechanics?
    10. How do you assemble, operate, or troubleshoot [Machine/System/Experiment]?
        - Example: How do you calibrate and operate a laser Doppler vibrometer?
    11. What steps are involved in designing or verifying [System/Component]?
        - Example: What steps are involved in verifying the structural integrity of a rocket payload bay?

**Comparison:**
    1. Which [Design/Model/Method] performs better under [Condition/Use Case]?
        - Example: Which antenna design performs better for low-Earth orbit communications: patch or helical?
    2. How do the properties of [Material/Component] differ between [Version A] and [Version B]?
        - Example: How do the tensile strengths of carbon fiber composites differ from aluminum alloys?
    3. What are the differences between [Theory A] and [Theory B] in explaining [Phenomenon]?
        - Example: What are the differences between Newtonian and relativistic mechanics in orbital calculations?
    4. How does performance change when [Parameter/Condition] is altered in [System]?
        - Example: How does signal-to-noise ratio change with bandwidth in a 5G communication link?
    5. Which modeling approach gives more accurate results for [Problem]?
        - Example: Which method gives more accurate results in fluid simulation: finite element or lattice Boltzmann?
    6. How do implementations of [Algorithm/Model] vary across [Platforms/Fields]?
        - Example: How does the implementation of FFT differ between digital signal processors and GPUs?
    7. Which statistical method is more appropriate for analyzing [Data Type/Experiment]?
        - Example: Which statistical test is more suitable for evaluating variance in machine failure rates?

**Summarization:**
    1. What are the main design principles or system behaviors described in [Document/Prototype]?
        - Example: What are the main design principles behind the reusable thermal protection system in the Dragon capsule?
    2. Summarize the results of [Experiment/Simulation] in terms of [Metric/Effect].
        - Example: Summarize the results of the CFD simulation in terms of pressure drop across the turbine blade.
    3. How did [Variable] affect [Outcome] in the analysis or test?
        - Example: How did increasing angular velocity affect stress distribution in the rotating shaft?
    4. List the most significant performance trade-offs or limitations mentioned in [Design/System].
        - Example: What are the major trade-offs of using PID controllers in quadcopter stabilization?
    5. What challenges or anomalies were reported in [System/Test Case]?
        - Example: What anomalies were encountered during the vacuum chamber test of the cubesat propulsion unit?
    6. What alternative approaches or optimizations were proposed for [Problem]?
        - Example: What optimizations were suggested to improve heat dissipation in the processor array?
    7. What are the key theoretical insights, assumptions, or simplifications used in [Study/Model]?
        - Example: What assumptions are made in the derivation of the Black-Scholes equation?

**Causal / Reasoning / Why Questions:**
    1. Why did [System/Test/Model] produce unexpected or suboptimal results?
        - Example: Why did the RF signal degrade rapidly during the satellite communication test?
    2. How did [Material/Design Parameter] influence [Performance/Outcome]?
        - Example: How did adding graphite fiber influence the tensile strength of the composite?
    3. What was the motivation behind selecting [Approach/Architecture] for [Design/Project]?
        - Example: What was the motivation behind selecting distributed control in the Mars rover design?
    4. Why was [Technique/Tool/Algorithm] chosen over other alternatives in [Context]?
        - Example: Why was k-means clustering chosen for fault detection in smart grids?
    5. What were the implications of [Experimental Outcome/Failure] for future iterations or versions?
        - Example: What were the implications of the failed nozzle separation in the static fire test?
    6. In what sequence did key events or computations occur in [Process/Simulation]?
        - Example: In what sequence did the finite element solver execute stress-strain iterations during load application?
"""

TEMPLATES_CRM = """
**Factual Retrieval:**
    1. What features or integrations does [CRM Platform/Product] support?
        - Example: What third-party integrations does Salesforce support for email marketing?
    2. Which customer segments or profiles are targeted by [Campaign/Strategy]?
        - Example: Which customer segments are prioritized in the recent onboarding campaign?
    3. What data sources feed into [Customer Analytics/Dashboard]?
        - Example: What data sources are used for the churn prediction model in HubSpot?
    4. How is [Customer Interaction/Support Process] handled in [Platform/Team]?
        - Example: How is escalation managed in the support service desk for Zendesk users?
    5. What are the steps in the [Customer Onboarding/Sales Pipeline] workflow?
        - Example: What are the steps in the customer onboarding process for new SaaS clients?
    6. What metrics or KPIs are tracked in [Sales Forecasting/Dashboard]?
        - Example: What KPIs are monitored in the Q2 sales pipeline forecasting report?
    7. When was [Feature/Integration/Update] released or last updated?
        - Example: When was the AI-powered lead scoring feature released in Dynamics 365?
    8. Who manages [Customer Account/Support Ticket/Integration] in [Team/Platform]?
        - Example: Who is responsible for managing VIP customer accounts in the support team?
    9. How is [Customer Data/Feedback] collected and processed in [Platform/Process]?
        - Example: How is customer feedback collected and analyzed in the NPS program?
    10. How do you configure or troubleshoot [CRM Feature/Integration]?
        - Example: How do you configure email automation workflows in HubSpot?
    11. What steps are involved in resolving [Support Issue/Customer Complaint]?
        - Example: What steps are followed to resolve a billing dispute in the service desk?

**Comparison:**
    1. Which CRM platform offers better [Feature/Capability]: [Platform A], [Platform B], or [Platform C]?
        - Example: Which platform offers better AI-driven customer insights: Salesforce, HubSpot, or Zoho CRM?
    2. How do customer retention rates compare between [Campaign A] and [Campaign B]?
        - Example: How do retention rates compare between the email nurture campaign and the referral program?
    3. What are the differences between [Sales Pipeline] stages in [Team A] and [Team B]?
        - Example: What are the differences in sales pipeline stages between inside sales and enterprise sales teams?
    4. How did customer satisfaction scores change after implementing [Feature/Process]?
        - Example: How did CSAT scores change after introducing live chat support?
    5. Which onboarding strategy results in faster time-to-value for customers?
        - Example: Which onboarding approach leads to faster product adoption: guided tutorials or personalized onboarding calls?
    6. How do analytics models for churn prediction differ between [Model A] and [Model B]?
        - Example: How do the logistic regression and random forest churn models differ in accuracy?
    7. Which support ticket resolution process reduces turnaround time more effectively?
        - Example: Which support workflow reduces average resolution time more: automated routing or manual triage?

**Summarization:**
    1. What are the main features or updates described in [Product Release/Integration Guide]?
        - Example: What are the main updates in the latest Salesforce Winter Release?
    2. Summarize the customer feedback themes from [Survey/Support Logs].
        - Example: Summarize the main customer complaints from the last quarter’s support tickets.
    3. What trends are observed in [Sales Pipeline/Customer Behavior] over [Time Period]?
        - Example: What trends are observed in upsell opportunities in Q1 2024?
    4. List the top challenges faced during [Customer Onboarding/Support Process].
        - Example: List the top 3 challenges faced during onboarding of enterprise customers.
    5. What opportunities for improving [Customer Experience/Support] were identified?
        - Example: What opportunities to improve support response times were found in the service desk audit?
    6. What are the key insights from [Customer Analytics Report/Market Research]?
        - Example: What key insights were revealed in the customer segmentation analysis?
    7. What is the current status or outcome of [Sales Forecast/CRM Implementation/Support Initiative]?
        - Example: What is the current status of the CRM platform migration project?

**Causal / Reasoning/ Why Questions:**
    1. Why did [Feature/Process/Strategy] improve [Customer Metric/Outcome]?
        - Example: Why did introducing AI lead scoring increase sales conversion rates?
    2. How did [Customer Behavior/Market Change] influence [Sales Pipeline/Support Volume]?
        - Example: How did the rise in subscription cancellations affect support ticket volume?
    3. What motivated the decision to implement [CRM Feature/Integration]?
        - Example: What motivated the company to implement multi-channel customer support?
    4. Why did [Team/Platform] choose [Sales/Support/Onboarding] approach?
        - Example: Why did the support team switch to a tiered escalation process?
    5. What were the consequences of [Technical Issue/Process Change] for customers?
        - Example: What were the consequences of the CRM downtime on customer satisfaction?
    6. In what order did the following CRM initiatives occur: [Feature Rollout], [Training], [Performance Improvement]?
        - Example: In what sequence did the rollout of the new dashboard, staff training, and sales performance increase happen?
"""


CHOOSE_TEMPLATE_PROMPT_SYSTEM = """
Given the following text contexts and images, choose the most suitable question templates from the provided list of templates. The templates will and the contexts and images will be used to synthesize the questions.

**Requirements:**
<requirements>
- First, choose the most suitable question category from "Factual Retrieval", "Comparison", "Summarization", "Causal / Reasoning/ Why Questions".
- Then, choose one or more suitable question templates from the category. If you cannot find any suitable templates, choose "None".
- Provide a brief explanation for your choice.
- The template should be able to answer the question based on the text contexts and images.
- The template should be able to handle the complexity of the question.
- The template should be able to handle the format of the text contexts and images.
</requirements>

**Format:**
- The output should be in the following format:
```
[
    {
        "question_category": "Factual Retrieval | Comparison | Summarization | Causal / Reasoning/ Why Questions",
        "question_templates": "Template 1",
        "explanation": "The explanation for the choice of question category and templates."
    },
    {
        "question_category": "Factual Retrieval | Comparison | Summarization | Causal / Reasoning/ Why Questions",
        "question_templates": "Template 2",
        "explanation": "The explanation for the choice of question category and templates."
    },
    ...
]
```"""

CHOOSE_TEMPLATE_PROMPT_USER = """
**Templates:**
{{TEMPLATES}}


Choose the most suitable question template from the provided list of templates. Return at most 3 templates. Try to cover more `question_category`.
Text contexts:
{text_contexts}
Images are as follows:
"""

import json
import base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

Contexts = ["<<fig-80a961247206cffc00d575b5be36fb93>> FY 2013-14 Actuals FY 2014-15 Actuals FY 2015-16 Actuals FY 2016-17 FY 2017-18 Projections Requested Even though no two audits are the same, the number of audits produced is an industry (ALGA) accepted performance metric as well as a performance metric reported by the Auditor\u2019s Office. The ALGA Benchmarking and Best Practices report states that \u201c\u2026slightly more than three quarters of respondents indicated their audit department used performance measures\u2026(and) 85% agree that the performance measures have been successfully integrated into ongoing management of the audit shop\u201d. The data indicates the Auditor\u2019s Office is producing less than one third of an audit department with 11-16 staff and approximately two thirds of what an audit department with 6-10 staff produce. CBO recognizes that the number of audits issued is not a perfect measure due to variation in scope. However, CBO strongly encourages audit services to review its performance against its peers and use performance management to ensure it is providing the highest quality services at the lowest possible cost. Decision Package Analysis & Recommendations IPR Asst. Program Manager to Full Time, AU_01, $69,870, 0.5 FTE This package requests that the current IPR Assistant Program Manager transition from 0.5 FTE to 1.0 FTE. This request addresses requirements set forth by the state in House Bill 2002 and by the U.S. Department of Justice (DOJ) settlement agreement. A key element of the DOJ settlement is that all investigations be complete within 180 days. To meet this, IPR must complete their portion within a 60-day time frame. IPR strives to complete 45% of cases in a 60- day time frame. The percent of (estimated) cases that are projected to meet that goal in FY 2016-17 fell 5 percentage points from 29% in FY 2015-16 down to 24% in FY 2016-17. These percentages are misleading as they do not adequately reflect changes in workload. Among other things, increased workload and process inefficiencies pose challenges to IPR achieving their goal. As expected, there has been an increase in the total volume of complaints. There are two kinds of complaints: community initiated and Portland Police Bureau (PPB) initiated complaints. Each complaint requires some measure of intake and analysis from the IPR team. Bureau Initated Complaints are Growing Faster than Community Initiated \u2022 The composition of complaints is important because community-initiated 600 complaints often involve force, 500 65% growth and the majority of these are 400 12% growth referred for investigation either by internal affairs or IPR. 300 \u2022 Bureau-initiated complaints 200 Number of PPB Initiated grew 65% in the last year while 100 Complaints community initiated complaints 0 FY 2015-16 Actuals FY 2016-17 Projection Number of Community Initiated Complaints grew 12%. \u2022 Currently, the assistant manager is responsible for reviewing the majority of bureau initiated complaints, which are more time intensive because they include: officer involved shootings, in-custody deaths, and interpersonal workplace conflicts. To offset the additional workload, Council approved two additional investigators in FY 2016-17 bringing the total number of investigators to seven; however, until recently, only six of the seven positions were filled. Legislation that took effect in January 2016 changed criteria such that a significantly higher portion of cases are investigated. The number of cases referred requiring investigation grew 76% in the last year.", "Requested Appropriations With the fiscal year half-way completed, departments have had the opportunity to re-evaluate their current operations and identify any unforeseen needs that have become known. Staff is requesting the Council\u2019s consideration of budget appropriation changes for the General Fund totaling $457,952 with a revenue offset of $391,152. As discussed below, the net cost of $66,800 from these appropriations can be absorbed within the current General Fund budget with no actual cost impact. The appropriations requested for the Wastewater Fund total $50,700 which is the before-mentioned generator carried over from FY 2018-19). Below is further detail on these requested appropriation changes and pending Council direction on these requests, staff will return to the Council at a subsequent meeting for formal approval of these change: City Management"]
img_path = "YOUR_DATA_PATH/selected_documents/by_class_finance_lang_english_pages_3_textp_85/Corporate_Finance_figures/5406059/figure-3-5.jpg"
fig = "<<fig-80a961247206cffc00d575b5be36fb93>>"
img = encode_image(img_path)

user_prompt = [
        {
            "type": "text",
            "text": CHOOSE_TEMPLATE_PROMPT_USER.replace("{text_contexts}", json.dumps(Contexts, indent=4)).replace("{{TEMPLATES}}", TEMPLATES_REPORT)
            + "\n\nThese are the tables and images in the above chunks:",
        }
    ]
user_prompt += [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img}", "name": f"This is the image for {fig} in the above context."},
            }
        ]

assistant_output = """```
[
    {
        "question_category": "Factual Retrieval",
        "question_templates": "What was the [Metric] of [Entity] in [Time Period]/[Report or Doc]?",
        "explanation": "This chart reports the number of audit reports issued by a specific audit service over several fiscal years, making it appropriate to ask for the metric value (number of audit reports) by year."
    },
    {
        "question_category": "Comparison",
        "question_templates": "How does [Metric] for \"[Company A]\" compare to [Metric] for \"[Company B]\" in [Time Period/Contexts]?",
        "explanation": "The chart contrasts the performance of the audit service with industry benchmarks (ALGA 11–15 Staff and ALGA 6–10 Staff), allowing for comparative analysis of audit output."
    },
    {
        "question_category": "Comparison",
        "question_templates": "How did [Metric] change for [Entity] from [Time A] to [Time B]?",
        "explanation": "This chart provides audit output across multiple fiscal years, enabling a temporal comparison of audit performance."
    },
    {
        "question_category": "Summarization",
        "question_templates": "Summarize the trends/key points/findings in [Document on Topic] about [Metric] over [Time Period]?",
        "explanation": "The image reflects a pattern of consistently lower audit outputs compared to industry standards over time, making it suitable for summarizing overall trends."
    },
    {
        "question_category": "Causal / Reasoning/ Why Questions",
        "question_templates": "Why did [Entity/Event] result in [Outcome]?",
        "explanation": "Given that the audit service's output is below industry averages, one could explore the reasons behind this underperformance."
    }
]
```
"""

MESSAGE_WITH_EXAMPLE = [
        {
            "role": "system",
            "content": CHOOSE_TEMPLATE_PROMPT_SYSTEM,
        },
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assistant_output},
    ]


def choose_fixed_templates(domain_name):
    if "legal" in domain_name.lower():
        return TEMPLATES_LEGAL
    elif "commerce" in domain_name.lower():
        return TEMPLATES_COMMERCE_MANUFACTURING
    elif "education" in domain_name.lower():
        return TEMPLATES_EDUCATION
    elif "energy" in domain_name.lower():
        return TEMPLATES_ENERGY
    elif "construction" in domain_name.lower():
        return TEMPLATES_CONSTRUCTION
    elif "finance" in domain_name.lower():
        return TEMPLATES_FINANCE
    elif "health" in domain_name.lower():
        return TEMPLATES_HEALTHCARE
    elif "engineering" in domain_name.lower():
        return TEMPLATES_ENG_SCI
    elif "crm" in domain_name.lower():
        return TEMPLATES_CRM
    else:
        return TEMPLATES_REPORT




        