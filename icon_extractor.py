#!/usr/bin/env python3

import os
import sys
import plistlib
import subprocess
import shutil
import tempfile
from pathlib import Path
import datetime

class IconExtractor:
    def __init__(self):
        self.temp_dir = None
        self.mount_point = None

    def cleanup(self):
        """Clean up temporary files and mounts"""
        try:
            if self.mount_point and os.path.exists(self.mount_point):
                subprocess.run(
                    ['hdiutil', 'detach', self.mount_point, '-quiet'], 
                    check=False,
                    capture_output=True,
                    timeout=30
                )
                try:
                    os.rmdir(self.mount_point)
                except OSError:
                    pass
                
        except Exception as e:
            print(f"Warning: Error during unmount: {e}")
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            print(f"\nPreserving temporary directory for debugging: {self.temp_dir}")

    def mount_dmg(self, dmg_path):
        """Mount a DMG and return the mount point"""
        self.mount_point = tempfile.mkdtemp()
        try:
            subprocess.run(
                ['hdiutil', 'attach', dmg_path, '-mountpoint', self.mount_point, '-quiet'],
                check=True
            )
            return self.mount_point
        except subprocess.CalledProcessError:
            raise Exception(f"Failed to mount DMG: {dmg_path}")

    def extract_pkg(self, pkg_path):
        """Extract a PKG and return the extraction directory"""
        try:
            # Create a simple directory path
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            self.temp_dir = os.path.join(tempfile.gettempdir(), f'pkg_extract_{timestamp}')
            
            # Remove directory if it exists and create a new empty one
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            os.makedirs(self.temp_dir)
            
            print(f"Created temporary directory: {self.temp_dir}")
            
            # Use xar to extract the PKG
            print(f"Attempting to extract PKG using xar: {pkg_path}")
            result = subprocess.run(
                ['xar', '-xf', pkg_path, '-C', self.temp_dir],
                check=True,
                capture_output=True,
                text=True
            )
            
            if result.stderr:
                print(f"Warning during PKG extraction: {result.stderr}")
            
            print("\nInitial PKG contents:")
            for item in os.listdir(self.temp_dir):
                print(f"- {item}")
                item_path = os.path.join(self.temp_dir, item)
                if item.endswith('.pkg') and os.path.isdir(item_path):
                    nested_pkg_dir = item_path
                    print(f"\nFound nested PKG directory: {nested_pkg_dir}")
                    
                    # Create directory for nested PKG contents
                    nested_dir = os.path.join(self.temp_dir, 'nested_pkg_extract')
                    os.makedirs(nested_dir, exist_ok=True)
                    
                    # Look for Payload in nested PKG directory
                    nested_payload = os.path.join(nested_pkg_dir, 'Payload')
                    if os.path.exists(nested_payload):
                        print("\nFound Payload in nested PKG, extracting...")
                        payload_extract_dir = os.path.join(nested_dir, 'PayloadExtracted')
                        os.makedirs(payload_extract_dir, exist_ok=True)
                        
                        result = subprocess.run(
                            ['tar', '-xvf', nested_payload, '-C', payload_extract_dir],
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        
                        print("\nExtracted nested Payload contents:")
                        for root, dirs, files in os.walk(payload_extract_dir):
                            print(f"\nDirectory: {root}")
                            for d in dirs:
                                print(f"  Dir: {d}")
                            for f in files:
                                print(f"  File: {f}")
                        
                        return payload_extract_dir
            
            # If no nested PKG with payload found, check original PKG payload
            payload_path = os.path.join(self.temp_dir, 'Payload')
            if os.path.exists(payload_path):
                print("\nFound Payload file in original PKG, extracting...")
                payload_extract_dir = os.path.join(self.temp_dir, 'PayloadExtracted')
                os.makedirs(payload_extract_dir, exist_ok=True)
                
                result = subprocess.run(
                    ['tar', '-xvf', payload_path, '-C', payload_extract_dir],
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                print("\nExtracted Payload contents:")
                for root, dirs, files in os.walk(payload_extract_dir):
                    print(f"\nDirectory: {root}")
                    for d in dirs:
                        print(f"  Dir: {d}")
                    for f in files:
                        print(f"  File: {f}")
                
                return payload_extract_dir
            
            # If no Payload found anywhere, return the original extraction directory
            return self.temp_dir
            
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise Exception(f"Failed to extract PKG: {pkg_path}. Error: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise Exception(f"Error extracting PKG: {str(e)}")

    def find_app_in_directory(self, directory):
        """Find the first .app bundle in a directory"""
        print(f"Searching for .app bundle in: {directory}")
        for root, dirs, files in os.walk(directory):
            print(f"Checking directory: {root}")
            # Check for .app directories
            for dir in dirs:
                if dir.endswith('.app'):
                    full_path = os.path.join(root, dir)
                    print(f"Found .app bundle: {full_path}")
                    return full_path
            # Check for .app files
            for file in files:
                if file.endswith('.app'):
                    full_path = os.path.join(root, file)
                    print(f"Found .app bundle: {full_path}")
                    return full_path
        return None

    def find_icon_in_pkg(self, directory):
        """Find icon files directly in PKG contents"""
        print(f"Searching for icon files in: {directory}")
        for root, _, files in os.walk(directory):
            print(f"Checking directory: {root}")
            for file in files:
                if file.endswith('.icns'):
                    full_path = os.path.join(root, file)
                    print(f"Found icon file: {full_path}")
                    return full_path
        return None

    def get_icon_path_from_app(self, app_path):
        """Get the icon path from an app's Info.plist"""
        try:
            plist_path = os.path.join(app_path, 'Contents/Info.plist')
            if not os.path.exists(plist_path):
                return None

            with open(plist_path, 'rb') as f:
                plist = plistlib.load(f)

            # Get icon filename from plist
            icon_filename = plist.get('CFBundleIconFile', '')
            if not icon_filename:
                app_name = os.path.basename(app_path)
                icon_filename = app_name

            # Add .icns extension if missing
            if not icon_filename.endswith('.icns'):
                icon_filename += '.icns'

            icon_path = os.path.join(app_path, 'Contents/Resources', icon_filename)
            return icon_path if os.path.exists(icon_path) else None

        except Exception as e:
            print(f"Error reading plist: {e}")
            return None

    def convert_icns_to_png(self, icns_path, png_path):
        """Convert .icns to .png using sips or PIL as fallback"""
        try:
            # First try using sips (macOS)
            print("Converting .icns to .png using sips...")
            result = subprocess.run(
                ['sips', '-s', 'format', 'png', icns_path, '--out', png_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"Converted icon to PNG: {png_path}")
                return True
            
        except FileNotFoundError:
            print("sips not found, falling back to PIL...")
            try:
                from PIL import Image
                
                # Convert icns to png using iconutil first (macOS)
                temp_iconset = icns_path + '.iconset'
                os.makedirs(temp_iconset, exist_ok=True)
                
                subprocess.run(['iconutil', '-c', 'iconset', icns_path, '-o', temp_iconset], check=True)
                
                # Find the largest PNG in the iconset
                largest_size = 0
                largest_file = None
                
                for file in os.listdir(temp_iconset):
                    if file.endswith('.png'):
                        img_path = os.path.join(temp_iconset, file)
                        with Image.open(img_path) as img:
                            width, height = img.size
                            size = width * height
                            if size > largest_size:
                                largest_size = size
                                largest_file = img_path
                
                if largest_file:
                    # Open and resize the largest image
                    with Image.open(largest_file) as img:
                        # Calculate new size maintaining aspect ratio
                        ratio = min(300/img.width, 300/img.height)
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                        resized_img.save(png_path, 'PNG')
                    print(f"Converted icon to PNG using PIL: {png_path}")
                    
                # Cleanup
                shutil.rmtree(temp_iconset, ignore_errors=True)
                return True
                
            except ImportError:
                print("PIL not installed. Cannot convert icon.")
                return False
                
        return False

    def extract_icon(self, input_path, output_path):
        """Main method to extract icon from DMG or PKG"""
        try:
            if not os.path.exists(input_path):
                raise Exception(f"Input file does not exist: {input_path}")

            # Handle DMG
            if input_path.lower().endswith('.dmg'):
                mount_point = self.mount_dmg(input_path)
                app_path = self.find_app_in_directory(mount_point)
                if not app_path:
                    raise Exception("No .app bundle found in DMG")
                icon_path = self.get_icon_path_from_app(app_path)

            # Handle PKG
            elif input_path.lower().endswith('.pkg'):
                extract_dir = self.extract_pkg(input_path)
                
                # First try to find an .app bundle
                app_path = self.find_app_in_directory(extract_dir)
                if app_path:
                    print(f"Found app bundle at: {app_path}")
                    icon_path = self.get_icon_path_from_app(app_path)
                else:
                    print("No .app bundle found, searching for icon files directly...")
                    icon_path = self.find_icon_in_pkg(extract_dir)

            else:
                raise Exception("Input file must be a .dmg or .pkg")

            if not icon_path:
                # List contents of extraction directory for debugging
                print("\nDirectory contents:")
                for root, dirs, files in os.walk(extract_dir):
                    print(f"\nDirectory: {root}")
                    if dirs:
                        print("Subdirectories:", dirs)
                    if files:
                        print("Files:", files)
                raise Exception("No icon found in package")

            # Determine output format
            if output_path.lower().endswith('.png'):
                # Convert to PNG
                if not self.convert_icns_to_png(icon_path, output_path):
                    raise Exception("Failed to convert icon to PNG")
            else:
                # Copy original .icns file
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                shutil.copy2(icon_path, output_path)
                
            print(f"Icon successfully extracted to: {output_path}")

        finally:
            self.cleanup()

def main():
    if len(sys.argv) != 3:
        print("Usage: python icon_extractor.py <input_dmg_or_pkg> <output_icns_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    extractor = IconExtractor()
    try:
        extractor.extract_icon(input_path, output_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 