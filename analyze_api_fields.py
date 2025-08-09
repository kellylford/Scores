#!/usr/bin/env python3
"""
ESPN API Field Analyzer
Analyzes the generated JSON reference files to create detailed field documentation
"""

import json
from typing import Dict, Any, List, Set

def analyze_json_file(file_path: str) -> Dict[str, Any]:
    """Analyze a JSON reference file and extract all available fields"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def extract_all_fields(data: Any, path: str = "", max_depth: int = 6, current_depth: int = 0) -> Set[str]:
    """Recursively extract all field paths from API data"""
    fields = set()
    
    if current_depth >= max_depth:
        return fields
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            fields.add(current_path)
            
            if isinstance(value, (dict, list)):
                fields.update(extract_all_fields(value, current_path, max_depth, current_depth + 1))
    
    elif isinstance(data, list) and data:
        # Analyze first item in list
        fields.update(extract_all_fields(data[0], path, max_depth, current_depth + 1))
    
    return fields

def categorize_fields(fields: Set[str]) -> Dict[str, List[str]]:
    """Categorize fields by their likely purpose"""
    categories = {
        "identification": [],
        "team_info": [],
        "game_status": [],
        "statistics": [],
        "timing": [],
        "venue_weather": [],
        "media": [],
        "betting": [],
        "players": [],
        "plays": [],
        "other": []
    }
    
    for field in sorted(fields):
        field_lower = field.lower()
        
        if any(x in field_lower for x in ["id", "uid", "key"]):
            categories["identification"].append(field)
        elif any(x in field_lower for x in ["team", "competitor", "abbreviation", "displayname", "location"]):
            categories["team_info"].append(field)
        elif any(x in field_lower for x in ["status", "state", "period", "clock", "quarter", "inning"]):
            categories["game_status"].append(field)
        elif any(x in field_lower for x in ["stat", "score", "record", "standing", "leader"]):
            categories["statistics"].append(field)
        elif any(x in field_lower for x in ["date", "time", "published", "start", "end"]):
            categories["timing"].append(field)
        elif any(x in field_lower for x in ["venue", "weather", "temperature", "address", "city"]):
            categories["venue_weather"].append(field)
        elif any(x in field_lower for x in ["logo", "image", "broadcast", "link", "media"]):
            categories["media"].append(field)
        elif any(x in field_lower for x in ["odd", "spread", "line", "bet"]):
            categories["betting"].append(field)
        elif any(x in field_lower for x in ["athlete", "player", "position", "jersey", "height", "weight"]):
            categories["players"].append(field)
        elif any(x in field_lower for x in ["play", "drive", "down", "yard", "pitch"]):
            categories["plays"].append(field)
        else:
            categories["other"].append(field)
    
    return categories

def generate_field_reference(league: str, reference_file: str) -> str:
    """Generate detailed field reference for a league"""
    print(f"Analyzing {league} reference...")
    
    data = analyze_json_file(reference_file)
    
    # Extract sample data for better understanding
    sample_data = {}
    for endpoint_name, endpoint_data in data.get("endpoints", {}).items():
        if "sample_data" in endpoint_data:
            sample_data[endpoint_name] = endpoint_data["sample_data"]
    
    # Extract all fields from the structure
    all_fields = set()
    for endpoint_name, endpoint_data in data.get("endpoints", {}).items():
        if isinstance(endpoint_data, list):
            # Handle list of examples
            for example in endpoint_data:
                if "structure" in example:
                    endpoint_fields = extract_all_fields(example["structure"])
                    all_fields.update(endpoint_fields)
        elif "structure" in endpoint_data:
            endpoint_fields = extract_all_fields(endpoint_data["structure"])
            all_fields.update(endpoint_fields)
    
    categorized_fields = categorize_fields(all_fields)
    
    # Generate documentation
    doc = f"""# {league} API Field Reference

Generated from live API data on {data.get('exploration_time', 'unknown')}

## Available Endpoints

"""
    
    # Document each endpoint
    for endpoint_name, endpoint_data in data.get("endpoints", {}).items():
        if isinstance(endpoint_data, list):
            # Handle game_details_examples which is a list
            doc += f"""### {endpoint_name.replace('_', ' ').title()}

**Multiple Examples Available**: {len(endpoint_data)} examples

"""
            for i, example in enumerate(endpoint_data[:2]):  # Show first 2 examples
                doc += f"""#### Example {i+1}
**URL**: `{example.get('url', 'N/A')}`
**Description**: {example.get('description', 'No description')}

"""
        else:
            doc += f"""### {endpoint_name.replace('_', ' ').title()}

**URL**: `{endpoint_data.get('url', 'N/A')}`
**Description**: {endpoint_data.get('description', 'No description')}

**Key Fields**: {', '.join(endpoint_data.get('key_fields', []))}

"""
        
        if endpoint_name in sample_data and not isinstance(endpoint_data, list):
            sample = sample_data[endpoint_name]
            doc += "**Sample Data**:\n```json\n"
            doc += json.dumps(sample, indent=2)[:500] + "...\n```\n\n"
    
    # Document field categories
    doc += """## Field Categories

The following fields are available across various endpoints:

"""
    
    for category, fields in categorized_fields.items():
        if fields:
            doc += f"""### {category.replace('_', ' ').title()} Fields
```
{chr(10).join(fields[:20])}"""
            if len(fields) > 20:
                doc += f"\n... and {len(fields) - 20} more"
            doc += "\n```\n\n"
    
    return doc

def main():
    """Generate detailed field references for both leagues"""
    
    # Generate MLB reference
    mlb_doc = generate_field_reference("MLB", "ESPN_API_REFERENCE_MLB.json")
    with open("ESPN_API_FIELDS_MLB.md", "w", encoding="utf-8") as f:
        f.write(mlb_doc)
    
    # Generate NFL reference  
    nfl_doc = generate_field_reference("NFL", "ESPN_API_REFERENCE_NFL.json")
    with open("ESPN_API_FIELDS_NFL.md", "w", encoding="utf-8") as f:
        f.write(nfl_doc)
    
    print("Generated detailed field references:")
    print("- ESPN_API_FIELDS_MLB.md")
    print("- ESPN_API_FIELDS_NFL.md")

if __name__ == "__main__":
    main()
