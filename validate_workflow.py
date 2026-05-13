import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

# Build set of all node names
node_names = {n["name"] for n in data["nodes"]}
print(f"Total nodes: {len(node_names)}")

# Check connections
issues = []
for source, targets in data["connections"].items():
    if source not in node_names:
        issues.append(f"ORPHAN CONNECTION SOURCE: '{source}' (not a real node)")
    for conn_type, conn_list in targets.items():
        for conn_group in conn_list:
            for conn in conn_group:
                target = conn.get("node")
                if target and target not in node_names:
                    issues.append(f"BROKEN CONNECTION: '{source}' -> '{target}' (target doesn't exist)")

# Check for nodes referencing other nodes via $() expressions
for node in data["nodes"]:
    params = json.dumps(node.get("parameters", {}))
    import re
    refs = re.findall(r"\$\('([^']+)'\)", params)
    for ref in refs:
        if ref not in node_names:
            issues.append(f"BROKEN $() REF in '{node['name']}': references '{ref}' which doesn't exist")

if issues:
    print(f"\n⚠️  Found {len(issues)} issues:")
    for i in issues:
        print(f"  - {i}")
else:
    print("\n✅ All connections and references are valid!")

# List all node names for review
print("\n--- All nodes ---")
for n in data["nodes"]:
    print(f"  {n['name']} ({n['type']})")
