#Word from Olympus:
from website import create_app
#pip install -r requirements.txt (if I listed them in a requirements.txt)
#Heathens:
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from flask import Flask, send_file
from pathlib import Path
import datetime, pytz

app = create_app()

# Path to your ChromeDriver
chrome_driver_path = "webdriver\chromedriver.exe"  # This is the chromedriver path

# Path to the directory where files will be saved on the server
project_root = Path(__file__).resolve().parent  # This will be the root of your repository
download_dir = project_root / "downloads"  # Folder inside the project to save downloaded files

# Ensure the download folder exists
download_dir.mkdir(parents=True, exist_ok=True)

# Set up Chrome options to download files to the server's directory
chrome_options = Options()
chrome_options.add_argument("--disable-software-rasterizer")    #an update with error
chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
prefs = {
    "download.default_directory": str(download_dir),  # Set the download directory to our server folder
    "download.prompt_for_download": False,             # Don't prompt for download location
    "safebrowsing.enabled": False                      # Disable safe browsing warnings
}
chrome_options.add_experimental_option("prefs", prefs)

# Function to create and return a Selenium WebDriver
def create_driver():
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Download function using Selenium
def download_excel():
    driver = create_driver()
    # Open the webpage where the download link is located
    driver.get("https://www.fincen.gov/msb-state-selector") #url for website to scrape

    #xpath is the flexible way of specifying multiple attributes such as class id and href (the link uses javascript, not static link)
    try:
        #switch to the iframe in this case --updated
        driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@id='MSBframe']"))

        # Wait for the element (download link) to be clickable
        download_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@id='ExportExcelLink' and contains(@class, 'exportall') and @href='#']"))
        )

        # Click the download button to trigger the file download
        download_button.click()

        # Wait for the download to complete (adjust wait time if needed)
        time.sleep(5)  # Adjust depending on download time and file size
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

    #alternatively should just see if count of files in downloads dir has gone up since start of script (use var) because name random
    """ # Check if the file was downloaded successfully
    downloaded_file = download_dir / "data.xlsx"  # File name may vary depending on the server
    if downloaded_file.exists():
        print(f"File downloaded successfully: {downloaded_file}")
        return downloaded_file
    else:
        print("Download failed.")
        return None """

# Flask route to trigger download and send the file to the client
@app.route('/download_excel')
def download_excel_route():
    downloaded_file = download_excel()  # Calls the Selenium-based download function

    if downloaded_file:
        # Serve the downloaded file as an attachment to the client
        return send_file(downloaded_file, as_attachment=True, attachment_filename="data.xlsx")  #this will be a custom name ^^^
    else:
        return "Download failed", 400

#right now simply checks if the server has any msb data
from pathlib import Path
def due_for_updated_data(save_folder):
    # Set the path to your downloads directory
    downloads_dir = Path("downloads")  # Replace with actual path

    # Check if the directory exists
    if downloads_dir.exists() and downloads_dir.is_dir():
        # Check if there are any files in the directory
        if any(downloads_dir.iterdir()):
            #file => see date
            print("There are files in the downloads directory.")

            #get file date
            files = glob.glob(save_folder + '/*')
            max_file = max(files, key=os.path.getctime)
            filename = max_file.split("\\")[-1].split(".")[0]

            #compare tokens
            file_tokens = tokenize_time(filename)
            cur_time_tokens = tokenize_time(str(datetime.datetime.now(pytz.timezone('America/Chicago'))))
            #if current year is greater then update
            if(int(cur_time_tokens[0]) > int(file_tokens[0])):  #yr v yr
                return True
            elif(int(cur_time_tokens[1]) > int(file_tokens[1])):    #month v month
                return True
            elif(int(cur_time_tokens[2]) > int(file_tokens[2])):    #day v day
                return True
            elif(int(cur_time_tokens[3]) > int(file_tokens[3])):    #hour v hour (update every hour)
                return True
            else:
                return False    #if only a difference of minutes, do not update
        else:
            #no files => make one
            print("No files found in the downloads directory.")
            return True

def tokenize_time(s):
    s=s.replace(':', '-').replace('.', '-').replace(' ', '-')
    tokens = s.split("-")
    print(tokens)
    return tokens

import glob
#uses os so may not be good
#https://stackoverflow.com/questions/38459972/rename-downloaded-files-selenium#:~:text=You%20don't%20have%20control,and%20then%20rename%20it%20accordingly.
def rename_download(save_folder, new_filename):
    files = glob.glob(save_folder + '/*')
    max_file = max(files, key=os.path.getctime)
    filename = max_file.split("\\")[-1].split(".")[0]
    new_path = max_file.replace(filename, new_filename)
    os.rename(max_file, new_path)
    return new_path

#https://www.geeksforgeeks.org/get-current-date-and-time-using-python/
#filename is decided by time stamp (no matter where it will be in Chicago's time (universal here))
def give_label():
    current_time = datetime.datetime.now(pytz.timezone('America/Chicago'))
    stime = str(current_time)
    stime=stime.replace(':', '-').replace('.', '-').replace(' ', '-')
    return stime

# Start Flask app
if __name__ == '__main__':
    if(due_for_updated_data('downloads')):
        print("Starting download...")
        download_excel_route()  # Calling the download_excel function directly here
        rename_download('downloads', give_label())
        print("Download completed.")
    app.run(debug=True)