import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

for node in data["nodes"]:
    if node.get("name") == "PG: Get Active Session":
        # Change: client is PRIMARY, session is optional (LEFT JOIN)
        node["parameters"]["query"] = (
            "SELECT s.session_id, s.status, s.preview_image_url, "
            "c.client_id as cid, c.business_name, c.tagline, c.established_year, c.location, "
            "c.brand_category, c.brand_positioning, c.phone_primary, c.phone_display, "
            "c.wa_phone_id, c.wa_token, c.fb_page_id, c.fb_access_token, "
            "c.ig_node_id, c.ig_credential_id, c.kie_api_key, c.imgbb_api_key, "
            "c.serp_api_key, c.calendarific_api_key, "
            "c.prompt_poster, c.prompt_enhance, c.prompt_planner, c.prompt_morning, c.prompt_welcome "
            "FROM ks_clients c "
            "LEFT JOIN ks_sessions s ON s.phone = '{{ $json.from }}' AND s.status NOT IN ('closed', 'skip') "
            "WHERE c.wa_phone_id = '{{ $json.businessPhoneId }}' "
            "ORDER BY s.created_at DESC LIMIT 1;"
        )
        print(f"  Fixed: {node['name']} (LEFT JOIN: client always found)")
        break

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("\nDone! Client data will always be fetched, even on first message.")
