import json

main_file = "Kapoor and Sons - WhatsApp Offer Automation copy (5).json"
api_file = "Client Management API.json"

with open(main_file, "r") as f:
    main_data = json.load(f)

with open(api_file, "r") as f:
    api_data = json.load(f)

# Append nodes
for node in api_data.get("nodes", []):
    main_data["nodes"].append(node)

# Append connections
api_conns = api_data.get("connections", {})
for source_node, targets in api_conns.items():
    if source_node not in main_data["connections"]:
        main_data["connections"][source_node] = targets
    else:
        # Merge if source already exists (unlikely since these are new nodes)
        for target_type, target_conns in targets.items():
            if target_type not in main_data["connections"][source_node]:
                main_data["connections"][source_node][target_type] = target_conns
            else:
                main_data["connections"][source_node][target_type].extend(target_conns)

with open(main_file, "w") as f:
    json.dump(main_data, f, indent=2)

print("Merged successfully!")
