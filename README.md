# bili-video-converter

A tool for converting Bilibili App downloaded videos to MP4 format.

处理Bilibili下载的.m4s文件，合并为MP4文件，可单独导出音频文件。

## Features

- Convert to multiple MP4.
- Batch processing support
- High-quality output files.

## Installation

```bash
pip install bili-video-converter
```

## Usage

```bash
bili-converter [-h] [--audio] [--audio-only] [--audio_directory AUDIO_DIRECTORY] [base_directory] [output_directory]
```

## Requirement

- Python 3.8+
- FFmpeg
- argparse>=1.4.0

## License

GPL v3
