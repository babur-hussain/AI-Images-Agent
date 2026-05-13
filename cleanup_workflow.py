import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

# These are the node IDs/names from the Client Management API that should be removed
api_node_names = {
    "WH: Auth", "Verify Firebase Token", "Respond: Auth",
    "WH: Clients", "Parse Request", "Route",
    "PG: List", "Format List", "Respond: List",
    "PG: Create", "Respond: Create", "Respond: Error",
    "WH: Update", "Auth Update", "If OK?",
    "PG: Update", "Respond: Update", "Respond: Unauth",
    "WH: Toggle", "Auth Toggle", "PG: Toggle", "Respond: Toggle",
    "WH: Delete", "Auth Delete", "PG: Delete", "Respond: Delete"
}

# Count original nodes
original_count = len(data["nodes"])

# Filter out the API nodes
data["nodes"] = [n for n in data["nodes"] if n.get("name") not in api_node_names]

removed_count = original_count - len(data["nodes"])
print(f"Removed {removed_count} API nodes (from {original_count} to {len(data['nodes'])})")

# Remove connections for those nodes
for name in list(data["connections"].keys()):
    if name in api_node_names:
        del data["connections"][name]
        print(f"  Removed connection source: {name}")

# Also fix the broken SQL in the UPDATE query (openrouter_api_key=serp... and brand_colors=daily_cron...)
for node in data["nodes"]:
    if "query" in node.get("parameters", {}):
        q = node["parameters"]["query"]
        if "openrouter_api_key=serp_api_key" in q:
            q = q.replace("openrouter_api_key=serp_api_key=", "serp_api_key=")
            node["parameters"]["query"] = q
            print(f"  Fixed broken SQL in node: {node.get('name')}")
        if "brand_colors=daily_cron" in q:
            q = q.replace("brand_colors=daily_cron=", "daily_cron=")
            node["parameters"]["query"] = q
            print(f"  Fixed broken SQL in node: {node.get('name')}")

# Also clean openrouter/brand_colors from Merge Context jsCode
for node in data["nodes"]:
    if "jsCode" in node.get("parameters", {}):
        code = node["parameters"]["jsCode"]
        if "openrouter_api_key: session?.openrouter_api_key" in code:
            code = code.replace("  openrouter_api_key: session?.openrouter_api_key || '',\n", "")
            node["parameters"]["jsCode"] = code
            print(f"  Cleaned openrouter from jsCode in: {node.get('name')}")
        if "brand_colors: session?.brand_colors" in code:
            code = code.replace("  brand_colors: session?.brand_colors || {},\n", "")
            node["parameters"]["jsCode"] = code
            print(f"  Cleaned brand_colors from jsCode in: {node.get('name')}")

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("\nDone! Workflow is clean.")
print(f"Final node count: {len(data['nodes'])}")
print(f"Final connection count: {len(data['connections'])}")
