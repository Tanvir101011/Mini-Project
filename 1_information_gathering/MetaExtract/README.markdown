# MetaExtract

## Description
MetaExtract is a Python tool you can use to explore and modify metadata in JPEG image files on your own computer. It helps you learn about metadata, like camera details or copyright information stored in images, by extracting, editing, or removing it. Inspired by tools that analyze file metadata, MetaExtract is designed for your personal experimentation with files you own, in a private environment like your home computer.

**Important**: This tool is for your personal use only with files you own or have explicit permission to analyze. Using it on files or systems without clear authorization is illegal and could cause serious issues.

## Features
- Extracts EXIF metadata (e.g., camera model, date taken) and IPTC metadata (e.g., copyright, keywords) from JPEG files.
- Modifies specific metadata tags (e.g., Artist, Comment).
- Removes all metadata to clean an image file.
- Supports processing multiple files using glob patterns (e.g., `*.jpg`).
- Saves extracted metadata to a text file with timestamps and details.
- Quiet mode to reduce terminal output.
- Simple design for easy use in personal projects.

## Installation
1. **What You Need**:
   - Python 3.12 or later (check with `python3 --version`).
   - Pillow library for image processing.
   - A computer with image files you own (e.g., JPEG photos).
   - No special permissions needed unless accessing restricted files.
2. Install Pillow:
   ```bash
   pip3 install Pillow
   ```
3. Save the `metaextract.py` script to a folder (e.g., `/home/user/metaextract/`).
4. Run the script:
   ```bash
   python3 metaextract.py --help
   ```

## How to Use
MetaExtract lets you extract, modify, or remove metadata from JPEG files. You specify the files to process (single or multiple) and choose an action (extract, modify, or remove). Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Extract metadata from a single JPEG file:
```bash
python3 metaextract.py image.jpg
```

Process all JPEG files in a folder:
```bash
python3 metaextract.py *.jpg
```

### Options
- `files`: Image files or glob pattern (e.g., `image.jpg`, `*.jpg`).
- `-o, --output`: Output file for metadata (default: auto-generated, e.g., `metaextract_results_20250515_103010.txt`).
- `-q, --quiet`: Run quietly (logs to file only).
- `-m, --modify TAG VALUE`: Modify a metadata tag (e.g., `Artist "John Doe"`).
- `-r, --remove`: Remove all metadata from files.

### Using Each Feature

#### 1. Extracting Metadata
**What It Does**: Reads EXIF and IPTC metadata from JPEG files and displays or saves it.
**How to Use**:
1. Extract metadata from one file:
   ```bash
   python3 metaextract.py photo.jpg
   ```
2. Process multiple files:
   ```bash
   python3 metaextract.py *.jpg
   ```
**What Happens**:
- Metadata is logged to `metaextract.log` and a results file:
  ```
  2025-05-15 10:30:00 - Starting MetaExtract: Files=1
  2025-05-15 10:30:01 - Extracted metadata from photo.jpg: 12 EXIF, 3 IPTC tags
  2025-05-15 10:30:01 - Results saved to metaextract_results_20250515_103001.txt
  ```
- Results file example:
  ```
  File: photo.jpg
  EXIF Metadata:
    Make: Canon
    Model: EOS 5D
    DateTime: 2025:01:01 12:00:00
    Artist: Jane Doe
  IPTC Metadata:
    IPTC_(2, 25): nature, landscape
    IPTC_(2, 80): Jane Doe
    IPTC_(2, 120): Scenic view
  --------------------------------------------------
  ```
**Tips**:
- Use photos from your camera or test images with metadata.
- Check results in the output file for detailed tags.

#### 2. Modifying Metadata
**What It Does**: Changes a specific metadata tag (e.g., Artist, XPComment).
**How to Use**:
1. Set the Artist tag:
   ```bash
   python3 metaextract.py photo.jpg -m Artist "John Smith"
   ```
2. Modify a comment for multiple files:
   ```bash
   python3 metaextract.py *.jpg -m XPComment "Personal photo"
   ```
**What Happens**:
- The specified tag is updated:
  ```
  2025-05-15 10:35:00 - Starting MetaExtract: Files=1
  2025-05-15 10:35:01 - Modified Artist to 'John Smith' in photo.jpg
  ```
**Tips**:
- Supported tags include `Artist`, `XPComment`, `DateTime`. Check EXIF tag lists for more.
- Back up files before modifying, as changes overwrite the original.

#### 3. Removing Metadata
**What It Does**: Deletes all EXIF and IPTC metadata from files.
**How to Use**:
1. Remove metadata from one file:
   ```bash
   python3 metaextract.py photo.jpg -r
   ```
2. Clean multiple files:
   ```bash
   python3 metaextract.py *.jpg -r
   ```
**What Happens**:
- Metadata is removed, and no results file is created:
  ```
  2025-05-15 10:40:00 - Starting MetaExtract: Files=1
  2025-05-15 10:40:01 - Removed metadata from photo.jpg
  ```
**Tips**:
- Verify removal by extracting metadata afterward.
- Back up files, as metadata removal is permanent.

#### 4. Processing Multiple Files
**What It Does**: Handles multiple files using glob patterns.
**How to Use**:
1. Process all JPEGs in a folder:
   ```bash
   python3 metaextract.py *.jpg
   ```
2. Combine with other actions (e.g., modify):
   ```bash
   python3 metaextract.py *.jpg -m Artist "My Collection"
   ```
**What Happens**:
- All matching files are processed:
  ```
  2025-05-15 10:45:00 - Starting MetaExtract: Files=3
  2025-05-15 10:45:01 - Extracted metadata from img1.jpg: 10 EXIF, 2 IPTC tags
  2025-05-15 10:45:01 - Extracted metadata from img2.jpg: 8 EXIF, 0 IPTC tags
  2025-05-15 10:45:01 - Results saved to metaextract_results_20250515_104501.txt
  ```
**Tips**:
- Use `ls *.jpg` to confirm files before processing.
- Ensure enough disk space for output files.

#### 5. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   python3 metaextract.py photo.jpg -q
   ```
**What Happens**:
- No terminal output; logs go to `metaextract.log`:
  ```
  $ python3 metaextract.py photo.jpg -q
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:50:00 - Starting MetaExtract: Files=1
  2025-05-15 10:50:01 - Extracted metadata from photo.jpg: 12 EXIF, 3 IPTC tags
  ```
**Tips**:
- Check logs with `cat metaextract.log` or `tail -f metaextract.log`.
- Useful for processing many files without clutter.

#### 6. Custom Output File
**What It Does**: Saves metadata to a user-specified file.
**How to Use**:
1. Specify an output file:
   ```bash
   python3 metaextract.py photo.jpg -o my_metadata.txt
   ```
**What Happens**:
- Results are saved to the specified file:
  ```
  2025-05-15 10:55:00 - Starting MetaExtract: Files=1
  2025-05-15 10:55:01 - Results saved to my_metadata.txt
  ```
**Tips**:
- Use a unique name to avoid overwriting files.
- Check the file for results after processing.

### Example Workflow
To learn about image metadata on your computer:
1. Gather some JPEG photos you took or download test images.
2. Extract metadata:
   ```bash
   python3 metaextract.py photo1.jpg photo2.jpg -o metadata.txt
   ```
3. Modify the Artist tag:
   ```bash
   python3 metaextract.py photo1.jpg -m Artist "My Name"
   ```
4. Remove metadata from a file:
   ```bash
   python3 metaextract.py photo2.jpg -r -q
   ```
5. Check `metaextract.log` and `metadata.txt` for results.
6. Delete output files securely after use.

## Output
- Logs are saved to `metaextract.log`.
- Extracted metadata is saved to `metaextract_results_<timestamp>.txt` (or a custom file with `-o`).
- Example results file:
  ```
  File: photo.jpg
  EXIF Metadata:
    Make: Canon
    Model: EOS 5D
    DateTime: 2025:01:01 12:00:00
  IPTC Metadata:
    IPTC_(2, 25): nature
  --------------------------------------------------
  ```

## Important Notes
- **Environment**: Use MetaExtract only with files you own or have permission to analyze (e.g., photos on your computer).
- **File Types**: Currently supports JPEG files; other formats (e.g., PNG, PDF) are not supported.
- **Testing**: Use your own photos or create test JPEGs with metadata using a camera or image editor.

## Disclaimer
**Personal Use Only**: MetaExtract is for your personal learning with files you own or have explicit permission to analyze. Using it on files or systems without clear authorization is illegal and could lead to legal consequences, technical issues, or unintended harm. Always ensure you have permission from the file owner before extracting or modifying metadata.

**Safe Use**:
- **Controlled Setup**: Use on your personal computer with files you own to avoid affecting others.
- **Data Security**: Output files (`metaextract.log`, `metaextract_results_*.txt`) may contain sensitive data (e.g., GPS coordinates). Store them securely and delete them after use (e.g., `rm metaextract_*.txt`).
- **Legal Compliance**: Follow all applicable laws and regulations in your area.
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not use on files from others without permission (e.g., downloaded images).
- Do not share output files, as they may contain private data.
- Do not modify files you don’t own, as it could violate privacy or laws.

## Limitations
- Only supports JPEG files with EXIF/IPTC metadata.
- Limited tag modification (e.g., Artist, XPComment); advanced tags require further coding.
- Requires Pillow library; no support for other metadata formats (e.g., XMP).
- May fail on corrupted or non-standard JPEG files.

## Testing Tips
- Create test JPEGs: Take photos with a camera or use an image editor to add metadata.
- Verify files: Check with `ls *.jpg` before processing.
- Secure outputs: Delete files after use (`rm metaextract_*.txt`).
- Check logs in real-time: `tail -f metaextract.log`.
- Test modifications: Extract metadata after modifying to confirm changes.

## Troubleshooting
- **No metadata found**: Ensure the JPEG has EXIF/IPTC data (test with a camera photo).
- **File not found**: Verify file paths or glob patterns (e.g., `ls *.jpg`).
- **Pillow errors**: Install Pillow (`pip3 install Pillow`).
- **Unsupported tag**: Check supported EXIF tags (e.g., `Artist`, `DateTime`) in documentation.

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.