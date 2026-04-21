# C++ GUI for Web Scraper & Decryptor

A Qt-based graphical user interface for the web scraper and decryption tool.

## Features

- User-friendly GUI for configuring scraper parameters
- Input fields for:
  - Start URL
  - Maximum pages to scrape
  - Maximum depth
  - Number of workers
  - Timeout settings
- Real-time status updates
- Formatted display of scraping results
- JSON output with decrypted messages

## Prerequisites

- C++ compiler with C++17 support (GCC 7+, Clang 5+, MSVC 2017+)
- CMake 3.16 or higher
- Qt 5.15+ or Qt 6.x
- Python 3.x (for running the backend scraper)

## Building on Linux

### Install Qt

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install qt6-base-dev qt6-tools-dev cmake build-essential
# Or for Qt5:
# sudo apt-get install qtbase5-dev qt5-qmake cmake build-essential
```

**Fedora:**
```bash
sudo dnf install qt6-qtbase-devel cmake gcc-c++
# Or for Qt5:
# sudo dnf install qt5-qtbase-devel cmake gcc-c++
```

### Build the Application

```bash
cd gui
mkdir build
cd build
cmake ..
make
```

The executable `WebScraperGUI` will be created in the repository root directory.

## Building on Windows

### Install Qt

1. Download and install Qt from https://www.qt.io/download
2. Install CMake from https://cmake.org/download/
3. Install Visual Studio 2019 or later with C++ support

### Build the Application

Using Qt Creator:
1. Open Qt Creator
2. Open the `gui/CMakeLists.txt` file
3. Configure the project
4. Build the project

Or using command line:
```cmd
cd gui
mkdir build
cd build
cmake -G "Visual Studio 16 2019" ..
cmake --build . --config Release
```

## Building on macOS

### Install Qt

```bash
brew install qt6 cmake
# Or for Qt5:
# brew install qt@5 cmake
```

### Build the Application

```bash
cd gui
mkdir build
cd build
cmake ..
make
```

## Running the Application

After building, run the executable from the repository root directory:

```bash
# Linux/macOS
./WebScraperGUI

# Windows
WebScraperGUI.exe
```

**Important:** The GUI must be run from the repository root directory so it can find the `scraper.py` file.

## Usage

1. Enter the starting URL in the "Start URL" field
2. Configure the scraping parameters:
   - **Max Pages:** Maximum number of pages to scrape (default: 30)
   - **Max Depth:** How deep to follow links (default: 2)
   - **Workers:** Number of concurrent workers (default: 8)
   - **Timeout:** Request timeout in seconds (default: 10)
3. Click "Start Scraping"
4. Monitor the status in the status area
5. View results in the results display area

## How It Works

The C++ GUI application:
1. Provides a user-friendly interface for configuration
2. Launches the Python scraper as a subprocess
3. Captures and displays the JSON output
4. Parses and formats the results for easy viewing

The backend Python scraper:
- Concurrently scrapes pages on the same host
- Extracts candidate encoded strings from HTML/script content
- Automatically attempts layered decryption/decoding (Base64, URL encoding, hex, ROT13)
- Returns structured JSON with decrypted findings per page

## Troubleshooting

### "Failed to start Python"
- Ensure Python is installed and available in your PATH
- Try running `python --version` in terminal to verify

### "Could not find Qt"
- Make sure Qt is properly installed
- Set the `CMAKE_PREFIX_PATH` environment variable to your Qt installation path:
  ```bash
  export CMAKE_PREFIX_PATH=/path/to/Qt/6.x.x/gcc_64
  ```

### Build errors
- Ensure you have a C++17 compatible compiler
- Check that CMake version is 3.16 or higher
- Verify Qt installation is complete

## License

Same as the main project.
