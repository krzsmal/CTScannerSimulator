# CT Scanner Simulator

## Overview

The CT Scanner Simulator provides an educational and research tool for understanding how medical CT scanners work. Users can upload medical images or regular images, generate sinograms using cone beam CT geometry, and reconstruct images using filtered or unfiltered backprojection. The application features real-time visualization of the scanning process with animated reconstruction capabilities.

This simulator implements the fundamental principles of computed tomography, including:
- Cone beam X-ray projection geometry
- Sinogram generation using ray tracing (Bresenham's algorithm)
- Filtered backprojection with ramp filter
- DICOM file handling for medical imaging workflows
- Quality assessment through RMSE (Root Mean Square Error) calculations

## Technologies

<img src="https://img.shields.io/badge/Streamlit-222629?logo=streamlit" height="30"> <img src="https://img.shields.io/badge/Numpy-013243?logo=numpy" height="30"> <img src="https://img.shields.io/badge/Matplotlib-11557C?logo=matplotlib" height="30"> <img src="https://img.shields.io/badge/scikit image-CE5C00" height="30"> <img src="https://img.shields.io/badge/DICOM-002957" height="30">

## Live Demo

You can try the CT Scanner Simulator online via Streamlit Cloud:  
https://ctscannersimulator-krzsmal.streamlit.app

> ⚠️ Note: This is hosted on the free Streamlit Cloud plan. If the app has not been used recently, the first launch may take a few seconds to start due to the server waking up.  
> ⚠️ Note: Some interactive animation features, such as step-by-step visualization of the sinogram generation and image reconstruction, may not work properly on the hosted version. These features are fully functional when running the application locally.

Sample input files are included in the repository under the `example_input/` folder:  
- **JPEG images** for testing regular images  
- **DICOM files (.dcm)** for testing medical imaging workflows

You can use these files to quickly try out the CT Scanner Simulator without needing your own data.

## Features

### Core Functionality
- **Multi-format Image Support**: Load JPEG, PNG, and DICOM files
- **Cone Beam CT Simulation**: Realistic X-ray source and detector geometry
- **Sinogram Generation**: Create projection data with configurable parameters
- **Image Reconstruction**: Backprojection with optional ramp filtering
- **Real-time Animation**: Step-by-step visualization of scanning and reconstruction
- **Quality Metrics**: RMSE calculation for reconstruction accuracy

### Interactive Controls
- **Adjustable CT Parameters**:
  - Angular step size (rotation increment)
  - Number of detectors in array
  - Detector span angle
  - Filtered vs. unfiltered backprojection
- **Animation Controls**: Play, pause, and step through reconstruction process
- **View Modes**: Switch between full result and iterative visualization

### DICOM Integration
- **Metadata Extraction**: Automatic parsing of patient information, study details
- **Custom File Naming**: Intelligent filename generation based on patient data
- **DICOM Export**: Save reconstructed images as valid DICOM files

## Screenshots

![Screenshot1](https://github.com/user-attachments/assets/10df30d6-1f42-440f-b9d2-c597e39043f0)

![Screenshot2](https://github.com/user-attachments/assets/e267b503-aadb-4a58-9726-2a590ca5eb65)

![Screenshot3](https://github.com/user-attachments/assets/0c2a3cb0-0ca5-4f8f-a8bc-bcb1314d3c33)

## Project Structure

```
CTScannerSimulator/
├── main.py                   # Application entry point and main orchestration
├── config/
│   └── constants.py          # Configuration constants and session keys
├── core/                     # CT scanning simulation logic
│   ├── __init__.py
│   ├── ct_scanner.py         # Main CT scanner implementation
│   ├── image_processing.py   # Image normalization and filtering
│   └── geometry.py           # CT geometry calculations
├── dicom/                    # Medical imaging file handling
│   ├── __init__.py
│   ├── dicom_handler.py      # DICOM file I/O operations
│   └── metadata.py           # Metadata extraction utilities
├── ui/                       # User interface components
│   ├── __init__.py
│   ├── components.py         # Reusable UI widgets
│   ├── sidebar.py            # Parameter control panel
│   └── sections.py           # Main application sections
└── utils/                    # Support utilities
    ├── __init__.py
    ├── session_state.py      # Streamlit session management
    └── file_utils.py         # File validation and naming
```

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/ct-scanner-simulator.git
cd ct-scanner-simulator
```

2. **Create virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Application

1. **Launch the simulator**:
```bash
streamlit run main.py
```

2. **Open in browser**: The application automatically opens at `http://localhost:8501`

## License

This project is licensed under the **[GNU General Public License v3.0](LICENSE)**.
