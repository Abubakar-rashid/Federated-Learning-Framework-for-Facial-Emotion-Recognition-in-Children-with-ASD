"""
Script to extract autistic-labeled images from ASD_8k dataset
Consolidates images from train, test, and valid sets into Concatenated folder
"""

import os
import shutil
import csv
from pathlib import Path

# Define paths
base_path = Path(r"c:\Workspace_1\Deep learning\Sem Proj\Federated Learning for FER in ASD children\datasets")
asd_8k_path = base_path / "ASD_8k"
concatenated_path = base_path / "Concatenated"

# Create Concatenated folder if it doesn't exist
concatenated_path.mkdir(parents=True, exist_ok=True)

# Define the sets to process
sets = ['train', 'test', 'valid']

# Statistics
total_copied = 0
errors = []
all_autistic_files = {}  # Dictionary to track filenames across sets

print("="*70)
print("Finding Duplicate Autistic Images Across Sets")
print("="*70)

# First pass: collect all autistic filenames from each set
for set_name in sets:
    print(f"\nProcessing {set_name} set...")
    
    # Paths for current set
    set_path = asd_8k_path / set_name
    csv_file = set_path / "_classes.csv"
    
    if not csv_file.exists():
        print(f"  WARNING: CSV file not found: {csv_file}")
        errors.append(f"CSV not found: {csv_file}")
        continue
    
    # Read CSV and filter autistic images
    autistic_files = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if Autistic column has value 1
            if row['Autistic'] == '1':
                autistic_files.append(row['filename'])
    
    # Track which sets each filename appears in
    for filename in autistic_files:
        if filename not in all_autistic_files:
            all_autistic_files[filename] = []
        all_autistic_files[filename].append(set_name)
    
    print(f"  Found {len(autistic_files)} autistic images in {set_name} set")

# Analyze duplicates
duplicates = {filename: sets for filename, sets in all_autistic_files.items() if len(sets) > 1}
unique_files = {filename: sets for filename, sets in all_autistic_files.items() if len(sets) == 1}

print("\n" + "="*70)
print("Duplicate Analysis Results")
print("="*70)
print(f"Total unique filenames: {len(all_autistic_files)}")
print(f"Filenames appearing in multiple sets: {len(duplicates)}")
print(f"Filenames appearing in only one set: {len(unique_files)}")

if duplicates:
    print(f"\n{'='*70}")
    print(f"Files appearing in multiple sets ({len(duplicates)} files):")
    print(f"{'='*70}")
    
    # Count by number of sets
    in_two_sets = sum(1 for sets in duplicates.values() if len(sets) == 2)
    in_three_sets = sum(1 for sets in duplicates.values() if len(sets) == 3)
    
    print(f"  Appearing in 2 sets: {in_two_sets} files")
    print(f"  Appearing in all 3 sets: {in_three_sets} files")
    
    # Show first 20 duplicates
    print(f"\nFirst 20 duplicate filenames:")
    for i, (filename, sets_list) in enumerate(list(duplicates.items())[:20], 1):
        print(f"  {i}. {filename}")
        print(f"     Found in: {', '.join(sets_list)}")
    
    if len(duplicates) > 20:
        print(f"\n  ... and {len(duplicates) - 20} more duplicates")
    
    # Save full duplicate list to file
    duplicate_report = base_path / "duplicate_autistic_images.txt"
    with open(duplicate_report, 'w') as f:
        f.write("Duplicate Autistic Images Across Train/Test/Valid Sets\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total duplicate filenames: {len(duplicates)}\n")
        f.write(f"Files in 2 sets: {in_two_sets}\n")
        f.write(f"Files in all 3 sets: {in_three_sets}\n\n")
        f.write("="*70 + "\n")
        f.write("Complete List:\n")
        f.write("="*70 + "\n\n")
        
        for filename, sets_list in sorted(duplicates.items()):
            f.write(f"{filename}\n")
            f.write(f"  Sets: {', '.join(sets_list)}\n\n")
    
    print(f"\nFull duplicate report saved to: {duplicate_report}")

print("\n" + "="*70)
print("Copying Files to Concatenated Folder (with set prefixes)")
print("="*70)

# Second pass: copy files with set prefix to avoid conflicts
for set_name in sets:
    print(f"\nProcessing {set_name} set...")
    
    # Paths for current set
    set_path = asd_8k_path / set_name
    csv_file = set_path / "_classes.csv"
    
    if not csv_file.exists():
        continue
    
    # Read CSV and filter autistic images
    autistic_files = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Autistic'] == '1':
                autistic_files.append(row['filename'])
    
    print(f"  Found {len(autistic_files)} autistic images in {set_name} set")
    
    # Copy files
    copied = 0
    skipped = 0
    for filename in autistic_files:
        src_file = set_path / filename
        # Add set prefix ONLY for files that appear in multiple sets
        if filename in duplicates:
            dst_file = concatenated_path / f"{set_name}_{filename}"
        else:
            dst_file = concatenated_path / filename
        
        if not src_file.exists():
            skipped += 1
            continue
            
        try:
            # Copy all files (duplicates get set prefix)
            shutil.copy2(src_file, dst_file)
            copied += 1
        except Exception as e:
            error_msg = f"Error copying {filename}: {str(e)}"
            print(f"  ERROR: {error_msg}")
            errors.append(error_msg)
            skipped += 1
    
    print(f"  Successfully copied {copied} images from {set_name} set (skipped {skipped} missing files)")
    total_copied += copied

print("\n" + "="*70)
print("Extraction Complete!")
print("="*70)
print(f"Total autistic images copied: {total_copied}")
print(f"Destination folder: {concatenated_path}")

if errors:
    print(f"\n{len(errors)} errors/warnings occurred:")
    for error in errors[:10]:  # Show first 10 errors
        print(f"  - {error}")
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more errors")
else:
    print("\nNo errors occurred!")

# Verify the result
if concatenated_path.exists():
    file_count = len(list(concatenated_path.glob("*.jpg")))
    print(f"\nVerification: {file_count} files in Concatenated folder")
