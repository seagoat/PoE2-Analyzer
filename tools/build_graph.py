import json

def build_graph():
    print("Loading relations data...")
    with open('../web/poe2_relations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nodes = data['nodes']
    
    print("Building requirements map...")
    requirements_map = {} 
    for node in nodes:
        for inp in node.get('inputs', []):
            val = inp['value'].lower()
            if val not in requirements_map:
                requirements_map[val] = []
            requirements_map[val].append(node['id'])
            
    print("Building links...")
    links = []
    
    for source in nodes:
        source_id = source['id']
        for out in source.get('outputs', []):
            target = out.get('target', '')
            if not target:
                continue
            target = str(target).lower()
            
            for req_tag, target_node_ids in requirements_map.items():
                if req_tag in target:
                    for target_id in target_node_ids:
                        if source_id != target_id:
                            links.append({
                                "source": source_id,
                                "target": target_id,
                                "label": f"{out['type']} {out.get('value','')}"
                            })
                            
    print("Deduplicating links...")
    unique_links = {}
    for link in links:
        key = f"{link['source']}->{link['target']}"
        if key not in unique_links:
            unique_links[key] = link
            
    final_links = list(unique_links.values())
    
    graph_nodes = []
    for n in nodes:
        graph_nodes.append({
            "id": n["id"],
            "name": n["name"],
            "group": n["category"],
            "val": 1 # size
        })
        
    graph_data = {
        "nodes": graph_nodes,
        "links": final_links
    }
    
    out_path = '../web/poe2_graph.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False)
    
    print(f"Graph generated with {len(graph_nodes)} nodes and {len(final_links)} edges.")

if __name__ == "__main__":
    build_graph()