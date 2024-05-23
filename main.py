import argparse
from ebooklib import epub
from tqdm import tqdm
import asyncio
import json
import os

from utils import get_chapters, get_save_path, generate, merge_audio_files

def parse_arguments():
    parser = argparse.ArgumentParser(description="Script to convert EPUB chapters to audio files.")

    parser.add_argument('--output-dir', type=str, default="./audiobook/", help='Output directory for audio files')
    parser.add_argument('--path', type=str, default="./example.epub", help='Path to the EPUB file')
    parser.add_argument('--voice', type=str, default="en-US-EricNeural", help='Voice to use in Text-to-Speech')
    parser.add_argument('--retry-attempts', type=int, default=10, help='Number of times to retry on failure')
    parser.add_argument('--max-concurrent-tasks', type=int, default=5, help='Limit the number of concurrent tasks')
    parser.add_argument('--dry-run', default=False, action='store_true', help='If set, will save the text to be spoken as a json file instead of actually speaking it')
    parser.add_argument('--skip-chapters', type=int, default=0, help='Number of chapters to skip')
    parser.add_argument('--skip-paragraphs', type=int, default=0, help='Number of paragraphs to skip')
    parser.add_argument('--start-chapter', type=int, default=0, help='Chapter number to start from')
    parser.add_argument('--end-chapter', type=int, default=0, help='Chapter number to end at')
    parser.add_argument('--clean-text', default=True, action='store_true', help='If set, will clean the text')
    parser.add_argument('--remove-text-list', type=str, nargs='+', help='List of text strings to remove', default=[
        "ReadNovelFull.me?",
        "ReadNovelFull.me",
    ])
    
    return parser.parse_args()

async def main(args):
    
    os.makedirs(args.output_dir, exist_ok=True)

    book = epub.read_epub(args.path)
    
    # save the chapters to json file
    chapters = get_chapters(
        book, 
        args.clean_text,
        args.skip_chapters,
        args.start_chapter,
        args.end_chapter,
        args.skip_paragraphs, 
        args.remove_text_list
    )
    

    with open('chapters.json', 'w') as f:
        json.dump(chapters, f)

    
    if not args.dry_run:
        print("Generating audio files...")
        print("This may take a while depending on the number of chapters and the length of the text.")
        for index, chapter in tqdm(enumerate(chapters)):
            
            chapter_index = index + args.start_chapter + 1
            # Limit the number of concurrent downloads to MAX_CONCURRENT_TASKS
            semaphore = asyncio.Semaphore(args.max_concurrent_tasks) 

            tasks = []
            output_files = []
            for i, chunk in enumerate(chapter['paragraphs']):
                output_file = get_save_path(chapter_index, i, args.output_dir)
                output_files.append(output_file)
                tasks.append(generate(semaphore, chunk, output_file, args.voice, args.retry_attempts))

            await asyncio.gather(*tasks)

            merge_audio_files(chapter_index, output_files, f"{args.output_dir}chapter_{chapter_index:04d}_merged.mp3")

            chapter_index += 1

    else:
        print("Dry run enabled. Not saving audio files.")
        print("Saving chapters to json file...")
        with open('chapters.json', 'w') as f:
            json.dump(chapters, f)
    

if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(main(args))