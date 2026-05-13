import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

ctx = "$('Merge Context').first().json"

for node in data["nodes"]:
    name = node.get("name", "")
    
    # Fix Send Morning Message
    if name == "Send Morning Message":
        body = node["parameters"].get("jsonBody", "")
        body = body.replace("919203580338", "{{ $json.phone }}")
        body = body.replace("Kapoor & Sons", "{{ $json.business_name }}")
        body = body.replace("Kapoor \\u0026 Sons", "{{ $json.business_name }}")
        node["parameters"]["jsonBody"] = body
        # Also fix URL and header
        url = node["parameters"].get("url", "")
        url = url.replace("919203580338", "{{ $json.phone }}")
        node["parameters"]["url"] = url
        print(f"  Fixed: {name}")

    # Fix ALL remaining in any parameter - do a full dump/replace
    params_str = json.dumps(node.get("parameters", {}))
    changed = False
    
    replacements = {
        "Kapoor \\u0026 Sons": f"{{{{ {ctx}.business_name }}}}",
        "Kapoor & Sons": f"{{{{ {ctx}.business_name }}}}",
        "Betul's oldest and most trusted electronics showroom (est. 1988)": f"{{{{ {ctx}.brand_positioning || {ctx}.tagline || 'trusted local business' }}}}",
        "Betul's oldest electronics showroom since 1988": f"{{{{ {ctx}.tagline || 'Your trusted partner' }}}}",
        "Betul, Madhya Pradesh, India": f"{{{{ {ctx}.location || 'India' }}}}",
        "Betul, Madhya Pradesh": f"{{{{ {ctx}.location || 'India' }}}}",
        "Betul, MP": f"{{{{ {ctx}.location }}}}",
        "in Betul": f"in {{{{ {ctx}.location || 'your area' }}}}",
        "Betul ka Sabse Trusted Electronics Store": f"{{{{ {ctx}.brand_positioning || 'Your Trusted Store' }}}}",
        "Trusted Electronics Store of Betul": f"{{{{ {ctx}.brand_positioning || 'Your Trusted Store' }}}}",
        "est. 1988": f"est. {{{{ {ctx}.established_year }}}}",
        "(est. 1988)": f"(est. {{{{ {ctx}.established_year }}}})",
        "Since 1988": f"Since {{{{ {ctx}.established_year }}}}",
        "A Trusted Name Since 1947": f"{{{{ {ctx}.tagline || 'Your Trusted Store' }}}}",
        "since 1947": f"since {{{{ {ctx}.established_year }}}}",
        "Since 1947": f"Since {{{{ {ctx}.established_year }}}}",
        "7697551111": f"{{{{ {ctx}.phone_display }}}}",
        "919203580338": f"{{{{ {ctx}.phone_primary }}}}",
        "PREMIUM ELECTRONICS SHOWROOM": f"{{{{ {ctx}.business_name }}}} - {{{{ {ctx}.brand_category || 'retail' }}}}",
        "Premium Electronics \\u0026 Appliance Showroom": f"{{{{ {ctx}.brand_positioning || 'Premium Store' }}}}",
        "Premium Electronics & Appliance Showroom": f"{{{{ {ctx}.brand_positioning || 'Premium Store' }}}}",
        "electronics and mobile shop": f"{{{{ {ctx}.brand_category || 'retail' }}}} business",
        "electronics showroom": f"{{{{ {ctx}.brand_category || 'retail' }}}} business",
        "They sell mobiles, TVs, ACs, washing machines, laptops, and all electronics.": "",
    }
    
    for old, new in replacements.items():
        if old in params_str:
            params_str = params_str.replace(old, new)
            changed = True
    
    if changed:
        node["parameters"] = json.loads(params_str)
        print(f"  Deep fixed: {name}")

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("\nDone!")
