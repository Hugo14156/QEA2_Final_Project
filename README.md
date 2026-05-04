# QEA2 Final Project

Fourier Series Sketcher is an interactive drawing app built with pygame-ce.
You can draw a shape, convert it into Fourier coefficients, and watch epicycle
animation reconstruct your drawing.

Pre-packaged releases will be published on GitHub so you can run the app
without setting up Python.

## Features

- Freehand and line drawing modes
- Eraser mode
- Save and load drawing image and point data
- Convert drawing to Fourier coefficients
- Animated epicycle rendering with adjustable wave count and speed
- Trace path display during animation
- Build and release packaging scripts for executable distribution

## Run As A Python Repository

### Prerequisites

- Python 3.13+
- pip

### Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Run the app.

	python -m venv .venv
	.venv\Scripts\activate
	pip install -r requirements.txt
	python main.py

If you are on macOS or Linux, activate with:

	source .venv/bin/activate

## Run As An Executable

Download the latest pre-packaged release from the GitHub Releases page.

- Windows: run the .exe
- macOS: run the packaged app or binary from the release archive
- Linux: run the packaged binary from the release archive

If your OS warns about unknown publishers, confirm the prompt and continue.

## How To Use The App

### Toolbar Controls

- Save: saves current canvas image and sampled point metadata
- Load: loads saved canvas image and point metadata
- Line Draw / Free Draw: toggles drawing mode
- Clear: clears the canvas and resets animation state
- Eraser On / Eraser Off: toggles eraser mode
- Convert: computes Fourier coefficients and starts animation
- Play Anim / Pause Anim / Resume Anim: controls animation playback
- Quit: exits the app

### Sliders

- Point Resolution: percentage of drawn points kept for conversion
- Wave Count: number of Fourier components shown in animation
- Anim Speed: animation playback speed

### Typical Workflow

1. Draw a shape on the canvas.
2. Adjust Point Resolution and Wave Count.
3. Click Convert.
4. Watch epicycles animate and trace the reconstruction.
5. Use Play Anim and speed slider to inspect behavior.

## Repository Outline

	.
	├── app/
	│   ├── app.py
	│   ├── control/
	│   │   └── controller.py
	│   ├── model/
	│   │   ├── app_model.py
	│   │   └── test_app_model.py
	│   └── view/
	│       ├── button.py
	│       ├── slider.py
	│       └── view.py
	├── file_types/
	│   └── file_types.py
	├── saved_series/
	│   ├── converted_points.json
	│   └── drawing_points.json
	├── scripts/
	│   ├── build_executable.py
	│   └── package_release.py
	├── tests/
	├── FOURIER_MATH.md
	├── main.py
	├── requirements.txt
	└── README.md

## Packaging An Executable

Use the build script to create a platform-specific executable.

	python scripts/build_executable.py

Helpful options:

	python scripts/build_executable.py --name QEA2_Fourier_Sketcher --onefile
	python scripts/build_executable.py --onedir
	python scripts/build_executable.py --console
	python scripts/build_executable.py --clean

Important: native executable builds are platform-specific.
To create builds for all platforms, run the script on each target OS.

## Packaging A Release Archive

Use the release packaging script to build and create a distributable archive,
plus checksum and manifest metadata.

	python scripts/package_release.py --version v1.0.0

Package existing dist output without rebuilding:

	python scripts/package_release.py --skip-build --version v1.0.0

Other useful options:

	python scripts/package_release.py --onedir --version v1.0.0
	python scripts/package_release.py --format zip --version v1.0.0
	python scripts/package_release.py --no-docs --version v1.0.0

Release artifacts are written to the releases folder by default.

## Notes

- Fourier math details are documented in FOURIER_MATH.md.
- Dependencies are listed in requirements.txt.
- Pre-packaged releases will be available on GitHub Releases.
