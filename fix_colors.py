import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

for node in data.get("nodes", []):
    if "systemMessage" in node.get("parameters", {}):
        msg = node["parameters"]["systemMessage"]
        if "COLOR PALETTE" in msg:
            # Replace the hardcoded colors in Gemini: Prompt Enhancer Model
            start_idx = msg.find("COLOR PALETTE")
            end_idx = msg.find("BILINGUAL HINDI + ENGLISH")
            if start_idx != -1 and end_idx != -1:
                new_msg = msg[:start_idx] + "COLOR PALETTE:\\n- Pick a dynamic, premium color palette that matches the product category, festival, or mood.\\n- Ensure high contrast and professional aesthetics.\\n\\n" + msg[end_idx:]
                node["parameters"]["systemMessage"] = new_msg
                
        # For Content Planner
        msg = node["parameters"]["systemMessage"]
        if "(Light/airy palette preferred: ivory white, royal blue, warm gold" in msg:
            new_msg = msg.replace("(Light/airy palette preferred: ivory white, royal blue, warm gold \\u2014 Indian premium brand aesthetic)", "(Pick a dynamic, premium color palette that matches the product category, festival, or mood)")
            node["parameters"]["systemMessage"] = new_msg

    if "jsCode" in node.get("parameters", {}):
        code = node["parameters"]["jsCode"]
        if "Preferred Colors:" in code:
            start_idx = code.find("Preferred Colors:")
            end_idx = code.find("Add subtle Indian premium")
            if start_idx != -1 and end_idx != -1:
                new_code = code[:start_idx] + "Preferred Colors:\\n- Pick a dynamic, premium color palette that matches the product category, festival, or mood.\\n- Ensure high contrast and professional aesthetics.\\n\\n" + code[end_idx:]
                node["parameters"]["jsCode"] = new_code

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("Colors cleaned up!")
