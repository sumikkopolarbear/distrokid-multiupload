import os
import json
from datetime import date
import argparse


def generate_metadata_file(path):
    if "metadata.json" in os.listdir(path):
        raise FileExistsError(f"An album metadata file already exists for {path}")
    
    album_metadata = {}
    album_metadata["album_name"] = os.path.basename(path)
    album_metadata["band_name"] = ""
    album_metadata["release_date"] = str(date.today())
    album_metadata["record_label"] = ""
    album_metadata["genre"] = ""
    
    #Find first picture in directory to use as album cover
    album_cover_path = ""
    for images in os.listdir(path):
        # check if the image ends with png or jpg or jpeg
        if (images.endswith(".png") or images.endswith(".jpg") or images.endswith(".jpeg")):
            album_cover_path = images
    album_metadata["album_cover_file_name"] = album_cover_path
    
    valid_file_types = ["wav", "mp3", "m4a", "flac", "aiff", "wma"]
    songs_data = []
    for file in os.listdir(path):
        if file.endswith(tuple(valid_file_types)):
            song_data = {}
            song_data["title"] = os.path.splitext(file)[0]
            song_data["file_name"] = file
            
            writer_data = {}
            writer_data["contribution"] = "ml"
            writer_data["first_name"] = ""
            writer_data["middle_name"] = ""
            writer_data["last_name"] = ""
            song_data["writers"] = [writer_data]
            
            songs_data.append(song_data)
    album_metadata["songs"] = songs_data
    
    with open(path + "//" + "metadata.json", "w", encoding="utf-8") as file:
        json.dump(album_metadata, file, indent=2)
    
    print("Created metadata file successfully!")

if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="Creates a template metadata file for an album", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("path", help="Absolute path to album folder")
    
    args = parser.parse_args()
    path = args.path
    generate_metadata_file(path)
    