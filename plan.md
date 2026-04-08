# PDF to Markdown Conversion Plan for Euclid Conference Talks

## Objective
Convert multiple Euclid conference presentation PDFs to markdown format for easy searching and reading with Claude, storing output in `docs/` directory.

## Selected Approach
**Tool**: Marker ([datalab-to/marker](https://github.com/datalab-to/marker))
**LLM Backend**: Google Gemini API (free tier: 1500 requests/day)
**Model**: gemini-2.0-flash (default, fastest)

## Why This Approach
- Marker specialized for academic PDFs with tables, equations, complex layouts
- Gemini free tier sufficient for conference talk volumes (~20-30 presentations)
- `--use_llm` flag enables high-accuracy conversion vs base mode
- Handles presentation-specific challenges (tables spanning slides, LaTeX)

## Installation Steps
```bash
pip install marker-pdf
```

## Environment Setup
Set Gemini API key as environment variable:
```bash
export GOOGLE_API_KEY="your-key-here"
```

Or store in `.env` file for persistence.

## Batch Conversion Script Requirements

### Input
- Directory containing PDF files (e.g., `euclid_talks/`)
- Each PDF is a conference presentation

### Output
- Markdown files written to `docs/` directory
- Naming convention: sanitized version of PDF filename (e.g., `talk_name.md`)
- Preserve subdirectory structure if PDFs organized by session/topic

### Script Functionality
1. Accept input directory path as command-line argument
2. Recursively find all PDF files in input directory
3. For each PDF:
   - Convert using Marker with `--use_llm` flag
   - Use Gemini API (gemini-2.0-flash model)
   - Write output to `docs/` with `.md` extension
   - Preserve original filename (sanitized for filesystem)
   - Log conversion progress and any errors
4. Handle errors gracefully (continue processing remaining PDFs if one fails)
5. Optional: Add metadata header to each markdown file (original filename, conversion date)

### Marker Command Structure
```bash
marker_single /path/to/input.pdf /path/to/output_dir \
  --use_llm \
  --llm_provider gemini \
  --llm_model gemini-2.0-flash
```

Or for batch processing:
```bash
marker /path/to/pdf_directory /path/to/output_dir \
  --use_llm \
  --llm_provider gemini \
  --llm_model gemini-2.0-flash
```

## Python Script Template (Recommended)
```python
import os
import subprocess
from pathlib import Path

def convert_pdfs_to_markdown(input_dir, output_dir="docs"):
    """
    Convert all PDFs in input_dir to markdown using Marker with Gemini LLM.

    Args:
        input_dir: Path to directory containing PDF files
        output_dir: Path to output directory (default: docs/)
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Find all PDF files
    pdf_files = list(Path(input_dir).rglob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files to convert")

    for pdf_path in pdf_files:
        print(f"Converting {pdf_path.name}...")

        # Use marker_single for individual file conversion
        cmd = [
            "marker_single",
            str(pdf_path),
            output_dir,
            "--use_llm",
            "--llm_provider", "gemini",
            "--llm_model", "gemini-2.0-flash"
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✓ Converted {pdf_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to convert {pdf_path.name}: {e.stderr}")
            continue

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python convert_pdfs.py <input_directory> [output_directory]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "docs"

    convert_pdfs_to_markdown(input_dir, output_dir)
```

## Alternative: Direct Batch Processing
Marker has built-in batch processing:
```bash
marker /path/to/euclid_talks /path/to/docs \
  --use_llm \
  --llm_provider gemini \
  --llm_model gemini-2.0-flash
```

This may be simpler than custom script if default behavior is acceptable.

## Cost Estimate
- **~20 talks × 30 slides = 600 pages**
- **Cost with Gemini free tier**: $0 (well under 1500 req/day limit)
- **Cost if exceeding free tier**: ~$0.05-0.10 for entire conference

## Post-Conversion
Once markdown files are in `docs/`, Claude can search and reference them easily during conversations using the Read, Grep, and Glob tools.

## Notes for User
- Get Gemini API key from: https://ai.google.dev/
- Note: You mentioned getting OpenAI key - Gemini is recommended instead for free tier, but Marker supports OpenAI if you prefer (`--llm_provider openai`)
- Consider organizing PDFs by topic/session before conversion to preserve structure in `docs/`
