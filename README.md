### VocalEdgeBook

# EPUB to Audio Converter

This project is a Python script to convert the chapters of an EPUB book into audio files using edge-tts Text-to-Speech (TTS) technology. The script supports concurrency, custom voices, and can clean the text before synthesizing it into speech.

## Features

- Converts chapters from an EPUB file to MP3 audio files.
- Choose from a variety of voices (default is "en-US-EricNeural").
- Supports retry attempts for the TTS API.
- Allows skipping chapters and paragraphs.
- Option to clean the text by removing specified strings.
- Save the text to a JSON file instead of generating audio (dry-run mode).
- Merge generated audio files into a single audio file per chapter.

## Dependencies

- `edge-tts` (Text-to-Speech API by Microsoft Cognitive Services)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/epub-to-audio.git
   cd epub-to-audio
   ```

2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

3. Ensure that you have the `ffmpeg` library installed, which is required by `pydub`:
   - On Ubuntu:
     ```sh
     sudo apt-get install ffmpeg
     ```
   - On MacOS:
     ```sh
     brew install ffmpeg
     ```
   - On Windows, download the FFmpeg executable from [here](https://ffmpeg.org/download.html) and follow the installation instructions.

## Usage

```sh
python main.py --output-dir OUTPUT_DIR --path EPUB_PATH [options]
```

### Options

- `--output-dir`: Output directory for audio files (default: `./audiobook/`)
- `--path`: Path to the EPUB file (default: `./book.epub`)
- `--voice`: Voice to use in Text-to-Speech (default: `en-US-EricNeural`) [Voices List](https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462)
- `--retry-attempts`: Number of times to retry on failure (default: 10)
- `--max-concurrent-tasks`: Limit the number of concurrent tasks (default: 5)
- `--dry-run`: Save the text to be spoken as a JSON file instead of actually speaking it
- `--skip-chapters`: Number of chapters to skip (default: 0)
- `--skip-paragraphs`: Number of paragraphs to skip (default: 0)
- `--start-chapter`: Chapter number to start from (default: 0)
- `--end-chapter`: Chapter number to end at (default: 0)
- `--clean-text`: Clean the text before generating audio (default: True)
- `--remove-text-list`: List of text strings to remove

### Example

Convert chapters from an EPUB file and save the audio files:

```sh
python main.py --output-dir ./output/ --path ./book.epub --voice en-US-EricNeural
```

Dry run mode (save chapters as JSON file instead of generating audio):

```sh
python main.py --output-dir ./output/ --path ./book.epub --dry-run
```

## Contributing

Feel free to submit issues, fork the repository, and send pull requests with updates. Any contributions are highly appreciated!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

If you encounter any problems or have any questions, feel free to open an issue or reach out to me directly. Happy audiobook making!
