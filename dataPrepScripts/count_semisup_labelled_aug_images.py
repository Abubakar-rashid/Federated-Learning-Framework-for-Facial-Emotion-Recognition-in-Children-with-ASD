#!/usr/bin/env python3
"""Count image files per class inside SemiSup_labelled_Aug under datasets.

Usage:
    python count_semisup_labelled_aug_images.py [--json]

The script locates the nearest `datasets` directory (walking up from cwd), finds
the first directory named `SemiSup_labelled_Aug`, and counts image files in each
immediate subdirectory (class). It prints a human-readable report by default or
JSON when `--json` is passed.
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

def find_semisup_dir(datasets_dir: Path):
    # locate directory named SemiSup_labelled_Aug anywhere under datasets
    for d in datasets_dir.rglob('SemiSup_labelled_Aug'):
        if d.is_dir():
            return d
    return None

def count_images_in_dir(d: Path):
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

    semisup = find_semisup_dir(datasets)
    if semisup is None:
        print('Could not find a SemiSup_labelled_Aug directory under', datasets, file=sys.stderr)
        sys.exit(3)

    results = {}
    classes_list = []
    for entry in sorted(semisup.iterdir()):
        if entry.is_dir():
            cnt = count_images_in_dir(entry)
            results[entry.name] = cnt
            classes_list.append({'class': entry.name, 'count': cnt})

    total = sum(results.values())

    if as_json:
        out = {'semisup_path': str(semisup), 'classes': classes_list, 'total': total}
        print(json.dumps(out, indent=2))
        return

    print('SemiSup_labelled_Aug path:', semisup)
    print('\nCounts per class:')
    for name, cnt in results.items():
        print(f'  {name}: {cnt}')
    print('\nTotal images:', total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count images per class in SemiSup_labelled_Aug')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()
    main(as_json=args.json)
