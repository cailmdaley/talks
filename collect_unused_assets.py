#!/usr/bin/env python3
import os
import shutil

def find_used_assets():
    used_assets = set()
    for root, dirs, files in os.walk('.'):
        if 'index.md' in files:
            with open(os.path.join(root, 'index.md'), 'r') as f:
                content = f.read()
                for line in content.splitlines():
                    if 'assets/' in line:
                        start = line.find('assets/')
                        end = line.find(')', start)
                        if end == -1:
                            end = len(line)
                        asset = line[start:end]
                        used_assets.add(asset)
    return used_assets

def move_unused_assets(used_assets):
    assets_folder = './assets'
    unused_assets_folder = './unused_assets'
    if not os.path.exists(unused_assets_folder):
        os.makedirs(unused_assets_folder)
    
    for root, dirs, files in os.walk(assets_folder):
        for file in files:
            asset_path = os.path.join(root, file)
            relative_path = os.path.relpath(asset_path, '.')
            if relative_path not in used_assets:
                print(f'{relative_path} is unused, moving to {unused_assets_folder}')
                shutil.move(asset_path, os.path.join(unused_assets_folder, file))

if __name__ == "__main__":
    used_assets = find_used_assets()
    move_unused_assets(used_assets)