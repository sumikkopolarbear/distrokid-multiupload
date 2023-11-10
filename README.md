# distrokid-multiupload
## Installation

```
git clone https://github.com/sumikkopolarbear/distrokid-multiupload.git
```

```
cd distrokid-multiupload
```

```
pip install -r requirements.txt
```

## Script Setup
Look for Profile Path in [chrome://version](chrome://version/).

For Windows, it should look something similar to 
```
C:\Users\caleb\AppData\Local\Google\Chrome\User Data\Default
```
For Mac, it should look similar to
```
~/Library/Application Support/Google/Chrome/Default
```

Go to line 50 of upload.py and update user-data-dir<br><br>
Example:
With profile path `~/Library/Application Support/Google/Chrome/Default`
```
chrome_options.add_argument(r"--user-data-dir={PROFILE_PATH}")
```
becomes
```
chrome_options.add_argument(r"--user-data-dir=~/Library/Application Support/Google/Chrome")
```

Note: The last part of the path (`Default`) is excluded as that is the specific Profile used.

## Album Setup 
- Move all the music files for the album to a directory.
- The name of the album directory will be used as the name of the album.
- The names of the music files will be used as names of the songs.
- If you have a picture in the album directory, it will be used as the album cover.
- Take the folder path and move on to either generate_metadata or upload.

## generate_metadata.py
This is an optional step that will create a `metadata.json` file at the given album path if one doesn't exist already. <br>
If skipped, the upload will still create the metadata file and use that.<br>
The purpose of this step is so that you can edit metadata fields if desired.

`python generate_metadata.py {ALBUM_PATH}`

For example,<br>
`python generate_metadata.py ../test-album`

After the file is created, you can fill out fields in the file before uploading.<br>
Some fields are easier to fill out on the DistroKid website though, so feel free to skip this step.<br><br>

An example generated metadata file is in the test-album folder as `metadata.json`<br>
An example filled out metadata file is also in the test-album folder as `metadata2.json`

## Upload album
Upload will use the metadata file to fill out the DistroKid upload form.
If no metadata file exists at album directory, it'll create one and use that. <br>

`python upload.py {ALBUM_PATH}`

For example,<br>
`python upload.py ../test-album`

### Note:
- Make sure you are logged in to DistroKid and have all Chrome browsers closed. <br> This is because Chrome does not allow Selenium (the open source library used to fill out the form) to open a new Chrome instance while another one is running.
- The script can't fill out fields such as song writers or band names without user input, so make sure to either update the metadata file before uploading or fill out the form after the script finishes.
