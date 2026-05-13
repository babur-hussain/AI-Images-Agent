import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

# 1. Fix Welcome Menu to use dynamic business_name and tagline
for node in data["nodes"]:
    if node.get("name") == "Send: Welcome Menu":
        # Make the welcome message dynamic using Merge Context data
        node["parameters"]["jsonBody"] = (
            '={\n'
            '  "messaging_product": "whatsapp",\n'
            '  "to": "{{ $(\'Merge Context\').first().json.from }}",\n'
            '  "type": "interactive",\n'
            '  "interactive": {\n'
            '    "type": "button",\n'
            '    "body": {\n'
            '      "text": "\U0001f44b Welcome to *{{ $(\'Merge Context\').first().json.business_name }}*!\\n\\n'
            '{{ $(\'Merge Context\').first().json.tagline || $(\'Merge Context\').first().json.brand_positioning || \'Your trusted partner\' }}\\n\\n'
            'What would you like to do today?"\n'
            '    },\n'
            '    "action": {\n'
            '      "buttons": [\n'
            '        { "type": "reply", "reply": { "id": "create_offer", "title": "\U0001f4e2 Create Offer" } },\n'
            '        { "type": "reply", "reply": { "id": "content_planner", "title": "\U0001f4c5 Content Planner" } },\n'
            '        { "type": "reply", "reply": { "id": "skip_today", "title": "\u23ed Skip Today" } }\n'
            '      ]\n'
            '    }\n'
            '  }\n'
            '}'
        )
        # Add retry on fail
        node["retryOnFail"] = True
        node["maxTries"] = 3
        node["waitBetweenTries"] = 1000
        print(f"  Fixed: {node['name']} (dynamic message + retry)")

# 2. Add retry on fail to critical nodes
retry_nodes = [
    "PG: Get Active Session",
    "PG: Auto Create Session",
    "PG: Open Session",
    "PG: Start Collecting",
    "PG: Append Offer",
    "PG: Append Text Detail",
    "PG: Get All Offers",
    "PG: Save Preview URL",
    "PG: Close Session",
    "PG: Reject & Close Session",
    "PG: Save Content Idea",
    "PG: Start With Idea",
    "Daily: Save Idea",
    "Send: Start Offer Prompt",
    "Send: Offer Saved + Generate Button",
    "Send: Text Saved + Generate Button",
    "Send: Preview Image",
    "Send: Approval Buttons",
    "Send: Posted Confirmation",
    "Send: Reject Confirmation",
    "Send: Regenerate Prompt",
    "Send: Content Plan",
    "Send Morning Message",
    "Publish: Facebook",
    "Publish: Instagram",
    "IG: Publish Container",
    "Create KIE Task",
    "Get KIE Result",
    "WA: Download Image",
    "Download WA Media",
    "Upload to ImgBB",
    "Daily: Call AI",
    "Calendarific: Get Today Holidays",
    "Merge Context"
]

for node in data["nodes"]:
    if node.get("name") in retry_nodes:
        node["retryOnFail"] = True
        node["maxTries"] = 3
        node["waitBetweenTries"] = 1000
        print(f"  Added retry: {node['name']}")

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print(f"\nDone! Fixed welcome message + added retry on fail to {len(retry_nodes)} nodes.")
