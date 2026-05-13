import json

file_path = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
with open(file_path, "r") as f:
    data = json.load(f)

ctx = "$('Merge Context').first().json"

# ===== 1. REVERT Merge Context — remove all prompt building logic =====
for node in data["nodes"]:
    if node.get("name") == "Merge Context":
        # Rebuild clean Merge Context — just data passing, NO prompt logic
        node["parameters"]["jsCode"] = (
            "const session = $('PG: Get Active Session').first().json;\n"
            "const parsed = $('WA: Parse Message').first().json;\n\n"
            "const sessionId = session?.session_id || null;\n"
            "const sessionStatus = session?.status || null;\n"
            "const previewImageUrl = session?.preview_image_url || null;\n"
            "const from = parsed.from;\n"
            "const msgType = parsed.msgType;\n"
            "const buttonId = parsed.buttonId;\n"
            "const text = parsed.text;\n"
            "const imageId = parsed.imageId;\n"
            "const caption = parsed.caption;\n"
            "const businessPhoneId = parsed.businessPhoneId;\n"
            "const businessPhone = parsed.businessPhone;\n\n"
            "const createdAt = session?.created_at ? new Date(session.created_at) : null;\n"
            "const isStale = createdAt ? (Date.now() - createdAt.getTime()) > 2 * 60 * 60 * 1000 : false;\n"
            "const isNewSession = !sessionId || isStale;\n"
            "const autoSessionId = isNewSession ? ('KS_AUTO_' + Date.now()) : sessionId;\n\n"
            "// Client config from ks_clients JOIN\n"
            "return [{ json: {\n"
            "  sessionId: autoSessionId,\n"
            "  sessionStatus: isNewSession ? null : sessionStatus,\n"
            "  previewImageUrl: isNewSession ? null : previewImageUrl,\n"
            "  from, msgType, buttonId, text, imageId, caption, businessPhoneId, businessPhone,\n"
            "  hasActiveSession: !isNewSession, isNewSession,\n"
            "  // Per-client config\n"
            "  client_id: session?.cid || null,\n"
            "  business_name: session?.business_name || 'Business',\n"
            "  tagline: session?.tagline || '',\n"
            "  established_year: session?.established_year || '',\n"
            "  location: session?.location || '',\n"
            "  brand_category: session?.brand_category || 'general',\n"
            "  brand_positioning: session?.brand_positioning || '',\n"
            "  phone_display: session?.phone_display || from,\n"
            "  wa_phone_id: session?.wa_phone_id || '',\n"
            "  wa_token: session?.wa_token || '',\n"
            "  fb_page_id: session?.fb_page_id || '',\n"
            "  fb_access_token: session?.fb_access_token || '',\n"
            "  ig_node_id: session?.ig_node_id || '',\n"
            "  ig_credential_id: session?.ig_credential_id || '',\n"
            "  kie_api_key: session?.kie_api_key || '',\n"
            "  imgbb_api_key: session?.imgbb_api_key || '',\n"
            "  prompt_poster: session?.prompt_poster || '',\n"
            "  prompt_enhance: session?.prompt_enhance || '',\n"
            "  prompt_planner: session?.prompt_planner || '',\n"
            "  prompt_morning: session?.prompt_morning || '',\n"
            "  prompt_welcome: session?.prompt_welcome || ''\n"
            "} }];"
        )
        print(f"  Reverted: Merge Context — clean data passing only")

# ===== 2. FIX Build Welcome Body — output raw JSON string properly =====
for node in data["nodes"]:
    if node.get("name") == "Build Welcome Body":
        node["parameters"]["jsCode"] = (
            "const ctx = $('Merge Context').first().json;\n\n"
            "// Build welcome text from DB prompt or default\n"
            "let welcomeText = '';\n"
            "const pw = ctx.prompt_welcome || '';\n"
            "if (pw.trim().length > 5) {\n"
            "  welcomeText = pw\n"
            "    .replace(/\\{\\{business_name\\}\\}/g, ctx.business_name)\n"
            "    .replace(/\\{\\{tagline\\}\\}/g, ctx.tagline || '')\n"
            "    .replace(/\\{\\{location\\}\\}/g, ctx.location || '');\n"
            "} else {\n"
            "  welcomeText = '\\ud83d\\udc4b Welcome to *' + ctx.business_name + '*!\\n\\n' +\n"
            "    (ctx.tagline || ctx.brand_positioning || 'Your trusted partner') +\n"
            "    '\\n\\nWhat would you like to do today?';\n"
            "}\n\n"
            "return [{ json: {\n"
            "  wa_phone_id: ctx.wa_phone_id,\n"
            "  wa_token: ctx.wa_token,\n"
            "  from: ctx.from,\n"
            "  welcomeText\n"
            "} }];"
        )
        print(f"  Fixed: Build Welcome Body — outputs clean fields")

# ===== 3. FIX Send: Welcome Menu — use simple template like all other nodes =====
for node in data["nodes"]:
    if node.get("name") == "Send: Welcome Menu":
        node["parameters"] = {
            "method": "POST",
            "url": "=https://graph.facebook.com/v25.0/{{ $json.wa_phone_id }}/messages",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Authorization", "value": "=Bearer {{ $json.wa_token }}"},
                    {"name": "Content-Type", "value": "application/json"}
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({messaging_product:'whatsapp',to:$json.from,type:'interactive',interactive:{type:'button',body:{text:$json.welcomeText},action:{buttons:[{type:'reply',reply:{id:'create_offer',title:'Create Offer'}},{type:'reply',reply:{id:'content_planner',title:'Content Planner'}},{type:'reply',reply:{id:'skip_today',title:'Skip Today'}}]}}}) }}",
            "options": {}
        }
        # Keep retry settings
        node["retryOnFail"] = True
        node["maxTries"] = 3
        node["waitBetweenTries"] = 1000
        print(f"  Fixed: Send: Welcome Menu — uses $json from Build Welcome Body")

# ===== 4. ADD "Build Planner Prompt" Code node for AI Content Agent =====
# Find AI Content Agent position
ai_agent_pos = [37984, 46240]
for node in data["nodes"]:
    if node.get("name") == "AI Content Agent":
        ai_agent_pos = node["position"]
        # Set simple system message reference
        node["parameters"]["options"]["systemMessage"] = "={{ $json.plannerSystemMsg }}"
        print(f"  Fixed: AI Content Agent — references $json.plannerSystemMsg")

build_planner = {
    "parameters": {
        "jsCode": (
            "const ctx = $('Merge Context').first().json;\n"
            "const input = $input.first().json;\n\n"
            "// Build planner system message from DB or default\n"
            "let plannerSystemMsg = ctx.prompt_planner || '';\n"
            "if (!plannerSystemMsg || plannerSystemMsg.trim().length < 50) {\n"
            "  const bname = ctx.business_name;\n"
            "  const bloc = ctx.location || 'India';\n"
            "  const bcat = ctx.brand_category || 'retail';\n"
            "  const bpos = ctx.brand_positioning || ctx.tagline || 'trusted local business';\n"
            "  plannerSystemMsg = 'You are an ELITE social media strategist for ' + bname + ' - ' + bpos + ' in ' + bloc + '.\\n\\n'\n"
            "    + '=== ABSOLUTE RULE ===\\nNEVER suggest any specific price, discount percentage, or deal number. '\n"
            "    + 'Pricing is decided by the shop owner only.\\n\\n'\n"
            "    + 'Provide ONE content idea for TODAY with:\\n'\n"
            "    + '1. POST THEME\\n2. CAPTION (Hindi+English mix, emojis)\\n'\n"
            "    + '3. CONTENT HOOK\\n4. BEST TIME\\n5. HASHTAGS (8-10)\\n6. DESIGN DIRECTION\\n\\n'\n"
            "    + 'Keep it actionable for a trusted local ' + bcat + ' business in ' + bloc + '.';\n"
            "}\n\n"
            "return [{ json: { ...input, plannerSystemMsg } }];"
        )
    },
    "id": "build-planner-prompt-001",
    "name": "Build Planner Prompt",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [ai_agent_pos[0] - 224, ai_agent_pos[1]]
}
data["nodes"].append(build_planner)
print(f"  Added: Build Planner Prompt node")

# Update connection: Prepare Content Planner → Build Planner Prompt → AI Content Agent
# Find what currently connects to AI Content Agent
for src_name, conns in data["connections"].items():
    if src_name == "Prepare Content Planner":
        for i, output in enumerate(conns.get("main", [])):
            for j, conn in enumerate(output):
                if conn.get("node") == "AI Content Agent":
                    conns["main"][i][j] = {"node": "Build Planner Prompt", "type": "main", "index": 0}
                    print(f"  Rerouted: Prepare Content Planner → Build Planner Prompt")
    if src_name == "Calendarific: Get Today Holidays":
        for i, output in enumerate(conns.get("main", [])):
            for j, conn in enumerate(output):
                if conn.get("node") == "AI Content Agent":
                    conns["main"][i][j] = {"node": "Build Planner Prompt", "type": "main", "index": 0}
                    print(f"  Rerouted: Calendarific → Build Planner Prompt")

data["connections"]["Build Planner Prompt"] = {
    "main": [[{"node": "AI Content Agent", "type": "main", "index": 0}]]
}
print(f"  Connected: Build Planner Prompt → AI Content Agent")

# ===== 5. FIX AI: Enhance Image Prompt — build system msg in Consolidate All Offers =====
for node in data["nodes"]:
    if node.get("name") == "AI: Enhance Image Prompt":
        # Simple reference — the system message will be passed through the data flow
        node["parameters"]["options"]["systemMessage"] = "={{ $('Consolidate All Offers').first().json.enhanceSystemMsg }}"
        print(f"  Fixed: AI: Enhance Image Prompt — references enhanceSystemMsg from Consolidate")

    if node.get("name") == "Consolidate All Offers":
        code = node["parameters"]["jsCode"]
        # Add enhanceSystemMsg building at the end, before return
        enhance_code = (
            "\n// Build enhance system message from DB or default\n"
            "let enhanceSystemMsg = ctx.prompt_enhance || '';\n"
            "if (!enhanceSystemMsg || enhanceSystemMsg.trim().length < 50) {\n"
            "  enhanceSystemMsg = 'You are an expert image generation prompt engineer for Indian retail marketing visuals.\\n\\n'\n"
            "    + '=== ABSOLUTE RULES ===\\n'\n"
            "    + '1. User offer details MUST appear verbatim as PRIMARY focus.\\n'\n"
            "    + '2. NEVER invent any price, discount, or deal.\\n'\n"
            "    + '3. NEVER alter product or brand names.\\n'\n"
            "    + '4. Output ONLY the enhanced prompt.\\n\\n'\n"
            "    + 'BRAND: ' + ctx.business_name + '\\n'\n"
            "    + 'LOCATION: ' + (ctx.location || '') + '\\n'\n"
            "    + 'CONTACT: ' + (ctx.phone_display || '') + '\\n'\n"
            "    + (ctx.established_year ? 'ESTABLISHED: ' + ctx.established_year + '\\n' : '') + '\\n'\n"
            "    + 'COMPOSITION: Product as hero, offer text bold, brand header, contact at bottom, 1:1 square format.\\n'\n"
            "    + 'PALETTE: Ivory white bg, royal blue headers, warm gold highlights, premium Indian retail aesthetic.';\n"
            "}\n"
        )
        # Insert before the return
        code = code.replace(
            "return [{ json: {",
            enhance_code + "\nreturn [{ json: {"
        )
        # Add enhanceSystemMsg to return
        if "enhanceSystemMsg" not in code:
            code = code.replace(
                "} }];",
                ",\n  enhanceSystemMsg\n} }];"
            )
        node["parameters"]["jsCode"] = code
        print(f"  Fixed: Consolidate All Offers — builds enhanceSystemMsg")

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("\nDone! All prompt logic in separate dedicated nodes.")
