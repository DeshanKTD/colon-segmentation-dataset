"""
Filter metadata.jsonl to keep only records with colon_name.
Writes filtered records to filtered_metadata.jsonl
"""

import json
from pathlib import Path
import argparse
import os

def create_json():
    base_dir = Path(__file__).resolve().parent
    filtered_path = base_dir / 'filtered_metadata.jsonl'
    rename_file_path = base_dir / 'rename_dataset.jsonl'
    
    records_with_colon_name = 0
    records_without_colon_name = 0
    
    with open(filtered_path, 'r') as infile, open(rename_file_path, 'w') as outfile:
        for line in infile:
            record = json.loads(line.strip())
                
            name = record.get('colon_name')
            file_name = record.get('name')
            
            new_record = {
                'annotation_name': name,
                'file_name': file_name,
                'image_name': file_name + '_conv-sitk.mha',
                'index': int(name.replace('colon_', ''))
            }
            
            outfile.write(json.dumps(new_record) + '\n')
            
            
    print(f"Filtered metadata complete!")
    print(f"Records with colon_name: {records_with_colon_name}")
    print(f"Records without colon_name: {records_without_colon_name}")
    print(f"Output saved to: {filtered_path}")
    
    

def rename_files(folder_path, naming_conv):
    # read jsonl 
    base_dir = Path(__file__).resolve().parent
    jsonl_path = base_dir / 'rename_dataset.jsonl'
    
    with open(jsonl_path, 'r') as infile:
        records = [json.loads(line.strip()) for line in infile]
    for record in records:
        old_name = record['image_name']
        new_name = record['annotation_name']
        index = record['index']
        
        if os.path.isfile(os.path.join(folder_path, old_name)):
            name = f"{naming_conv.upper()}_{new_name}_{index:03d}__0000.mha"
            old_path = os.path.join(folder_path, old_name)
            new_path = os.path.join(folder_path, name)
            os.rename(old_path, new_path)
            print(f"Renamed {old_name} to {name}")
        else:
            print(f"Error: File {old_name} does not exist in {folder_path}. Skipping.")
            


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Convert .mha files to .nrrd labelmap format for 3D Slicer recognition"
    )
    
    parser.add_argument(
        "--task",
        "-t",
        type=str,
        required=True,
        help="Task to perform: 'create_json' or 'rename_files'"
    )
    
    parser.add_argument(
        "--dir",
        "-i",
        type=str,
        required=True,
        help="Directory containing .mha files"
    )
    
    parser.add_argument(
        "--naming_conv",
        "-n",
        type=str,
        required=False,
        help="Naming convention to use for renaming files (required if task is 'rename_files')"
    )
    
    args = parser.parse_args()
    
    if args.task == 'create_json':
        create_json()
    elif args.task == 'rename_files':
        if not args.naming_conv:
            print("Error: --naming_conv is required when task is 'rename_files'")
        else:
            rename_files(args.dir, args.naming_conv)
    else:
        print(f"Error: Unknown task '{args.task}'. Valid tasks are 'create_json' and 'rename_files'.")
