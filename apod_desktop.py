""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)
"""
import os.path
import sqlite3
import time
from datetime import datetime, date
from hashlib import sha256
from os import path
from sys import argv, exit, getsizeof

###
import requests


def main():

    # Determine the paths where files are stored                    
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    #code up from here is completely done!!!!!!!!!!!-----------------------------------------------

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
    image_url = apod_info_dict["hdurl"]
    
    # Download today's APOD
    image_msg = download_apod_image(image_url)
    img_bytes = image_msg.content
    hasher = sha256()
    hasher.update(img_bytes)
    image_sha256 = hasher.hexdigest()
    image_size = getsizeof(img_bytes)

    image_path = get_image_path(image_url, image_dir_path)

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        print("Image does not exist, saving it to the database.")
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)
    else:
        print("Image already exists skipping saving...")

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_dir_path(): #THIS IS DONE NO NOT TOUCH
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date(): #THIS IS DONE DO NOT TOUCH
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return apod_date

def get_image_path(image_url, dir_path):
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    base_filename = os.path.basename(image_url)
    new_filename = os.path.join(dir_path, base_filename)
    return new_filename

def get_apod_info(date):
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """
    URL = "https://api.nasa.gov/planetary/apod"
    params = {
        'api_key': "2C1wl8V1ce3mhjzvGeHPRieCvRwQTuQuBVyuyBTv",
        'date':date
    }
    response = requests.get(URL, params=params).json()
    return response

def print_apod_info(image_url, image_path, image_size, image_sha256):
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """

    print("IMAGE INFO")
    print("=============")
    print("URL", image_url)
    print("LOCAL PATH", image_path)
    print("SIZE", image_size)
    print("SHA256", image_sha256)

def download_apod_image(image_url):
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """

    response = requests.get(image_url)
    if not response.ok:
        raise RuntimeError("Couldn't find the image, check your network")
    return response

def save_image_file(image_msg, image_path):
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """
    with open(image_path, "wb") as img_file:
        img_file.write(image_msg.content)

def create_image_db(db_path):
    """
    Creates an image database if it doesn't already exist.

    :param db_path: Path of .db file
    :returns: None
    """
    db = sqlite3.connect(db_path)
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS contacts (location text, filesize integer, SHA256 integer, datetime integer);')
    db.commit()
    db.close()

def add_image_to_db(db_path, image_path, image_size, image_sha256):
    """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    db = sqlite3.connect(db_path)
    c = db.cursor()
    curr_time = int(time.time())
    c.execute('insert into contacts values (?,?,?,?)', (image_path, image_size, image_sha256, curr_time))
    db.commit()
    db.close()

def image_already_in_db(db_path, image_sha256):
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """
    db = sqlite3.connect(db_path)
    c = db.cursor()
    c.execute("SELECT SHA256 FROM contacts WHERE SHA256 = ?", (image_sha256,))
    exist = c.fetchone()
    db.close()
    if exist is not None:
        return True
    else:
        return False

def set_desktop_background_image(image_path):
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    print(image_path)
    import ctypes
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path , 0)

main()