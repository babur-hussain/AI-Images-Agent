import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

for node in data["nodes"]:
    # 1. Fix WA: Parse Message to also extract the business phone number (wa_phone_id from metadata)
    if node.get("name") == "WA: Parse Message":
        node["parameters"]["jsCode"] = (
            "const body = $input.first().json.body;\n\n"
            "// Handle webhook verification\n"
            "if ($input.first().json.query?.['hub.mode'] === 'subscribe') {\n"
            "  return [{ json: { isVerification: true, challenge: $input.first().json.query['hub.challenge'] } }];\n"
            "}\n\n"
            "const entry = body?.entry?.[0];\n"
            "const change = entry?.changes?.[0]?.value;\n"
            "const msg = change?.messages?.[0];\n"
            "if (!msg) return [{ json: { msgType: 'status_update' } }];\n\n"
            "// Extract the business phone number ID that RECEIVED this message\n"
            "const businessPhoneId = change?.metadata?.phone_number_id || '';\n"
            "const businessPhone = change?.metadata?.display_phone_number?.replace(/[^0-9]/g, '') || '';\n\n"
            "const msgType = msg.type;\n"
            "const from = msg.from;\n"
            "let buttonId = null;\n"
            "let text = null;\n"
            "let imageId = null;\n"
            "let caption = null;\n\n"
            "if (msgType === 'interactive') {\n"
            "  buttonId = msg.interactive?.button_reply?.id;\n"
            "}\n"
            "if (msgType === 'text') {\n"
            "  text = msg.text?.body;\n"
            "}\n"
            "if (msgType === 'image') {\n"
            "  imageId = msg.image?.id;\n"
            "  caption = msg.image?.caption || '';\n"
            "}\n\n"
            "return [{ json: { msgType, from, buttonId, text, imageId, caption, businessPhoneId, businessPhone, msg } }];"
        )
        print(f"  Fixed: {node['name']}")

    # 2. Fix PG: Get Active Session to lookup client by wa_phone_id instead of phone_primary
    if node.get("name") == "PG: Get Active Session":
        old_query = node["parameters"]["query"]
        # Replace the JOIN condition to match on wa_phone_id (the business number)
        new_query = old_query.replace(
            "JOIN ks_clients c ON c.phone_primary = '{{ $json.from }}'",
            "JOIN ks_clients c ON c.wa_phone_id = '{{ $json.businessPhoneId }}'"
        )
        node["parameters"]["query"] = new_query
        print(f"  Fixed: {node['name']}")

    # 3. Fix Merge Context to also pass businessPhoneId and businessPhone
    if node.get("name") == "Merge Context":
        code = node["parameters"]["jsCode"]
        # Add businessPhoneId to the parsed fields
        code = code.replace(
            "const caption = parsed.caption;",
            "const caption = parsed.caption;\nconst businessPhoneId = parsed.businessPhoneId;\nconst businessPhone = parsed.businessPhone;"
        )
        # Add businessPhoneId to the return object
        code = code.replace(
            "  from, msgType, buttonId, text, imageId, caption,",
            "  from, msgType, buttonId, text, imageId, caption, businessPhoneId, businessPhone,"
        )
        node["parameters"]["jsCode"] = code
        print(f"  Fixed: {node['name']}")

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("\nDone! Client lookup now uses wa_phone_id from the webhook metadata.")
