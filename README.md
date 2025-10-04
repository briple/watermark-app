# Watermark App

This is a simple watermark adding application designed for macOS. The application allows users to add watermarks to their images easily.

## Project Structure

```
watermark-app
├── src
│   ├── main.py          # Entry point of the application
│   └── component
│       ├── image_uploader.py 
│       ├── watermark_options.py  # GUI components for watermark options
│       ├── text_watermark_options.py  # GUI components for text 
│       ├── image_watermark_options.py  # GUI components for image 
│       ├── watermark_settings.py  # Settings management for watermarks
│       └── template_manager.py    # Manages watermark templates
├── assets
├── dist                  # Directory for built application
├── watermark_templates.json  # Predefined watermark templates
├── build_mac_app.py    # Script to build the macOS application
├── setup.py             # Packaging configuration
├── requirements.txt     # Project dependencies
├── README.md            # Project documentation
└── MANIFEST.in          # Additional files for distribution

```

## Installation

To install the application, clone the repository and run the following command:

```
pip install -r requirements.txt
```

## Usage

To run the application, execute the following command:

```
python src/main.py
```

This will open the application window where you can interact with the features.

To build the application, execute the following command:

```
python build_mac_app.py
```

This will build a runable application under ./dist/WatermarkApp.

To run it, execute the following command:

```
./dist.WatermarkApp

```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.