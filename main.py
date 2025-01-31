import argparse
import os
import json
import logging
from utils.image import remove_image_metadata
from utils.pdf import remove_pdf_metadata
from utils.audio import remove_audio_metadata
from utils.video import remove_video_metadata
from utils.documents import remove_document_metadata

def setup_logging():
    logging.basicConfig(
        filename="metadata_cleaner.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

def load_metadata_template(template_path):
    if template_path and os.path.exists(template_path):
        with open(template_path, "r") as file:
            return json.load(file)
    return {}

def process_file(file_path, output_path, metadata_template):
    ext = file_path.lower().split('.')[-1]
    
    if ext in ["jpg", "jpeg", "png"]:
        remove_image_metadata(file_path, output_path)
    elif ext == "pdf":
        remove_pdf_metadata(file_path, output_path)
    elif ext in ["mp3", "flac"]:
        remove_audio_metadata(file_path, output_path)
    elif ext in ["mp4", "mkv"]:
        remove_video_metadata(file_path, output_path)
    elif ext in ["docx"]:
        remove_document_metadata(file_path, output_path)
    else:
        logging.warning(f"Unsupported file format: {file_path}")
        print(f"Unsupported file format: {file_path}")
        return
    
    logging.info(f"Processed: {file_path} -> {output_path}")
    print(f"Metadata cleaned: {file_path} -> {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Metadata Cleaner CLI Tool")
    parser.add_argument("input", help="Path to the input file or directory")
    parser.add_argument("output", help="Path to the output file or directory")
    parser.add_argument("-t", "--template", help="Path to metadata template JSON file", default=None)
    
    args = parser.parse_args()
    
    setup_logging()
    metadata_template = load_metadata_template(args.template)
    
    if os.path.isdir(args.input):
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        for file_name in os.listdir(args.input):
            file_path = os.path.join(args.input, file_name)
            output_path = os.path.join(args.output, file_name)
            if os.path.isfile(file_path):
                process_file(file_path, output_path, metadata_template)
    else:
        process_file(args.input, args.output, metadata_template)
    
if __name__ == "__main__":
    main()
