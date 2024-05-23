import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import asyncio
import edge_tts
import os
from pydub import AudioSegment

def clean_paragraph(paragraph):
   
    # # Remove dot before punctuation
    cleaned_paragraph = re.sub(r'\b(?:\w\.)+\w\b', '', paragraph)

    cleaned_paragraph = cleaned_paragraph.replace('\"', "").replace('\n', "")

    # check if the paragraph has any text left 
    if (bool(re.search(r'[a-zA-Z0-9]', cleaned_paragraph))):
        return cleaned_paragraph
    else:
        return ''
    
def get_chapters(book, CLEAN_TEXT=False, SKIP_CHAPTERS=0, START_CHAPTER=0, END_CHAPTER=0, SKIP_PARAGRAPHS=0, REMOVE_TEXT_LIST=[]):
    chapters = []
    for index, item in tqdm(enumerate(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))):
        if(END_CHAPTER > 0 and index >= END_CHAPTER):
            break
        if(index < SKIP_CHAPTERS or index < START_CHAPTER):
            continue

        content = item.get_content()
        soup = BeautifulSoup(content, 'html.parser')
        
        
        chapter_content = soup.get_text()
        chapter_content = chapter_content.split('\n')
        chapter_content = [p for p in chapter_content if p.strip() != '']

        paragraphs = []
        for i, p in enumerate(chapter_content):
            if(i < SKIP_PARAGRAPHS):
                continue
            par = ''
            if p.strip() != '':
                # remove all the tags, dots and newlines
                if CLEAN_TEXT:
                    clean_p = p
                    for r in REMOVE_TEXT_LIST:
                        clean_p = clean_p.replace(r, '')
                    par = clean_paragraph(clean_p)
                else:
                    par = paragraphs.append(p)
            if par != '':
                paragraphs.append(par)

        if(len(paragraphs) == 0):
            continue
        
        chapters.append({ 'paragraphs': paragraphs })
    return chapters

def get_save_path(chapter_index, chunk_index, OUTPUT_DIR):
    chunk_index_padding = str(chunk_index+1).zfill(4)
    chapter_index_padding = str(chapter_index).zfill(4)
    return f"{OUTPUT_DIR}chap_{chapter_index_padding}_part_{chunk_index_padding}.mp3"

async def generate(semaphore, TEXT, output_file, VOICE, RETRY_ATTEMPTS, attempt=1) -> None:
    """Main function to convert text to speech and save it as an MP3 file"""

    if os.path.exists(output_file):
        return
        
    async with semaphore:
        try:
            communicate = edge_tts.Communicate(TEXT, VOICE)
            await communicate.save(output_file)
        except asyncio.exceptions.TimeoutError:
            if attempt <= RETRY_ATTEMPTS:
                print(f"TimeoutError: Attempt {attempt} for {output_file}. Retrying...")
                await amain(semaphore, TEXT, output_file, VOICE, RETRY_ATTEMPTS, attempt + 1)
            else:
                print(f"Failed after {RETRY_ATTEMPTS} attempts: {output_file}")
        except Exception as e:
            print(f"An error occurred for {output_file}: {e}")

def merge_audio_files(chapter_num, audio_files, output_filename, DELETE_FILES=True):

    # CHECK IF output file already exists
    if os.path.exists(output_filename):
        return

    """Merge all audio files of a chapter into a single file."""
    if not audio_files or len(audio_files) == 0:
        print(f"No audio files found for chapter {chapter_num:03d}")
        return

    merged = AudioSegment.empty()
    for file in audio_files:
        audio_segment = AudioSegment.from_mp3(file)
        merged += audio_segment

    merged.export(output_filename, format="mp3")

    if DELETE_FILES:
        for file in audio_files:
            os.remove(file)