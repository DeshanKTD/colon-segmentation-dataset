"""
Filter metadata.jsonl to keep only records with colon_name.
Writes filtered records to filtered_metadata.jsonl
"""

import json
from pathlib import Path

def filter_metadata():
    base_dir = Path(__file__).resolve().parent
    metadata_path = base_dir / 'metadata.jsonl'
    filtered_path = base_dir / 'filtered_metadata.jsonl'
    
    records_with_colon_name = 0
    records_without_colon_name = 0
    
    with open(metadata_path, 'r') as infile, open(filtered_path, 'w') as outfile:
        for line in infile:
            record = json.loads(line.strip())
            
            # Keep only records where colon_name is not None/null
            if record.get('colon_name') is not None:
                outfile.write(json.dumps(record) + '\n')
                records_with_colon_name += 1
            else:
                records_without_colon_name += 1
    
    print(f"Filtered metadata complete!")
    print(f"Records with colon_name: {records_with_colon_name}")
    print(f"Records without colon_name: {records_without_colon_name}")
    print(f"Output saved to: {filtered_path}")

if __name__ == "__main__":
    filter_metadata()
