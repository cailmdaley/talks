#!/usr/bin/env python3
import os
from datetime import datetime


def generate_index_html():
    base_dir = "."
    exclude_dirs = {
        "images",
        "template",
        "_template_quarto",
        "unused_images",
        "_site",
        ".git",
    }
    index_file_path = os.path.join(base_dir, "index.html")
    talks = []

    for root, dirs, files in os.walk(base_dir):
        # Only consider directories at the base level
        if root == base_dir:
            for dir_name in dirs:
                if dir_name not in exclude_dirs:
                    index_html_path = os.path.join(root, dir_name, "index.html")
                    if os.path.exists(index_html_path):
                        last_modified_time = os.path.getmtime(index_html_path)
                        last_modified_date = datetime.fromtimestamp(
                            last_modified_time
                        ).strftime("%B %d, %Y")
                        talks.append((dir_name, last_modified_date, last_modified_time))

    # Sort talks by last modified time in descending order
    talks.sort(key=lambda x: x[2], reverse=True)

    with open(index_file_path, "w") as index_file:
        index_file.write("<!DOCTYPE html>\n<html>\n<head>\n")
        index_file.write('<meta charset="utf-8">\n')
        index_file.write("<title>Index of Talks</title>\n")
        index_file.write("<style>\n")
        index_file.write("body { font-family: Arial, sans-serif; margin: 40px; }\n")
        index_file.write("h1 { color: #333; }\n")
        index_file.write("hr { width: 25em; margin-left: 0; }\n")
        index_file.write("ul { list-style-type: disc; padding-left: 20px; }\n")
        index_file.write("li { margin: 10px 0; }\n")
        index_file.write(
            "a { text-decoration: none; color: #1a73e8; font-size: 18px; }\n"
        )
        index_file.write("a:hover { text-decoration: underline; }\n")
        index_file.write("</style>\n")
        index_file.write("</head>\n<body>\n")
        index_file.write("<h1>Index of Talks</h1>\n")
        index_file.write("<hr>\n")
        index_file.write("<ul>\n")

        for dir_name, last_modified_date, _ in talks:
            index_file.write(
                f'<li><a href="{dir_name}/index.html">{dir_name}</a> ({last_modified_date})</li>\n'
            )

        index_file.write("</ul>\n")
        index_file.write("</body>\n</html>\n")


if __name__ == "__main__":
    generate_index_html()
