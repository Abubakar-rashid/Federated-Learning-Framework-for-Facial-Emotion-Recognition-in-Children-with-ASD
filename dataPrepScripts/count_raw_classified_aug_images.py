#!/usr/bin/env python3
"""Count image files per class inside Raw_Classified_Aug under datasets.

Usage:
    python count_raw_classified_aug_images.py [--json]

The script will search for a folder named `Raw_Classified_Aug` under the nearest
`datasets` directory (walking up from the current working directory). If multiple
matches are found, the first is used. For each immediate subdirectory (class)
it counts files with common image extensions and prints a small report.
"""

from pathlib import Path
import argparse
import json
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

def find_raw_aug(datasets_dir: Path):
    # find first directory named Raw_Classified_Aug under datasets (recursive)
    for d in datasets_dir.rglob('Raw_Classified_Aug'):
        if d.is_dir():
            return d
    return None

def count_images_in_dir(d: Path):
    # count files in directory and subdirectories with allowed extensions
    total = 0
    for f in d.rglob('*'):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            total += 1
    return total

def main(as_json: bool = False):
    try:
        datasets = find_datasets_dir()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    raw_aug = find_raw_aug(datasets)
    if raw_aug is None:
        print('Could not find a Raw_Classified_Aug directory under', datasets, file=sys.stderr)
        sys.exit(3)

    results = {}
    classes = []
    for entry in sorted(raw_aug.iterdir()):
        if entry.is_dir():
            cnt = count_images_in_dir(entry)
            results[entry.name] = cnt
            classes.append({'class': entry.name, 'count': cnt})

    total = sum(results.values())

    if as_json:
        out = {'raw_aug_path': str(raw_aug), 'classes': classes, 'total': total}
        print(json.dumps(out, indent=2))
        return

    print('Raw_Classified_Aug path:', raw_aug)
    print('\nCounts per class:')
    for name, cnt in results.items():
        print(f'  {name}: {cnt}')
    print('\nTotal images:', total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count images per class in Raw_Classified_Aug')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()
    main(as_json=args.json)
