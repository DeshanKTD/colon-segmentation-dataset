#!/usr/bin/env python3
"""
Convert .mha files to proper segmentation format for 3D Slicer.

This script loads .mha files from an input directory and converts them
to proper segmentation files that will be recognized as labelmap volumes
in 3D Slicer, then saves them as .nrrd files to an output directory.

Usage:
    python fix_segmentation_metadata.py --input_dir <path> --output_dir <path>
"""

import os
import argparse
from pathlib import Path
import SimpleITK as sitk


def convert_to_segmentation(image):
    """
    Convert an image to proper segmentation format.
    
    Args:
        image: SimpleITK image object
        
    Returns:
        SimpleITK image object configured as a segmentation
    """
    # Cast to unsigned char (uint8) or unsigned short (uint16) for labelmap
    # Determine max value to choose appropriate type
    stats_filter = sitk.StatisticsImageFilter()
    stats_filter.Execute(image)
    max_value = stats_filter.GetMaximum()
    
    if max_value <= 255:
        # Use UInt8 for labels 0-255
        segmentation = sitk.Cast(image, sitk.sitkUInt8)
    elif max_value <= 65535:
        # Use UInt16 for more labels
        segmentation = sitk.Cast(image, sitk.sitkUInt16)
    else:
        # Use UInt32 for very large label values
        segmentation = sitk.Cast(image, sitk.sitkUInt32)
    
    # Copy metadata from original image
    for key in image.GetMetaDataKeys():
        segmentation.SetMetaData(key, image.GetMetaData(key))
    
    # Add NRRD-specific metadata for labelmap recognition in Slicer
    # The "kinds" field tells Slicer this is a labelmap, not a scalar volume
    segmentation.SetMetaData("kinds", "domain domain domain")
    segmentation.SetMetaData("type", "unsigned char" if max_value <= 255 else "unsigned short")
    
    return segmentation


def process_directory(input_dir, output_dir):
    """
    Process all .mha files in input directory and save as .nrrd to output directory.
    
    Args:
        input_dir: Path to input directory containing .mha files
        output_dir: Path to output directory for converted .nrrd labelmap files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .mha files recursively
    mha_files = list(input_path.rglob("*.mha"))
    # sort files for consistent processing order
    mha_files.sort()
    
    if not mha_files:
        print(f"No .mha files found in {input_dir}")
        return
    
    print(f"Found {len(mha_files)} .mha file(s) to process")
    
    for mha_file in mha_files:
        try:
            print(f"\nProcessing: {mha_file.relative_to(input_path)}")
            
            # Read the image
            image = sitk.ReadImage(str(mha_file))
            print(f"  Original pixel type: {image.GetPixelIDTypeAsString()}")
            print(f"  Image size: {image.GetSize()}")
            
            # Convert to segmentation format
            segmentation = convert_to_segmentation(image)
            print(f"  Converted pixel type: {segmentation.GetPixelIDTypeAsString()}")
            
            # Preserve directory structure in output, but change extension to .nrrd
            relative_path = mha_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix('.nrrd')
            
            # Create parent directory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the segmentation as NRRD (Slicer's preferred format)
            sitk.WriteImage(segmentation, str(output_file), True)  # True = use compression
            print(f"  Saved to: {output_file.relative_to(output_path)}")
            print(f"  Format: NRRD (Slicer labelmap)")
            
        except Exception as e:
            print(f"  ERROR processing {mha_file.name}: {e}")
            continue
    
    print(f"\n✓ Processing complete. Output saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert .mha files to .nrrd labelmap format for 3D Slicer recognition"
    )
    parser.add_argument(
        "--input_dir",
        "-i",
        type=str,
        required=True,
        help="Input directory containing .mha segmentation files"
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        required=True,
        help="Output directory for converted .nrrd labelmap files"
    )
    
    args = parser.parse_args()
    
    # Validate input directory exists
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory does not exist: {args.input_dir}")
        return
    
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    
    process_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
