#!/usr/bin/env python3
"""Copy images from Train/Test of the "Autistic Children Emotions - Dr. Fatma M. Talaat" dataset
into the matching folders under Raw_Classified_Aug.

This script will:
- Locate a top-level `datasets` folder by walking up from the current working directory.
- Look for the dataset at: datasets / "Autistic Children Emotions - Dr. Fatma M. Talaat" / "Autistic Children Emotions - Dr. Fatma M. Talaat"
  (there is a nested folder in the repo). If that path doesn't exist it will try the single-level
  `datasets / "Autistic Children Emotions - Dr. Fatma M. Talaat"` path as a fallback.
- For each class subfolder in Train/ and Test/, copy image files into Raw_Classified_Aug/<class>.

Usage:
    python copy_images_to_raw_classified_aug.py [--dry-run]

By default the script performs real copies. Use --dry-run to only show actions.
"""

from pathlib import Path
import shutil
import argparse
import sys

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff'}

def find_datasets_dir(max_up=8):
    p = Path.cwd()
    for _ in range(max_up):
        candidate = p / 'datasets'
        if candidate.exists():
            return candidate.resolve()
        p = p.parent
    raise FileNotFoundError('datasets folder not found in cwd or parent directories')

def copy_images_for_dataset(base_dataset_dir: Path, dry_run: bool = False):
    raw_aug = base_dataset_dir / 'Raw_Classified_Aug'
    if not raw_aug.exists():
        if dry_run:
            print(f"DRY RUN: would create {raw_aug}")
        else:
            raw_aug.mkdir(parents=True, exist_ok=True)

    total_copied = 0
    processed_classes = set()
    skipped_files = 0

    for split in ('Train', 'Test'):
        split_dir = base_dataset_dir / split
        if not split_dir.exists():
            print(f"Warning: expected split folder not found: {split_dir}")
            continue

        for class_dir in sorted([d for d in split_dir.iterdir() if d.is_dir()]):
            processed_classes.add(class_dir.name)
            dest_class_dir = raw_aug / class_dir.name
            if not dest_class_dir.exists() and not dry_run:
                dest_class_dir.mkdir(parents=True, exist_ok=True)

            for src_file in class_dir.iterdir():
                if not src_file.is_file():
                    continue
                if src_file.suffix.lower() not in IMAGE_EXTS:
                    skipped_files += 1
                    continue

                dest_file = dest_class_dir / src_file.name
                # avoid overwrite: if exists, choose a new name with numeric suffix
                if dest_file.exists():
                    stem = src_file.stem
                    suffix = src_file.suffix
                    i = 1
                    while True:
                        candidate = dest_class_dir / f"{stem}_{i}{suffix}"
                        if not candidate.exists():
                            dest_file = candidate
                            break
                        i += 1

                if dry_run:
                    print(f"DRY RUN: would copy {src_file} -> {dest_file}")
                else:
                    shutil.copy2(src_file, dest_file)
                total_copied += 1

    return {
        'classes': sorted(processed_classes),
        'copied': total_copied,
        'skipped_non_images': skipped_files,
    }

def main(dry_run: bool = False):
    try:
        datasets_dir = find_datasets_dir()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    # Primary expected location (nested folder as in repo):
    nested = datasets_dir / 'Autistic Children Emotions - Dr. Fatma M. Talaat' / 'Autistic Children Emotions - Dr. Fatma M. Talaat'
    if nested.exists():
        base = nested
    else:
        fallback = datasets_dir / 'Autistic Children Emotions - Dr. Fatma M. Talaat'
        if fallback.exists():
            base = fallback
        else:
            print('Could not find the expected dataset folder under datasets/', file=sys.stderr)
            print('Searched for:', nested, 'and', fallback, file=sys.stderr)
            sys.exit(3)

    print('Using dataset base folder:', base)
    result = copy_images_for_dataset(base, dry_run=dry_run)

    print('\nSummary:')
    print('  Classes processed:', len(result['classes']))
    print('  Classes names:', result['classes'])
    print('  Files copied:', result['copied'])
    print('  Non-image files skipped:', result['skipped_non_images'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy images from Train/Test to Raw_Classified_Aug')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be copied without performing copy')
    args = parser.parse_args()
    main(dry_run=args.dry_run)
