import json
import re
import os

def export_data():
    data = {
        "gems": [],
        "passives": []
    }

    print("Parsing Gems.lua...")
    # 1. Parse Gems.lua
    try:
        with open("../../PathOfBuilding-PoE2/src/Data/Gems.lua", "r", encoding="utf-8") as f:
            gem_content = f.read()
            
        # Using regex to find gem blocks.
        # This regex looks for blocks starting with ["Metadata..."] = { ... }
        # and extracts name and tagString
        gem_blocks = re.findall(r'\["Metadata/Items/Gems/[^"]+"\]\s*=\s*\{(.*?)\n\t\}', gem_content, re.DOTALL)
        
        for block in gem_blocks:
            name_match = re.search(r'name\s*=\s*"([^"]+)"', block)
            tags_match = re.search(r'tagString\s*=\s*"([^"]+)"', block)
            
            if name_match:
                name = name_match.group(1)
                tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else []
                data["gems"].append({
                    "name": name,
                    "tags": tags
                })
        print(f"Extracted {len(data['gems'])} gems.")
    except Exception as e:
        print(f"Error parsing Gems.lua: {e}")

    print("Parsing tree.json...")
    # 2. Parse tree.json
    try:
        with open("../../PathOfBuilding-PoE2/src/TreeData/0_4/tree.json", "r", encoding="utf-8") as f:
            tree_data = json.load(f)
            
        nodes = tree_data.get("nodes", {})
        for node_id, node_info in nodes.items():
            # Skip empty nodes, mastery or generic structural nodes if they have no stats
            stats = node_info.get("stats", [])
            name = node_info.get("name", "Unknown Node")
            
            if not stats:
                continue
                
            data["passives"].append({
                "id": node_id,
                "name": name,
                "stats": stats
            })
        print(f"Extracted {len(data['passives'])} passive nodes with stats.")
    except Exception as e:
        print(f"Error parsing tree.json: {e}")

    # 3. Export to JSON
    out_path = "../web/poe2_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data successfully exported to {out_path}")

if __name__ == "__main__":
    export_data()
