import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

ctx = "$('Merge Context').first().json"

for node in data["nodes"]:
    name = node.get("name", "")

    # 1. CONSOLIDATE ALL OFFERS — uses prompt_poster
    # The jsCode builds the master prompt. We need it to use prompt_poster from DB
    # if available, otherwise fall back to the default hardcoded prompt.
    if name == "Consolidate All Offers":
        code = node["parameters"]["jsCode"]
        # Add prompt_poster override at the END of the jsCode, before the return
        # Find the return statement and prepend the override
        if "ctx.prompt_poster" not in code:
            # Replace the return to inject the override
            code = code.replace(
                "return [{ json: {",
                "// Use custom prompt from portal if configured\n"
                "const ctx = $('Merge Context').first().json;\n"
                "if (ctx.prompt_poster && ctx.prompt_poster.trim().length > 50) {\n"
                "  // Replace brand placeholders in custom prompt\n"
                "  prompt = ctx.prompt_poster\n"
                "    .replace(/\\{\\{business_name\\}\\}/g, ctx.business_name || 'Business')\n"
                "    .replace(/\\{\\{location\\}\\}/g, ctx.location || '')\n"
                "    .replace(/\\{\\{phone_display\\}\\}/g, ctx.phone_display || '')\n"
                "    .replace(/\\{\\{tagline\\}\\}/g, ctx.tagline || '')\n"
                "    .replace(/\\{\\{brand_category\\}\\}/g, ctx.brand_category || 'retail')\n"
                "    .replace(/\\{\\{established_year\\}\\}/g, ctx.established_year || '')\n"
                "    .replace(/\\{\\{brand_positioning\\}\\}/g, ctx.brand_positioning || '')\n"
                "    + '\\n\\nOFFER DETAILS:\\n' + offerDetails;\n"
                "}\n\n"
                "return [{ json: {"
            )
            node["parameters"]["jsCode"] = code
            print(f"  Fixed: {name} — now uses prompt_poster from DB")

    # 2. AI: ENHANCE IMAGE PROMPT — uses prompt_enhance
    if name == "AI: Enhance Image Prompt":
        params = node["parameters"]
        # The systemMessage is in options.systemMessage
        # Replace with dynamic: use DB prompt if available, else default
        default_system = params.get("options", {}).get("systemMessage", "")
        
        # Make the system message dynamic
        params["options"]["systemMessage"] = (
            "={{ $('Merge Context').first().json.prompt_enhance && "
            "$('Merge Context').first().json.prompt_enhance.trim().length > 50 "
            "? $('Merge Context').first().json.prompt_enhance "
            ": '" + default_system.replace("'", "\\'").replace("\n", "\\n") + "' }}"
        )
        print(f"  Fixed: {name} — now uses prompt_enhance from DB")

    # 3. AI CONTENT AGENT — uses prompt_planner
    if name == "AI Content Agent":
        params = node["parameters"]
        default_system = params.get("options", {}).get("systemMessage", "")
        
        params["options"]["systemMessage"] = (
            "={{ $('Merge Context').first().json.prompt_planner && "
            "$('Merge Context').first().json.prompt_planner.trim().length > 50 "
            "? $('Merge Context').first().json.prompt_planner "
            ": '" + default_system.replace("'", "\\'").replace("\n", "\\n") + "' }}"
        )
        print(f"  Fixed: {name} — now uses prompt_planner from DB")

    # 4. SEND: WELCOME MENU — uses prompt_welcome for the body text
    if name == "Send: Welcome Menu":
        params = node["parameters"]
        # Build a dynamic welcome message that uses prompt_welcome if set
        params["jsonBody"] = (
            '={\n'
            '  "messaging_product": "whatsapp",\n'
            '  "to": "{{ $(\'Merge Context\').first().json.from }}",\n'
            '  "type": "interactive",\n'
            '  "interactive": {\n'
            '    "type": "button",\n'
            '    "body": {\n'
            '      "text": "{{ $(\'Merge Context\').first().json.prompt_welcome && '
            '$(\'Merge Context\').first().json.prompt_welcome.trim().length > 5 '
            '? $(\'Merge Context\').first().json.prompt_welcome'
            '.replace(\'{{business_name}}\', $(\'Merge Context\').first().json.business_name)'
            '.replace(\'{{tagline}}\', $(\'Merge Context\').first().json.tagline || \'\')'
            '.replace(\'{{location}}\', $(\'Merge Context\').first().json.location || \'\')'
            ' : \'\U0001f44b Welcome to *\' + $(\'Merge Context\').first().json.business_name + \'*!\\n\\n\' + '
            '($(\'Merge Context\').first().json.tagline || $(\'Merge Context\').first().json.brand_positioning || \'Your trusted partner\') + '
            '\'\\n\\nWhat would you like to do today?\' }}"\n'
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
        print(f"  Fixed: {name} — now uses prompt_welcome from DB")

    # 5. SEND MORNING MESSAGE — uses prompt_morning
    if name == "Send Morning Message":
        params = node["parameters"]
        body = params.get("jsonBody", "")
        # The morning message is sent from Daily Trigger context
        # We need to inject prompt_morning support
        # For now, this runs from the Daily trigger, not per-webhook
        # It already uses $json.phone, $json.business_name
        print(f"  Note: {name} — runs from Daily Trigger (prompt_morning needs Daily flow to query client)")

    # 6. DAILY: CALL AI — uses prompt_planner for the content planning prompt
    if name == "Daily: Call AI":
        params = node["parameters"]
        body = params.get("jsonBody", "")
        # This node also runs from Daily Trigger, not webhook
        # It should ideally use client prompts too
        print(f"  Note: {name} — runs from Daily Trigger (prompt_planner used in AI Content Agent instead)")

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("\nDone! AI nodes now use prompts from database (portal System Prompts).")
print("\nMapping:")
print("  prompt_poster  → Consolidate All Offers (master prompt)")
print("  prompt_enhance → AI: Enhance Image Prompt (system message)")
print("  prompt_planner → AI Content Agent (system message)")
print("  prompt_welcome → Send: Welcome Menu (body text)")
print("  prompt_morning → Send Morning Message (Daily trigger - needs separate client query)")
