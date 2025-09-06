# Kokoro TTS Installation Guide

This guide explains how to install Kokoro TTS for the Walls AI Interface voice mode functionality.

## Why Separate Installation?

Kokoro TTS is installed separately from the main Walls application for several important reasons:

1. **Optional Dependency**: Voice mode is an optional feature - users who don't need TTS shouldn't be forced to install additional packages <mcreference link="https://github.com/hexgrad/kokoro" index="0">0</mcreference>
2. **Clean Distribution**: Keeps the main Walls codebase focused and lightweight for GitHub distribution
3. **Licensing**: Kokoro uses Apache licensing and can be deployed anywhere, but it's better to let users choose <mcreference link="https://github.com/hexgrad/kokoro" index="0">0</mcreference>
4. **Independent Updates**: Kokoro can be updated independently via pip without affecting the main application
5. **System-wide Availability**: Installing via pip makes Kokoro available system-wide for other projects

## Installation Methods

Choose one of the following methods to install Kokoro TTS:

### Method 1: Python Script (Recommended)

```bash
python install_kokoro.py
```

### Method 2: Bash Script (Linux/macOS)

```bash
./install_kokoro.sh
```

### Method 3: Windows Batch Script

```cmd
install_kokoro.bat
```

### Method 4: Manual Installation

```bash
pip install kokoro>=0.9.4 soundfile
```

## Installation Details

### Installation Method
- **Package Manager**: Installed via pip from PyPI <mcreference link="https://github.com/hexgrad/kokoro" index="0">0</mcreference>
- **System-wide**: Available to all Python environments
- **Configuration**: `ai_interface/voice_mode/kokoro_config.py` (auto-generated)
- **Dependencies**: Automatically handles torch, numpy, and other ML dependencies

### Files Created

1. **Kokoro TTS Package**: Installed via pip package manager
2. **Configuration File**: `ai_interface/voice_mode/kokoro_config.py`
3. **Service Integration**: Updates to `kokoro_service.py` for pip installation support

### Dependencies Installed

The installer will install these Python packages:
- `kokoro>=0.9.4` - Main Kokoro TTS package <mcreference link="https://github.com/hexgrad/kokoro" index="0">0</mcreference>
- `soundfile` - Audio file I/O
- `torch` - PyTorch for neural network inference (auto-installed with kokoro)
- `numpy` - Numerical computing (auto-installed with kokoro)
- `misaki` - G2P library used by Kokoro <mcreference link="https://github.com/hexgrad/kokoro" index="0">0</mcreference>

## Verification

After installation, verify that Kokoro TTS is working:

### Automatic Verification

The installer automatically runs a test to verify the installation. Look for:

```
✓ Kokoro installation verified!
✓ KPipeline can be initialized successfully
```

### Manual Verification

You can manually test the installation:

```python
# Test script
try:
    import kokoro
    from kokoro import KPipeline
    
    # Test basic functionality
    pipeline = KPipeline(lang_code='a')
    print("✓ Kokoro TTS is available and working!")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("Please run: pip install kokoro>=0.9.4")
except Exception as e:
    print(f"✗ Initialization failed: {e}")
```

### Installation Summary

After successful installation, the installer will:

1. Test that Kokoro can be imported successfully
2. Create a configuration file with the installation path
3. Update the Kokoro service to use the pip installation
4. Provide usage instructions

## Usage in Walls

Once installed, Kokoro TTS will be automatically available in the Walls voice mode:

1. Launch the Walls AI Interface
2. Double-click the AI loader to enter voice mode
3. Speak your message
4. The AI response will be synthesized using Kokoro TTS

### Voice Settings

Kokoro supports multiple voices and languages <mcreference link="https://github.com/hexgrad/kokoro" index="0">0</mcreference>:
- **American English** (`a`): `af_heart`, `af_sky`, `af_bella`, `af_sarah`
- **British English** (`b`): `bf_heart`, `bf_sky`, `bf_bella`, `bf_sarah`
- **Spanish** (`e`): `ef_heart`, `ef_sky`, `ef_bella`, `ef_sarah`
- **French** (`f`): `ff_heart`, `ff_sky`, `ff_bella`, `ff_sarah`
- **Italian** (`i`): `if_heart`, `if_sky`, `if_bella`, `if_sarah`
- **Portuguese** (`p`): `pf_heart`, `pf_sky`, `pf_bella`, `pf_sarah`

### Configuration

The `kokoro_config.py` file contains:
```python
# Kokoro is installed via pip, no additional path configuration needed
KOKORO_INSTALLED_VIA_PIP = True

try:
    import kokoro
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False
    print("Warning: Kokoro not found. Please run: pip install kokoro>=0.9.4")
```

## Troubleshooting

### Common Issues

#### 1. Pip Installation Failed
```
ERROR: Failed to install Kokoro via pip
```
**Solution**: 
- Check internet connection
- Update pip: `python -m pip install --upgrade pip`
- Try manual installation: `pip install kokoro>=0.9.4`
- Check Python version (3.8+ recommended)

#### 2. Import Error
```
ModuleNotFoundError: No module named 'kokoro'
```
**Solution**:
- Verify installation: `pip show kokoro`
- Reinstall: `pip install --upgrade kokoro>=0.9.4`
- Check virtual environment activation
- Restart Walls application

#### 3. KPipeline Initialization Failed
```
ERROR: Installation test failed
```
**Solution**:
- Install additional dependencies: `pip install soundfile`
- Check system audio libraries (see below)
- Try different language code: `KPipeline(lang_code='a')`
- Update torch: `pip install --upgrade torch`

#### 4. Audio Dependencies Missing
```
OSError: cannot load library 'libsndfile.so'
```
**Solution**:
- **Ubuntu/Debian**: `sudo apt-get install libsndfile1`
- **macOS**: `brew install libsndfile`
- **Windows**: Usually included with soundfile package

### Installation Issues

**Python not found:**
```
Error: Python is not installed. Please install Python first.
```
Solution: Install Python 3.7+ from [python.org](https://python.org/)

**Permission denied:**
```
Permission denied: ./install_kokoro.sh
```
Solution: Make the script executable with `chmod +x install_kokoro.sh`

### Runtime Issues

**Kokoro not found in voice mode:**
1. Check that `kokoro_config.py` exists in `ai_interface/voice_mode/`
2. Verify Kokoro is installed: `pip show kokoro`
3. Re-run the installer if necessary

**Import errors:**
1. Ensure all dependencies are installed: `pip install kokoro>=0.9.4 soundfile`
2. Check that Kokoro package is accessible: `python -c "import kokoro"`
3. Verify Python environment is correct

### Model Issues

**No voice output:**
1. Check if KPipeline initializes properly
2. Verify audio output system is working
3. Refer to the Kokoro TTS documentation for voice configuration

## Uninstallation

To remove Kokoro TTS:

### 1. Uninstall Kokoro Package
```bash
pip uninstall kokoro
```

### 2. Remove Configuration File
```bash
rm ai_interface/voice_mode/kokoro_config.py
```

### 3. Uninstall Additional Dependencies (Optional)
```bash
pip uninstall soundfile
```

**Note**: Core dependencies like torch and numpy may be used by other applications, so only uninstall them if you're sure they're not needed elsewhere.

## Development Notes

### For Contributors

If you're contributing to the Walls project:

1. **Don't commit Kokoro files**: The `.gitignore` should exclude any Kokoro-related files
2. **Test without Kokoro**: Ensure voice mode gracefully handles missing Kokoro installation
3. **Update installers**: If you modify the Kokoro integration, update the installation scripts

### For Distributors

When distributing Walls:

1. **Include installation scripts**: Always include the three installer files
2. **Document requirements**: Make sure users know about the separate Kokoro installation
3. **Test installation**: Verify the installers work on your target platforms

## Security Considerations

1. **PyPI Package**: Kokoro is installed from the official PyPI repository
2. **System-wide Installation**: Kokoro is installed system-wide via pip
3. **No Elevated Privileges**: Installation doesn't require admin/root access
4. **Standard Package Manager**: Uses Python's standard pip package manager

## License Information

- **Walls Project**: Licensed under the project's main license
- **Kokoro TTS**: Subject to its own license terms (check the Kokoro repository)
- **Installation Scripts**: Part of the Walls project, same license as main project

## Support

For installation issues:

1. Check this troubleshooting guide first
2. Verify your system meets the requirements
3. Try the Python installer if other methods fail
4. Check the Kokoro TTS repository for model-specific issues

## Future Improvements

Planned enhancements for the installation system:

1. **Model Management**: ✓ Automatic model downloading (implemented with pip installation)
2. **Version Pinning**: ✓ Lock to specific Kokoro versions (implemented: >=0.9.4)
3. **Update Mechanism**: ✓ Easy updates via pip (implemented)
4. **Alternative TTS**: Support for other TTS engines
5. **GUI Installer**: Graphical installation interface