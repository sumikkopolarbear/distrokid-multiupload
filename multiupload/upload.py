import argparse
from datetime import datetime
from generate_metadata import generate_metadata_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import os
import json

def read_metadata(path):
    metadata_file_name = "metadata.json"
    metadata_fields = ["album_name", "band_name", "release_date", "record_label", "genre", "album_cover_file_name", "songs"]
    
    # Check if album path is valid
    if not os.path.isdir(path):
        raise FileNotFoundError(f"No such album directory: '{path}'")
    
    # If album metadata does not exist, create it before uploading
    metadata_path = path + "//" + metadata_file_name
    if not os.path.isfile(metadata_path):
        print(f"No album metadata found at {path}. Creating...")
        generate_metadata_file(path)
        print("Album metadata created.")
    
    # Check if album metadata has any missing fields
    with open(metadata_path) as json_file:
        album_data = json.load(json_file)
        missing_fields = set(metadata_fields).difference(set(album_data.keys()))
        if len(missing_fields) > 0:
            raise KeyError(f"Album metadata file at {metadata_path} missing field(s): {missing_fields}")

    # Print metadata fields
    print("Collecting album metadata...")
    for item in metadata_fields:
        print(f"{item}: {album_data[item]}")
    
    return album_data


def upload(album_data, path):
    print("Uploading album data...")
    print(f"Num songs = {len(album_data['songs'])}")
    
    chrome_options = Options()
    #browswer stays open after script finishes running
    chrome_options.add_experimental_option("detach", True)
    #NEED TO UPDATE CHROME USER DATA DIR. SEE README FOR DETAILS
    chrome_options.add_argument(r"--user-data-dir=C:\Users\Caleb\AppData\Local\Google\Chrome\User Data")
    chrome_options.add_argument('--profile-directory=Default')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://distrokid.com/new-upload/")
    driver.implicitly_wait(3)
    
    if 'upload' not in str(driver.current_url):
        raise AssertionError("Upload form not reached. Try logging in to DistroKid or closing all chrome browsers and re-try.")
    
    #Update total number of songs
    select = Select(driver.find_element('id','howManySongsOnThisAlbum'))
    select.select_by_value(str(len(album_data['songs'])))
    
    #Update artist/band name
    artist_name = driver.find_element('id','artistName')
    artist_name.clear()
    artist_name.send_keys(album_data['band_name'])

    #Validate release date
    try:
        if "-" in album_data["release_date"]:
            date = datetime.strptime(album_data["release_date"], "%Y-%m-%d")
        else:
            date = datetime.strptime(album_data["release_date"], "%Y/%m/%d")
    except:
        raise KeyError(f"Invalid album metadata release date. Expecting a valid date in the format of YYYY-MM-DD or YYYY/MM/DD but got {album_data['release_date']}")
    
    #Update release date
    try:
        select = Select(driver.find_element('id','js-release-year'))
        select.select_by_visible_text(str(date.year))
        select = Select(driver.find_element('id','js-release-month'))
        select.select_by_value(str(date.month))
        select = Select(driver.find_element('id','js-release-day'))
        select.select_by_visible_text(str(date.day))
        
    except:
        raise KeyError(f"Album metadata release date '{album_data['release_date']}' not found in distrokid drop down fields.")
    
    #Update record label
    record_label = driver.find_element('id','recordLabel')
    record_label.clear()
    record_label.send_keys(album_data['record_label'])

    #Update album cover
    driver.find_element('id','artwork').send_keys(path + "//" + album_data['album_cover_file_name'])
    
    #Verify genre(s) are valid
    select = Select(driver.find_element('id','genrePrimary'))
    matching_text = ""
    
    if 'genre_secondary' in album_data.keys():
        select_secondary = Select(driver.find_element('id','genreSecondary'))
        matching_secondary_text = ""
    
    for option in select.options:
        if option.text.lower().replace(" ","") == album_data["genre"].lower().replace(" ",""):
            matching_text = option.text
            
        if 'genre_secondary' in album_data.keys():
            if option.text.lower().replace(" ","") == album_data["genre_secondary"].lower().replace(" ",""):
                matching_secondary_text = option.text
    
    #Update genre(s)
    if matching_text != "":
        select.select_by_visible_text(matching_text)
    elif album_data['genre'] != "":
        raise KeyError(f"Album genre '{album_data['genre']}' not found in distrokid drop down fields.")
    
    if 'genre_secondary' in album_data.keys():
        if matching_secondary_text != "":
            select_secondary.select_by_visible_text(matching_secondary_text)
        elif album_data['genre_secondary'] != "": 
            raise KeyError(f"Album secondary genre '{album_data['genre_secondary']}' not found in distrokid drop down fields.")
        
    #Update album title
    driver.find_element('id','albumTitleInput').send_keys(album_data['record_label'])
    
    driver.implicitly_wait(3)

    #Add songs
    song_data = album_data['songs']
    for song_num in range(len(song_data)):
        #Update song title
        driver.find_element('xpath', f"//input[@placeholder='Track {song_num+1} title']").send_keys(song_data[song_num]["title"])
        
        #Add song file
        driver.find_element('id',f'js-track-upload-{song_num+1}').send_keys(path + "//" + song_data[song_num]["file_name"])
        
        #Add additonal songwriters if more than 1 songwriter
        add_writer_button = driver.find_element('id', f"js-add-another-songwriter-link-{song_num+1}")
        for writer_num in range(len(song_data[song_num]['writers'])-1):
            add_writer_button.click()
            
        #Fill out song writer info
        writer_role_buttons = driver.find_elements('xpath', f"//select[@tracknum='{song_num+1}']")
        track_text_fields = driver.find_elements('xpath', f"//input[@type='text'][@tracknum='{song_num+1}']")[3:]
 

        for writer_num in range(len(song_data[song_num]['writers'])):
            writer_data = song_data[song_num]['writers'][writer_num]
            
            #Update song writer role
            if "contribution" in writer_data.keys():
                if writer_data["contribution"] == 'm':
                    role_value = 125
                elif writer_data["contribution"] == 'l':
                    role_value = 126
                else:
                    role_value = 197
                select = Select(writer_role_buttons[writer_num])
                select.select_by_value(str(role_value))
            
            #Update song writer name if name is provided
            if "first_name" in writer_data.keys():
                track_text_fields[3*writer_num].send_keys(writer_data["first_name"])
            if "middle_name" in writer_data.keys():
                track_text_fields[3*writer_num+1].send_keys(writer_data["middle_name"])
            if "last_name" in writer_data.keys():
                track_text_fields[3*writer_num+2].send_keys(writer_data["last_name"])
            
        

    print(f"Finished uploading data to DistroKid!")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Uploads album data to DistroKid", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("path", help="Absolute path to album folder")
    
    args = parser.parse_args()
    path =  os.path.abspath(args.path)
    upload(read_metadata(path), path)
