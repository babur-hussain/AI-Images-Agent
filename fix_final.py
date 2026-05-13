import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

ctx = "$('Merge Context').first().json"

for node in data["nodes"]:
    name = node.get("name", "")
    params_str = json.dumps(node.get("parameters", {}), ensure_ascii=False)
    changed = False
    
    reps = [
        ("Trusted by families across Betul", "Trusted by families in the area"),
        ("local Betul flavor", "local flavor"),
        ("local Betul/MP flavor", "local flavor"),
        ("KAPOOR & SONS", f"{{{{ {ctx}.business_name }}}}"),
        ("KAPOOR \\u0026 SONS", f"{{{{ {ctx}.business_name }}}}"),
    ]
    
    for old, new in reps:
        if old in params_str:
            params_str = params_str.replace(old, new)
            changed = True
    
    if changed:
        node["parameters"] = json.loads(params_str)
        print(f"  Fixed: {name}")

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("\nDone!")
