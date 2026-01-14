import json

def extract_fields_from_file(text):
    #print("text-->", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = {
        "parties": [],
        "effective_date": None,
        "term": "",
        "governing_law": "",
        "payment_terms": "",
        "termination": "",
        "auto_renewal": False,
        "confidentiality": "",
        "indemnity": "",
        "liability_cap": {},  # {"amount": int, "currency": str}
        "signatories": []
    }

    for line in lines:
        if line.startswith("- Party A:"):
            result["parties"].append(line.split(":",1)[1].strip())
        elif line.startswith("- Party B:"):
            result["parties"].append(line.split(":",1)[1].strip())
        elif line.startswith("Effective Date:"):
            result["effective_date"] = line.split(":",1)[1].strip()
        elif line.startswith("Term:"):
            result["term"] = line.split(":",1)[1].strip()
        elif line.startswith("Governing Law:"):
            result["governing_law"] = line.split(":",1)[1].strip()
        elif line.startswith("Payment Terms:"):
            result["payment_terms"] = line.split(":",1)[1].strip()
        elif line.startswith("Termination:"):
            result["termination"] = line.split(":",1)[1].strip()
        elif line.startswith("Auto Renewal:"):
            val = line.split(":",1)[1].lower()
            result["auto_renewal"] = "automatically" in val
        elif line.startswith("Confidentiality:"):
            result["confidentiality"] = line.split(":",1)[1].strip()
        elif line.startswith("Indemnity:"):
            result["indemnity"] = line.split(":",1)[1].strip()
        elif line.startswith("Liability Cap:"):
            try:
                result["liability_cap"] = json.loads(line.split(":",1)[1].strip())
            except json.JSONDecodeError:
                result["liability_cap"] = {}
        elif line.startswith("- Name:"):
            name_part, title_part = line.split("Title:")
            result["signatories"].append({
                "name": name_part.replace("- Name:", "").strip(),
                "title": title_part.strip()
            })

    return result


text = '''
Title: Master Services Agreement between Gamma Solutions and Delta Partners
Document ID: 2
Parties:
- Party A: Gamma Solutions
- Party B: Delta Partners
Effective Date: 2026-02-01
Term: 24 months
Governing Law: California
Payment Terms: Invoices payable within 30 days
Termination: Either party may terminate with 60 days written notice
Auto Renewal: Automatically renews for 12 months unless canceled 30 days prior
Confidentiality: All confidential info shall be protected for 5 years
Indemnity: Party B indemnifies Party A against all claims arising from services
Liability Cap: {"amount": 1000000, "currency": "USD"}
Signatories:
- Name: Carol White, Title: CEO (Gamma Solutions)
- Name: Dave Brown, Title: CFO (Delta Partners)'''
#print(extract_fields_from_file(text))