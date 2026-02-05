import os, ast
from openai import OpenAI
MODEL = "gpt-4o"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


CLAIM_EXTRACTION_TEMPLATE_pt1 = """Your goal is to extract the claims/facts which are used to answer the given question one by one from the model response.

**Requirements**:
You will only extract claims or facts which are required to answer the questions. You will ignore useless information.

**Examples:**

**Question:** By 2028, what outcomes does SUBARU anticipate from its "Monozukuri Innovation" and "Value Creation" focus, specifically regarding BEV models and sales targets in the U.S.?
**Response:** By 2028, SUBARU anticipates achieving a lineup of eight BEV models and aims for U.S. sales of 400,000 BEVs as outcomes from its "Monozukuri Innovation" and "Value Creation" focus.'


**Output:**
```json
[
    {
        "claim": "SUBARU anticipates achieving a lineup of eight BEV models."
    },
    {
        "claim": "SUBARU aims for U.S. sales of 400,000 BEVs."
    },
]
```

**Question:** Why did SUBARU emphasize 'Monozukuri Innovation' and 'Value Creation' in its management strategy leading up to 2028, during the transition to battery electric vehicles?
**Response:** SUBARU emphasized 'Monozukuri Innovation' and 'Value Creation' in its management strategy leading up to 2028 to effectively navigate the transition to battery electric vehicles (BEVs) and ensure competitiveness in the evolving automotive industry.

**Output:**
```json
[
    {
        "claim": "For effectively navigating the transition to battery electric vehicles (BEVs)."
    },
    {
        "claim": "For ensuring competitiveness in the evolving automotive industry."
    },
]
```

Now it is your turn. You will use the above format.
"""

CORRECTNESS_TEMPLATE_matching_pt1 = """Your goal is to verify whether each claim is in the response.

**Requirements**:
These claims are used as ground-truth answer of the questions.
You need to verify them one by one and check whether they are in the response.

**Examples:**

**Question:** By 2028, what outcomes does SUBARU anticipate from its "Monozukuri Innovation" and "Value Creation" focus, specifically regarding BEV models and sales targets in the U.S.?
**Response:** By 2028, SUBARU anticipates achieving a lineup of eight BEV models and aims for U.S. sales of 400,000 BEVs as outcomes from its "Monozukuri Innovation" and "Value Creation" focus.'
**Claims:**
```json
[
    {
        "claim": "SUBARU anticipates achieving a lineup of eight BEV models."
    },
    {
        "claim": "SUBARU aims for U.S. sales of 400,000 BEVs."
    },
]
```

**Output:**
```json
[
    {
        "claim": "SUBARU anticipates achieving a lineup of eight BEV models.",
        "verdict": "True",
        "Reason": "This claim is equivalent with the claim in the Response: 'By 2028, SUBARU anticipates achieving a lineup of eight BEV models...'."
    },
    {
        "claim": "SUBARU aims for U.S. sales of 400,000 BEVs.",
        "verdict": "True",
        "Reason": "This claim is equivalent with the claim in the Response: '...and aims for U.S. sales of 400,000 BEVs as outcomes from its "Monozukuri Innovation" and "Value Creation" focus.'."
    }
]
```

**Question:** Why did SUBARU emphasize 'Monozukuri Innovation' and 'Value Creation' in its management strategy leading up to 2028, during the transition to battery electric vehicles?
**Response:** SUBARU focused on 'Monozukuri Innovation' and 'Value Creation' to support its electrification sales target and production structure updates toward 2030 and to navigate the transition from internal combustion engine vehicles to battery electric vehicles (BEVs). This focus aims to position SUBARU as a world-leading company in manufacturing and innovation during a time of profound transformation in the automotive industry.
**Claims:**
```json
[
    {
        "claim": "For effectively navigating the transition to battery electric vehicles (BEVs)."
    },
    {
        "claim": "For ensuring competitiveness in the evolving automotive industry."
    },
]
```

**Output:**
```json
[
    {
        "claim": "For effectively navigating the transition to battery electric vehicles (BEVs).",
        "verdict": "True",
        "Reason": "This claim is equivalent with the claim in the Response: '...navigate the transition from internal combustion engine vehicles to battery electric vehicles (BEVs)...'."
    },
    {
        "claim": "For ensuring competitiveness in the evolving automotive industry.",
        "verdict": "True",
        "Reason": "This claim is equivalent with the claim in the Response: '...This focus aims to position SUBARU as a world-leading company in manufacturing and innovation during a time of profound transformation in the automotive industry.'."
    }
]
```

Now it is your turn. You will use the above format.
"""

CLAIM_EXTRACTION_TEMPLATE_pt2 = """
**Question:** {question}
**Response:** {response}

**Output:**
"""

CORRECTNESS_TEMPLATE_matching_pt2 = """
**Question:** {question}
**Response:** {response}
**Claims:**
{claims}

**Output:**
"""

def call_llm(prompt):
    messages = [
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.85,
            )

    return response.choices[0].message.content


def get_recall(question, answer, ground_truth, retry_times=3):
    prompt_claims_gt = CLAIM_EXTRACTION_TEMPLATE_pt1 + CLAIM_EXTRACTION_TEMPLATE_pt2.format(question=question, response=ground_truth)
    for _ in range(retry_times):
        try:
            claims_gt = call_llm(prompt_claims_gt)
            prompt = CORRECTNESS_TEMPLATE_matching_pt1 + CORRECTNESS_TEMPLATE_matching_pt2.format(question=question, response=answer, claims=claims_gt)
            response = call_llm(prompt)
            response = response.replace("```json", "```").split("```")[1].strip()
            response = ast.literal_eval(response)

            correctness = []
            for element in response:
                if element["verdict"].lower() == "true":
                    correctness.append(1)
                else:
                    correctness.append(0)
            recall = sum(correctness) / len(correctness)

            return recall, response
        except Exception as error:
            print(f"Error: {error}")                    #There was no code here so file was invalid
    return 0.0, []

def get_precision(question, answer, ground_truth, retry_times=3):
    prompt_claims_answer = CLAIM_EXTRACTION_TEMPLATE_pt1 + CLAIM_EXTRACTION_TEMPLATE_pt2.format(question=question, response=answer)
    for _ in range(retry_times):
        try:
            claims_ans = call_llm(prompt_claims_answer)
            prompt = CORRECTNESS_TEMPLATE_matching_pt1 + CORRECTNESS_TEMPLATE_matching_pt2.format(question=question, response=ground_truth, claims=claims_ans)
            response = call_llm(prompt)
            response = response.replace("```json", "```").split("```")[1].strip()
            response = ast.literal_eval(response)

            correctness = []
            for element in response:
                if element["verdict"].lower() == "true":
                    correctness.append(1)
                else:
                    correctness.append(0)
            precision = sum(correctness) / len(correctness)

            return precision, response
        except Exception as error:
            print(f"Error: {error}")                    #There was no code here so file was invalid
    return 0.0, []

if __name__ == '__main__':
    question = "What were the market shares by total assets of the Portuguese banking sector in 2005?"
    answer = "The provided context does not include specific information about the market shares by total assets of the Portuguese banking sector in 2005."
    ground_truth = "The market shares by total assets in 2005 were as follows: BES had 30%, BPI had 25%, BCP had 20%, CGD had 15%, and Santander Totta had 10%."
    contexts = [
    "Case discussionThe Good, the Bad and the Ugly:\nThe fall and resolution of Banco Espírito Santo\n“We usually say that first comes the interest of our country, second, that of the institution and, only in third, that of shareholders”– Ricardo Espírito Santo Silva Salgado, CEO 1992-2014i\nOna hot Sunday night,August 3rd, the Portuguese central bank, Banco de Portugal (BdP), announced the resolution of BancoEspírito Santo (BES), which had fallen in disgrace after, a few days earlier, posting a €3.6bn loss in 2014Q2. The size of the losses consumed most of the existing capital base. Once the European Central Bank (ECB) made the decision to revoke BES's status as a counterparty for refinancing operations and requested that the bank paid back about €10 billion in ECB loans, BdP was forced to recognise BES' inability to make such repayment and put the bank under resolution.\nThe resolutioninvolved the separation of BES between a good and a bad bank. BES’ sound assets and most liabilities were transferred toa “transition bank”, or \"good bank\", which got fresh capital in the amount of €4.9bn from the Portuguese \"Bank Resolution Fund\". The century and half old BES was to be liquidated, keeping only those assets deemed “toxic” in its balance sheet. This \"bad bank\" also retained all liabilities to qualified shareholders, the bank's initial equity as well as BES' subordinated bonds. These were ugly news for those who had invested on thatsummer's BES rights issue. Or even those, including Goldman Sachs, who took long positions on the stock a few days before. How could the Espírito Santos(ES), the oldest banking dynasty of Portugal, have broughtthe bank to its knees?Espírito Santo: the originsii\nJosé Maria doEspírito Santo e Silva was born in Lisbon on 1850, to unknown parents. As was commonplace throughout Catholic societies, being an unwanted baby,he was dropped off at the door of the nearest convent. According to legend, he was actually the son of a nobleman and his father not only funded the boy’s education, but also provided a loan for him to kick-start his adult life. It is no legend that by 1869, aged 19 years, José Maria owned a small shop where he dealt in currency exchange and sold lottery tickets. Later he moved on to real estate investments, asset management and commercial banking.\nBy 1911, now a much respected and influent Lisbon banker, José Maria finally bought out the position of the only remaining associate in their commercial banking and securities trading firm. “Silva, Beirão, Pinto & Cia.” became “J.M. Espírito Santo Silva” – the first firmto bear his name. In 1915 his son José Ribeiro took charge of the business after his father’s unexpected death. In 1920, he oversaw a new transformation, as it became BancoEspírito Santo SARL. During World War I, the Portuguese economy struggled.With strong inflation,\nThis case study was prepared by Paulo Soares de Pinho.\nthe Escudo lost value very quickly, but the ES weathered the storm. In the early 1930’s the bank escaped relatively unscathed a serious banking crisis. The bank grew steadily, but after Ricardo, José Ribeiro’s younger brother, took over as leader, it really took off. In 1937, they merged with another bank, creating BancoEspírito Santo e Comercial de Lisboa(BESCL), who became the leading privately-owned bank in Portugal. Ricardo, by then, becamea close personal advisor to Oliveira Salazar, the sombre dictator who had just risen to power, and used his influence to grow the bank’s business.\nDuring World War II, Portugal maintained a “neutral” status, which made it a safe haven for Europe’s aristocracy and top businessmen to safeguard their assets and, often, their lives. Ricardo was not only a shrewd banker but also, with the help of his wife, Mary Cohen, a masterful hostess, welcomed to his home many aristocrats and industrialists seeking refuge in Portugal, including the Duke of Windsor. Ricardo, whom the allies suspected of pro- German tendencies, made the most of Portugal’s status, and during the war period, BESCL’s stock quadrupled in value.\nRicardo would eventually die young, in 1955, and was succeeded by abrother, Manuel RibeiroEspírito Santo, who would continue along the same tone, further developing international connections to wealthy families, such as the Rockefellers and Firestones, and to nobility, like the future King of Spain JuanCarlos and his father. In the 1960s, a golden era for the Portuguese economy dawned after its entrance in the European Free Trade Agreement (EFTA). BESCL continued to grow, beginning to channel cash into several different businesses, from textiles to oil and gas. Under the authoritarian regime of Salazar, most business decisions were in one way or another very conditioned by central government, and assets in all business fields were highly consolidated around a handful of large, well- connected conglomerates. For the large part, these were controlled by three traditional",
    "Mary Cohen 1903-1979Vera Cohen ESS\n1924-1998José Ribeiro ESS\n1895-1968/ Antonio Ricciardi\n1919-...Exhibit 2. Market shares (by total assets) of Portuguese banking sector<<fig-fd5ca9ef1240359d8400360f0d554a9e>>BES BPI BCP CGD Santander TottaSources: Company data/CMVM; Bureau Van Dijk (Bankscope); Banco de Portugal; Own calculationsExhibit 3. Portuguese domestic banks consolidated headline financials, 2007-14<<tab-13e2e0a99d7ff1c9957669963df39f1b>>\n2013 2012 2011 2010 2009 3,983 4,970 6,200 6,012 5,969 5,314 5,554 5,844 5,921 5,721 4,985 5,921 5,818 2,878 2,931 -2,733 -1,235 -1,516 917 452 55,206 51,189 44,448 46,616 35,386 233,066 248,483 246,496 261,992 270,345 Of which: Overdue 16,295 15,179 12,137 9,603 8,915 51,126 56,179 50,723 49,157 19,419 46,883 61,247 74,602 81,125 74,316 253,164 251,027 244,431 230,558 218,478 41,184 56,600 75,029 89,061 116,807 11.9% 11.3% 8.6% 8.3% 7.8% 12.3% 11.5% 8.7% 7.4% N/A 2008 7,013 5,833 3,592 -220 21,505 268,200 5,632 14,407 74,303 217,870 94,219 6.6% N/A 6,504 5,647 1,419 4,022Selected income statement indicatorsNet interest incomeOperating costsImpairmentsNet income\nSelected balance sheet indicatorsAvailable for sale financial assetsGross credit to clientsLiabilities to central banksLiabilities to other banksDeposits and other liabilities to clients\nDebt securities issuedSolvency indicatorsRegulatory capital ratioCore Tier I (BIS II) ratioNote: N/A = not available.Source: Banco de Portugal\n2007\n2,511\n22,640\n242,513\n5,731\n72,362\n195,604\n97,333\n7.0%N/A\nExhibit 4. Simplified GES/BES corporate structure, 2014José Manuel   António   Manuel   Mosqueira   ES  Ricciardi  Fernando ES  do Amaral  ES Control  56.5%  ES International  100%  Non‐financial   Rioforte  interests   of which:  100%  ES Saúde  51%  ES Irmãos  49.3%  24.9%  ESFG  (Exhibit 4a)  100%  55%  ES Financial   Portugal  45%  Tranquilidade   PARTRAN  100%  (Insurance)  25.1%  of which:  10%  BES Seguros  75%  25%  BES Group  (Exhibit 4b) RicardoSalgadoLuxembourg\nNote: ”Conselho Superior” members all held similar stakes in ES Control, close to but under 20%; except for the case of Manuel Fernando, who represents his mother’s stake, Maria do Carmo Moniz Galvão ES (in fact the largest shareholder with 19.4%).\nSources: BES; ESFG; BPI Equity Research; Press sourcesExhi ibit 4a. ESF FG banking subsidiarie© Commercial \"Wealthand Investment ManagementBanking +BESV— ESBD - BEST -Banque Espirito ES Bankers (Dubai) BEST BankSourc ce: ESFGExhi ibit 4b. BES S Group sub bsidiaries, 2 2014Sourc ce: BESSanto et dela Vénétie Limited ESBP-ESBPES— Banque Bank PanamaPrivée EspiritoSantoExhi ibit 5. Sove ereign yields s and mone ey market ra ates, 2009-1 14dan-1L Jul-1 spain ECE main refinancing Portuguese 2012 MBESSourc        Exhi 14 soasoa 1BEEEEEELEEE\nTESTEDSD ESS teevesensewace, dan-12 Jul-12 dan-13, Jul-13 Jen-14 —sermany 10-year sovereign bonds | rateJan-10 Jul-A0dan-1L Jul-1Jul-08 Jan-09: Jan-08JuLosGraeEURIBOR 3mes ees* EURIBOR 12mECE mainECE mainECE main refinancingce: BloombergSourcratio, Portu uguese dom -to-deposit Exhi mestic banks ibit 6. Loan s vs. BES, 2 2009-13Jubi4200920102011@Comesticbanks2013Sourc ce: BES; Banc co de PortugalExhibit 7. BES selected financial indicators, 2009-14\n30-06-2014 31-03-2014 31-12-2013 31-12-2012 31-12-2011 31-12-2010 31-12-2009\n<<tab-0a692ea0608e91a7e9662975f3080158>>\nKey balance sheet indicators Total assets* 93.419 96.150 93.342 97.765 98.589 105.540 105.917 Net assets 80.216 82.817 80.608 83.691 80.237 83.655 81.702 Gross credit to clients 51.281 51.001 49.722 50.399 51.211 55.713 50.531 Deposits 35.932 36.242 36.831 34.540 34.206 30.819 25.447 Debt securities issued 11.476 12.666 11.920 15.424 18.452 24.110 33.101 Solvency indicators Risk-weighted assets 60.169 62.268 57.332 61.681 65.385 65.097 68.802 CETI/CTI capital** 3036 6079 6084 6471 6020 5416 5232 (Total equity) 4244 7017 7049 7733 6192 6859 6344 CETI/CTI ratio** 5,0% 9,8% 10,6% 10,5% 9,2% 7,9% 8,0% Tier I ratio 5,0% 9,8% 10,4% 10,4% 9,4% 8,8% 8,3% Regulatory minimum*** 8,0% 8,0% 10,0% 10,0% 9,0% 8,0% 8,0% Liquidity indicators ECB funds (net) 7.432 8.346 5.414 6.897 8.677 3.929 -1.760 Repoable assets 21.593 23.783 20.912 22.256 18.881 10.823 5.553 LTD ratio 126% 129% 121% 137% 141% 165% 192% Credit quality indicators Overdue loans**** / Gross loans 6,4% 6,0% 5,7% 3,9% 2,7% 2,0% 1,6% Credit provisions / Gross loans 10,5% 7,2% 6,8% 5,3% 4,2% 3,4% 3,1%Cost of risk\n8,3%\n2,2%\n2,0%\n1,6%\n1,2%\n0,7%"
  ]

    recall, response = get_recall(question=question, answer=answer, ground_truth=ground_truth)
    precision, response = get_precision(question, answer, ground_truth + "".join(contexts), retry_times=3)

