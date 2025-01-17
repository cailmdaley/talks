#!/usr/bin/env python3
import os
import shutil

def find_used_images():
    used_images = set()
    for root, dirs, files in os.walk('.'):
        if 'index.md' in files:
            with open(os.path.join(root, 'index.md'), 'r') as f:
                content = f.read()
                for line in content.splitlines():
                    start = 0
                    while 'images/' in line[start:]:
                        start = line.find('images/', start)
                        end = line.find(')', start)
                        if end == -1:
                            end = len(line)
                        asset = line[start:end]
                        used_images.add(asset)
                        start = end
    return used_images

def move_unused_images(used_images):
    images_folder = './images'
    unused_images_folder = './unused_images'
    if not os.path.exists(unused_images_folder):
        os.makedirs(unused_images_folder)
    
    for root, dirs, files in os.walk(images_folder):
        for file in files:
            asset_path = os.path.join(root, file)
            relative_path = os.path.relpath(asset_path, '.')
            if relative_path not in used_images:
                print(f'{relative_path} is unused, moving to {unused_images_folder}')
                shutil.move(asset_path, os.path.join(unused_images_folder, file))

if __name__ == "__main__":
    used_images = find_used_images()
    move_unused_images(used_images)