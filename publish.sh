#!/bin/bash
# Publish the rendered site to GitHub Pages
# Usage: ./publish.sh

quarto publish gh-pages --no-render --no-prompt --no-browser
