import json
import re
import os

def parse_stat(stat_str):
    stat = stat_str.lower()
    inputs = []
    outputs = []
    
    # Check conditions
    if "if you have" in stat or "while" in stat or "when" in stat or "on " in stat:
        condition_match = re.search(r'(if you have |while |when |on |if )([a-zA-Z\s]+)', stat)
        if condition_match:
            inputs.append({"type": "Condition", "value": condition_match.group(2).strip()})
    
    if "to spells" in stat:
        inputs.append({"type": "TagRequirement", "value": "spell"})
    if "to attacks" in stat:
        inputs.append({"type": "TagRequirement", "value": "attack"})
    if "to melee attacks" in stat:
        inputs.append({"type": "TagRequirement", "value": "melee"})
    
    # Check outputs
    # 1. Multipliers (Increased/Reduced - Additive with each other)
    inc_match = re.search(r'(\d+)% increased (.*)', stat)
    if inc_match:
        val = int(inc_match.group(1))
        outputs.append({"type": "Increased", "value": val, "target": inc_match.group(2).strip()})

    red_match = re.search(r'(\d+)% reduced (.*)', stat)
    if red_match:
        val = int(red_match.group(1))
        outputs.append({"type": "Reduced", "value": val, "target": red_match.group(2).strip()})

    # 2. Multipliers (More/Less - Multiplicative, Exponential growth)
    more_match = re.search(r'(\d+)% more (.*)', stat)
    if more_match:
        val = int(more_match.group(1))
        outputs.append({"type": "More (Multiplier)", "value": val, "target": more_match.group(2).strip()})

    less_match = re.search(r'(\d+)% less (.*)', stat)
    if less_match:
        val = int(less_match.group(1))
        outputs.append({"type": "Less (Multiplier)", "value": val, "target": less_match.group(2).strip()})

    # 3. Base Additions
    add_match = re.search(r'adds (\d+) to (\d+) (.*)', stat)
    if add_match:
        min_val = int(add_match.group(1))
        max_val = int(add_match.group(2))
        outputs.append({"type": "Added Base", "value": f"{min_val}-{max_val}", "target": add_match.group(3).strip()})

    # 4. Conversion
    conv_match = re.search(r'(\d+)% of (.*) converted to (.*)', stat)
    if conv_match:
        val = int(conv_match.group(1))
        outputs.append({"type": "Conversion", "value": val, "from": conv_match.group(2).strip(), "to": conv_match.group(3).strip()})

    # 5. Triggers
    trig_match = re.search(r'trigger level (\d+) (.*) on (.*)', stat)
    if trig_match:
        inputs.append({"type": "Trigger Event", "value": trig_match.group(3).strip()})
        outputs.append({"type": "Trigger Action", "value": trig_match.group(2).strip(), "level": int(trig_match.group(1))})

    # If nothing matched but it's a stat, just keep it as a generic output
    if not outputs:
        outputs.append({"type": "Generic", "value": stat_str})
        
    # Implicit target from generic stats (e.g., "15% increased Cold Damage" -> implicitly targets Cold)
    for out in outputs:
        if out["type"] in ["Increased", "Reduced", "More (Multiplier)", "Less (Multiplier)"]:
            target = out.get("target", "")
            if "cold" in target: inputs.append({"type": "TagRequirement", "value": "cold"})
            if "fire" in target: inputs.append({"type": "TagRequirement", "value": "fire"})
            if "lightning" in target: inputs.append({"type": "TagRequirement", "value": "lightning"})
            if "physical" in target: inputs.append({"type": "TagRequirement", "value": "physical"})
            if "chaos" in target: inputs.append({"type": "TagRequirement", "value": "chaos"})
            if "spell" in target: inputs.append({"type": "TagRequirement", "value": "spell"})
            if "attack" in target: inputs.append({"type": "TagRequirement", "value": "attack"})
            if "area" in target: inputs.append({"type": "TagRequirement", "value": "area"})
            if "projectile" in target: inputs.append({"type": "TagRequirement", "value": "projectile"})

    # Deduplicate inputs
    unique_inputs = []
    seen_in = set()
    for item in inputs:
        sig = f"{item['type']}:{item['value']}"
        if sig not in seen_in:
            seen_in.add(sig)
            unique_inputs.append(item)

    return unique_inputs, outputs

def export_data():
    data = {
        "classes": [],
        "nodes": []
    }

    print("Parsing tree.json for classes and passives...")
    ascendancy_to_class = {}
    try:
        with open("../../PathOfBuilding-PoE2/src/TreeData/0_4/tree.json", "r", encoding="utf-8") as f:
            tree_data = json.load(f)
            
        # Parse Classes
        classes_data = tree_data.get("classes", [])
        for c in classes_data:
            c_name = c.get("name")
            ascendancies = [a.get("name") for a in c.get("ascendancies", [])]
            data["classes"].append({
                "name": c_name,
                "ascendancies": ascendancies
            })
            for a in ascendancies:
                ascendancy_to_class[a] = c_name

        # Parse Passives
        nodes = tree_data.get("nodes", {})
        for node_id, node_info in nodes.items():
            stats = node_info.get("stats", [])
            name = node_info.get("name", "Unknown Node")
            ascendancy_name = node_info.get("ascendancyName", "")
            
            if not stats:
                continue
            
            all_inputs = []
            all_outputs = []
            for stat in stats:
                ins, outs = parse_stat(stat)
                all_inputs.extend(ins)
                all_outputs.extend(outs)
                
            unique_inputs = []
            seen_in = set()
            for item in all_inputs:
                sig = f"{item['type']}:{item['value']}"
                if sig not in seen_in:
                    seen_in.add(sig)
                    unique_inputs.append(item)
                    
            node_class = ascendancy_to_class.get(ascendancy_name, "All") if ascendancy_name else "All"

            data["nodes"].append({
                "id": f"passive_{node_id}",
                "name": name,
                "category": "Passive",
                "class_restriction": node_class,
                "ascendancy": ascendancy_name,
                "raw_stats": stats,
                "inputs": unique_inputs,
                "outputs": all_outputs
            })
    except Exception as e:
        print(f"Error parsing tree.json: {e}")

    print("Parsing Gems.lua...")
    try:
        with open("../../PathOfBuilding-PoE2/src/Data/Gems.lua", "r", encoding="utf-8") as f:
            gem_content = f.read()
            
        gem_blocks = re.findall(r'\["Metadata/Items/Gems/[^"]+"\]\s*=\s*\{(.*?)\n\t\}', gem_content, re.DOTALL)
        
        for block in gem_blocks:
            name_match = re.search(r'name\s*=\s*"([^"]+)"', block)
            tags_match = re.search(r'tagString\s*=\s*"([^"]+)"', block)
            
            if name_match:
                name = name_match.group(1)
                tags = [t.strip().lower() for t in tags_match.group(1).split(',')] if tags_match else []
                
                inputs = [{"type": "TagRequirement", "value": tag} for tag in tags if tag]
                outputs = [{"type": "Skill Provided", "value": name}]
                
                data["nodes"].append({
                    "id": f"gem_{name}",
                    "name": name,
                    "category": "Gem",
                    "class_restriction": "All", # Gems are for all classes
                    "ascendancy": "",
                    "tags": tags,
                    "raw_stats": [],
                    "inputs": inputs,
                    "outputs": outputs
                })
    except Exception as e:
        print(f"Error parsing Gems.lua: {e}")

    print("Parsing Uniques...")
    try:
        uniques_dir = "../../PathOfBuilding-PoE2/src/Data/Uniques/"
        if os.path.exists(uniques_dir):
            for filename in os.listdir(uniques_dir):
                if not filename.endswith(".lua"):
                    continue
                file_path = os.path.join(uniques_dir, filename)
                
                # Determine item slot from filename
                item_slot = filename.replace('.lua', '').capitalize()
                # Map specific slots to more standard names if needed
                if item_slot == 'Body': item_slot = 'Body Armour'
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # The file is a list of multi-line strings enclosed in [[ ... ]]
                item_blocks = re.findall(r'\[\[(.*?)\]\]', content, re.DOTALL)
                for block in item_blocks:
                    lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
                    if not lines: continue
                    
                    name = lines[0]
                    base_type = lines[1] if len(lines) > 1 else "Unknown"
                    
                    # Everything after Implicits/Variant/Requires usually contains the stats
                    stats = []
                    for line in lines[2:]:
                        if line.startswith("Variant:") or line.startswith("Requires ") or line.startswith("League:") or line.startswith("Implicits:"):
                            continue
                        
                        # Remove tags like {tags:fire,cold} or {variant:1}
                        clean_stat = re.sub(r'\{[^}]+\}', '', line).strip()
                        if clean_stat:
                            stats.append(clean_stat)
                    
                    all_inputs = []
                    all_outputs = []
                    for stat in stats:
                        ins, outs = parse_stat(stat)
                        all_inputs.extend(ins)
                        all_outputs.extend(outs)
                    
                    unique_inputs = []
                    seen_in = set()
                    for item in all_inputs:
                        sig = f"{item['type']}:{item['value']}"
                        if sig not in seen_in:
                            seen_in.add(sig)
                            unique_inputs.append(item)
                            
                    data["nodes"].append({
                        "id": f"unique_{name.replace(' ', '_')}",
                        "name": name,
                        "category": "Unique",
                        "item_slot": item_slot,
                        "class_restriction": "All",
                        "ascendancy": "",
                        "raw_stats": stats,
                        "inputs": unique_inputs,
                        "outputs": all_outputs
                    })
    except Exception as e:
        print(f"Error parsing Uniques: {e}")

    # Sort nodes alphabetically for better candidate list
    data["nodes"].sort(key=lambda x: x["name"])

    out_path = "../web/poe2_relations.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Relational data exported to {out_path}")

if __name__ == "__main__":
    export_data()
