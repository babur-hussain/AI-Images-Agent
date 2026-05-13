import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

# Find and replace the Instagram node
for i, node in enumerate(data["nodes"]):
    if node.get("name") == "Publish: Instagram":
        # Instagram Graph API requires 2 steps:
        # Step 1: Create media container (POST to /{ig-user-id}/media)
        # Step 2: Publish it (POST to /{ig-user-id}/media_publish)
        # We'll use a Code node to do both via fetch in one step
        
        old_position = node["position"]
        old_id = node["id"]
        
        # Replace with an HTTP Request node for Step 1 (create container)
        data["nodes"][i] = {
            "parameters": {
                "method": "POST",
                "url": "=https://graph.facebook.com/v25.0/{{ $('Merge Context').first().json.ig_node_id }}/media",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {
                            "name": "image_url",
                            "value": "={{ $('Merge Context').first().json.previewImageUrl }}"
                        },
                        {
                            "name": "caption",
                            "value": "=🏪 {{ $('Merge Context').first().json.business_name }} - {{ $('Merge Context').first().json.location }}\n📞 {{ $('Merge Context').first().json.phone_display }}"
                        },
                        {
                            "name": "access_token",
                            "value": "={{ $('Merge Context').first().json.fb_access_token }}"
                        }
                    ]
                },
                "options": {}
            },
            "id": old_id,
            "name": "Publish: Instagram",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": old_position
        }
        print("  Replaced Instagram community node with HTTP Request (create container)")
        break

# Now add a second node for Step 2 (publish the container)
publish_node = {
    "parameters": {
        "method": "POST",
        "url": "=https://graph.facebook.com/v25.0/{{ $('Merge Context').first().json.ig_node_id }}/media_publish",
        "sendQuery": True,
        "queryParameters": {
            "parameters": [
                {
                    "name": "creation_id",
                    "value": "={{ $json.id }}"
                },
                {
                    "name": "access_token",
                    "value": "={{ $('Merge Context').first().json.fb_access_token }}"
                }
            ]
        },
        "options": {}
    },
    "id": "ig-publish-step2-001",
    "name": "IG: Publish Container",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4,
    "position": [
        data["nodes"][i]["position"][0] + 300,
        data["nodes"][i]["position"][1]
    ]
}
data["nodes"].append(publish_node)
print("  Added IG: Publish Container node (step 2)")

# Update connections: Publish: Instagram now connects to IG: Publish Container
# instead of directly to PG: Close Session
# First, find what Instagram currently connects to
ig_connections = data["connections"].get("Publish: Instagram", {})
old_targets = ig_connections.get("main", [[]])[0] if ig_connections else []

# Instagram -> IG: Publish Container
data["connections"]["Publish: Instagram"] = {
    "main": [[{"node": "IG: Publish Container", "type": "main", "index": 0}]]
}

# IG: Publish Container -> whatever Instagram used to connect to (PG: Close Session)
data["connections"]["IG: Publish Container"] = {
    "main": [old_targets]
}

print(f"  Updated connections: Instagram -> IG: Publish Container -> {[t.get('node') for t in old_targets]}")

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("\nDone! Instagram now uses standard HTTP Request nodes (2-step Graph API).")
