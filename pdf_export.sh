#!/bin/bash
# Export a Reveal.js presentation to PDF using decktape
# Usage: ./pdf_export.sh <talk_name>
# Example: ./pdf_export.sh 25_EuclidWL_Marseille

if [ -z "$1" ]; then
    echo "Error: No talk name provided"
    echo "Usage: ./pdf_export.sh <talk_name>"
    echo "Example: ./pdf_export.sh 25_EuclidWL_Marseille"
    exit 1
fi

TALK_NAME="$1"
HTML_FILE="_site/${TALK_NAME}/${TALK_NAME}.html"
PDF_OUTPUT="${HOME}/Downloads/${TALK_NAME}.pdf"

if [ ! -f "$HTML_FILE" ]; then
    echo "Error: HTML file not found at $HTML_FILE"
    echo "Make sure the talk has been rendered first with 'quarto render'"
    exit 1
fi

echo "Converting $HTML_FILE to PDF..."
decktape reveal \
    -s 1920x1080 \
    -p 1500 \
    --pdf-title "${TALK_NAME}" \
    "$HTML_FILE" \
    "$PDF_OUTPUT"

echo "PDF exported to $PDF_OUTPUT"
