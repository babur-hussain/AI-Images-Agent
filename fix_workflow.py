import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

for node in data.get("nodes", []):
    if node.get("name") == "PG: Get Active Session" and "jsCode" in node.get("parameters", {}):
        code = node["parameters"]["jsCode"]
        code = code.replace("  openrouter_api_key: session?.openrouter_api_key || '',\\n", "")
        code = code.replace("  brand_colors: session?.brand_colors || {},\\n", "")
        node["parameters"]["jsCode"] = code
        
    # Remove openrouter and brand_colors from SQL
    if node.get("name") == "PG: Get Active Session" and "query" in node.get("parameters", {}):
        q = node["parameters"]["query"]
        q = q.replace("c.openrouter_api_key, ", "")
        q = q.replace("c.brand_colors, ", "")
        node["parameters"]["query"] = q
        
    # Remove openrouter and brand_colors from other API nodes (just in case)
    if "query" in node.get("parameters", {}):
        q = node["parameters"]["query"]
        q = q.replace("openrouter_api_key,", "")
        q = q.replace("'{{ $json.openrouter_api_key }}',", "")
        q = q.replace("brand_colors,", "")
        q = q.replace("'{{ JSON.stringify($json.brand_colors||{}) }}',", "")
        q = q.replace("openrouter_api_key='{{ $json.openrouter_api_key }}',", "")
        q = q.replace("brand_colors='{{ JSON.stringify($json.brand_colors||{}) }}',", "")
        node["parameters"]["query"] = q

    if node.get("name") == "Gemini: Prompt Enhancer Model" and "systemMessage" in node.get("parameters", {}):
        msg = node["parameters"]["systemMessage"]
        # Remove hardcoded color palette from system message
        msg = msg.replace("- Background: soft ivory white (#FAFAF7) or warm pearl (#F5F0E8) — NOT dark\\n- Headers/borders: rich royal blue (#1A3A6B)\\n- Highlights: warm gold (#C8972A)\\n- CTA badges: deep saffron (#E8621A)", 
                          "- Pick a dynamic, premium color palette that matches the product category, festival, or mood.\\n- Ensure high contrast and professional aesthetics.")
        node["parameters"]["systemMessage"] = msg

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("Workflow JSON cleaned up!")
