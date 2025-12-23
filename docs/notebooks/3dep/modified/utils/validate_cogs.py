#!/usr/bin/env python
"""
COG Validator Script for 3DEP Outputs.

Validates Cloud Optimized GeoTIFF (COG) files and optionally converts
non-compliant files to COG format.

Usage:
    python validate_cogs.py [--dir /path/to/tifs] [--verbose] [--fix]

Examples:
    # Validate all TIFs in default output directory
    python validate_cogs.py

    # Validate with verbose output
    python validate_cogs.py --verbose

    # Fix non-COG files in place
    python validate_cogs.py --fix

    # Validate specific directory
    python validate_cogs.py --dir /path/to/tifs --verbose

    # Generate JSON report
    python validate_cogs.py --json cog_report.json
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple
import json

from cog_utils import validate_cog, create_cog_gdal, get_cog_info


# Default output directory for 3DEP data
DEFAULT_OUTPUT_DIR = Path("/home/jovyan/data-store/data/output/3dep")


def find_tifs(directory: Path, recursive: bool = True) -> List[Path]:
    """
    Find all TIF files in directory.

    Args:
        directory: Directory to search
        recursive: Search subdirectories

    Returns:
        List of TIF file paths
    """
    if recursive:
        return list(directory.rglob("*.tif"))
    else:
        return list(directory.glob("*.tif"))


def validate_all_cogs(
    directory: Path,
    verbose: bool = False,
    fix: bool = False,
    recursive: bool = True
) -> Tuple[int, int, int, List[dict]]:
    """
    Validate all TIF files in a directory as COGs.

    Args:
        directory: Directory to search
        verbose: Print detailed information
        fix: Convert invalid files to COG
        recursive: Search subdirectories

    Returns:
        Tuple of (total, valid, fixed, results)
    """
    tifs = find_tifs(directory, recursive)

    total = len(tifs)
    valid = 0
    fixed = 0
    invalid = []
    results = []

    print(f"\nFound {total} TIF files in {directory}")
    print("=" * 70)

    for tif_path in sorted(tifs):
        is_cog, errors, warnings = validate_cog(tif_path)

        result = {
            "name": tif_path.name,
            "path": str(tif_path),
            "is_cog": is_cog,
            "errors": errors,
            "warnings": warnings
        }

        if is_cog:
            valid += 1
            status = "VALID"
            if warnings:
                status = "VALID*"  # Valid with warnings
        else:
            invalid.append(tif_path)
            status = "INVALID"

        # Print status line
        print(f"[{status:^8}] {tif_path.name}")

        if verbose:
            info = get_cog_info(tif_path)
            result.update(info)
            print(f"          Size: {info['file_size_mb']:.1f} MB | "
                  f"Dims: {info['width']}x{info['height']} | "
                  f"Overviews: {info['overview_count']}")

            for warn in warnings:
                print(f"          WARNING: {warn}")
            for err in errors:
                print(f"          ERROR: {err}")

        results.append(result)

    # Fix invalid files if requested
    if fix and invalid:
        print("\n" + "=" * 70)
        print(f"Converting {len(invalid)} invalid files to COG format...")
        print("-" * 70)

        for tif_path in invalid:
            print(f"  Converting: {tif_path.name}...", end=" ", flush=True)
            try:
                create_cog_gdal(tif_path, in_place=True)
                fixed += 1
                print("DONE")

                # Update result
                for r in results:
                    if r["path"] == str(tif_path):
                        r["fixed"] = True
                        r["is_cog"] = True
                        break

            except Exception as e:
                print(f"FAILED: {e}")
                for r in results:
                    if r["path"] == str(tif_path):
                        r["fix_error"] = str(e)
                        break

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total files:     {total}")
    print(f"  Valid COGs:      {valid}")
    print(f"  Invalid:         {len(invalid)}")
    if fix:
        print(f"  Fixed:           {fixed}")
        print(f"  Fix failures:    {len(invalid) - fixed}")
    print("=" * 70)

    return total, valid, fixed, results


def main():
    parser = argparse.ArgumentParser(
        description="Validate Cloud Optimized GeoTIFF (COG) files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory containing TIF files (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed validation information"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Convert non-COG files to COG format in place"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't search subdirectories"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Output validation results to JSON file"
    )

    args = parser.parse_args()

    # Validate directory exists
    if not args.dir.exists():
        print(f"Error: Directory not found: {args.dir}")
        sys.exit(1)

    # Run validation
    total, valid, fixed, results = validate_all_cogs(
        args.dir,
        verbose=args.verbose,
        fix=args.fix,
        recursive=not args.no_recursive
    )

    # Output JSON report if requested
    if args.json:
        report = {
            "directory": str(args.dir),
            "total_files": total,
            "valid_cogs": valid,
            "invalid": total - valid,
            "fixed": fixed,
            "files": results
        }

        with open(args.json, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nValidation report saved to: {args.json}")

    # Exit with error code if there are invalid/unfixed files
    if valid + fixed < total:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
