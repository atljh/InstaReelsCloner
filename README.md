**InstaReelsCloner** is a Python script for automatic downloading, processing, and posting Reels videos to Instagram. The script helps bloggers, marketers, and arbitrage specialists effectively manage video content by adding unique watermarks, filters, and scheduling posts.

## Features

- **Automatic Reels Download**: Download Reels from a specified Instagram account.
- **Video Uniqueization**: Apply watermarks, filters, and modify parameters (speed, color correction, etc.) to make the video unique.
- **Scheduled Posting**: Automatically post videos to Instagram at a specified time.
- **Multiple Instagram Accounts Support**: Manage multiple accounts for uploading content.
- **Content Optimization**: Ensure the content is optimized to avoid blocks and restrictions.
- **Flexible Settings**: Customize processing parameters and posting schedules.

## How It Works

1. The script downloads Reels from a specified Instagram account.
2. The video is processed by applying watermarks, filters, and speed adjustments.
3. The finished video is automatically posted to Instagram according to the set schedule.

This tool is ideal for bloggers, marketers, and arbitrage specialists who want to automate their video content management.

## Requirements

- **Python 3.11** or higher is required. Please make sure you have the correct version of Python installed on your system.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/atljh/InstaReelsCloner.git
    ```

2. **Navigate to the project folder**:
    ```bash
    cd InstaReelsCloner
    ```

3. **Configuration**:
    - Copy `config-sample.yaml` to `config.yaml` and adjust the settings:
      ```bash
      cp config-sample.yaml config.yaml
      ```

    - Edit `config.yaml` with your Instagram account details and scheduling preferences.

4. **Installation Scripts**:
    For Windows: You can use the provided install.bat script to install the necessary dependencies and set up the environment:
    ```bash
    isntall.bat
    ```
    For Linux: You can use the provided install.sh script to install the necessary dependencies and set up the environment:
    ```bash
    chmod +x install.sh
    ./install.sh
    ```

## File structure
    ```
        InstaReelsCloner/
        │
        ├── .flake8                 # Flake8 configuration file
        ├── .gitignore              # Git ignore configuration
        ├── README.md               # Project documentation
        ├── config-sample.yaml      # Sample configuration file
        ├── config.yaml             # Configuration file (to be customized)
        ├── image.png               # Image used for watermark
        ├── install.bat             # Windows installation script
        ├── install.sh              # Linux installation script
        ├── main.py                 # Main script to run the application
        ├── requirements.txt        # List of Python dependencies
        ├── test1/                  # Test videos
        │   ├── video_4.mp4
        │   └── video_5.mp4
        ├── __pycache__/            # Compiled Python files
        │   ├── config.cpython-311.pyc
        │   └── console.cpython-311.pyc
        ├── downloads/              # Directory for downloaded videos
        │   ├── .DS_Store
        │   └── unique_videos/      # Processed videos
        │       ├── video_1.mp4
        │       └── video_2.mp4
        ├── src/                    # Source code
        │   ├── __init__.py
        │   ├── config_loader.py    # Configuration loader
        │   ├── cloning/            # Video cloning and processing
        │   │   └── cloner.py
        │   ├── tools/              # Utility functions
        │   │   └── console.py
        │   ├── posting/            # Posting videos to Instagram
        │   │   └── poster.py
        │   ├── managers/           # Core logic for managing video content
        │   │   ├── __init__.py
        │   │   ├── auth.py
        │   │   ├── download.py
        │   │   ├── post.py
        │   │   ├── scheduler.py
        │   │   ├── uniqueize.py
        │   │   └── video_manager.py
        └── test1/                  # Test videos directory
            ├── video_4.mp4
            └── video_5.mp4
    ```


## Usage

1. **Run the script**:
    ```bash
    python main.py
    ```

2. The script will download, process, and post videos according to the configuration in `config.yaml`.

## Contributing

Feel free to fork the repository, create issues, and submit pull requests for any improvements or fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
