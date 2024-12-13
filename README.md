# 🎨 Icon Extractor

A Python utility to extract high-resolution icons from macOS PKG installers and DMG files. The script can process individual files or entire directories, converting icons to PNG format while maintaining the best possible quality. ✨

## ✅ Features

- 📦 Extract icons from both PKG installers and DMG files
- 🪆 Support for nested PKG files (like Zoom installer)
- 🗂️ Batch processing of entire directories
- 🖼️ Automatic conversion to PNG with optimal resolution
- 📝 Detailed progress and error reporting
- 🔍 Maintains highest available resolution (typically 512x512 or 1024x1024)
- 📐 Option to resize icons to specific dimensions while maintaining aspect ratio

## 🛠️ Requirements

- 🍎 macOS (uses system tools like `xar`, `sips`, and `iconutil`)
- 🐍 Python 3.6+
- 📚 Optional: Pillow (PIL) library for advanced image processing

## 📥 Installation

1. Clone the repository:
```bash
git clone https://github.com/roberto2lini/icon-extractor
cd icon-extractor
```

2. Make the script executable:
```bash
chmod +x icon_extractor.py
```

3. Install optional dependencies:
```bash
pip install Pillow
```

## 🚀 Usage

### 🎯 Extract icon from a single file

```
# 🖼️ Extract to PNG (recommended)
python3 icon_extractor.py input.pkg output.png

# 🔄 Extract original .icns file
python3 icon_extractor.py input.pkg output.icns

# 💿 Extract from DMG
python3 icon_extractor.py input.dmg output.png
```

### 📂 Process an entire directory

```bash
python3 icon_extractor.py --dir input_directory output_directory
```

This will:
- 🔍 Find all PKG and DMG files in the input directory (including subdirectories)
- 📤 Extract icons and save them as PNGs in the output directory
- 📊 Provide a summary of successful and failed extractions

## 💡 Examples

### 🎥 Extract Zoom icon
```bash
python3 icon_extractor.py zoomusInstallerFull.pkg zoom_icon.png
```

### 📚 Process multiple installers
```bash
python3 icon_extractor.py --dir ~/Downloads/Installers ~/Desktop/Icons
```

### 📝 Sample Output
```
Processing: /Downloads/Installers/zoomusInstallerFull.pkg
Created temporary directory: /tmp/pkg_extract_20241213_164740
Attempting to extract PKG using xar: zoomusInstallerFull.pkg
Found nested PKG directory: /tmp/pkg_extract_20241213_164740/zoomus.pkg
Converting .icns to .png using sips...
Icon successfully extracted to: /Desktop/Icons/zoom_icon.png

Processing Summary:
✅ Successfully processed: 1 files
❌ Failed to process: 0 files

Successfully processed files:
  /Downloads/Installers/zoomusInstallerFull.pkg -> /Desktop/Icons/zoom_icon.png
```

## 📄 Supported File Types

- 📦 PKG installers (including nested PKG files)
- 💿 DMG disk images
- 🎨 Outputs to either PNG (with optional resizing) or original ICNS format

## ⚠️ Error Handling

The script provides detailed error messages and creates a summary when processing multiple files. Failed extractions don't stop the batch process, and a final report shows both successful and failed operations.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Here are some ways you can contribute:
- 🐛 Report bugs
- ✨ Request features
- 📝 Improve documentation
- 🔧 Submit pull requests

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤔 Common Issues

### No icon found in package
- Ensure the package contains an application bundle
- Check if the package is properly formatted
- Verify the package is not corrupted

### Conversion failed
- Ensure `sips` and `iconutil` are available on your system
- Check if you have proper permissions
- Try installing Pillow for alternative conversion method