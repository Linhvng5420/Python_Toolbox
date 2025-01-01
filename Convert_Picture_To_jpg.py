import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image
from selenium.webdriver.chrome.options import Options

def capture_web_to_image(url, output_path):
    """
    Capture a screenshot of the given URL and save it as a JPG file.

    :param url: The URL of the webpage to capture.
    :param output_path: The path to save the output JPG file.
    """
    # Setup headless Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    try:
        # Open the webpage
        driver.get(url)

        # Capture screenshot
        screenshot_path = output_path.replace('.jpg', '.png')
        driver.save_screenshot(screenshot_path)

        # Convert PNG to JPG
        with Image.open(screenshot_path) as img:
            rgb_image = img.convert('RGB')
            rgb_image.save(output_path, "JPEG")

        # Remove temporary PNG file
        os.remove(screenshot_path)

        print(f"Saved: {output_path}")
    except Exception as e:
        print(f"Error capturing {url}: {e}")
    finally:
        driver.quit()

def convert_folder_to_jpg(input_folder, output_folder):
    """
    Convert all text files containing URLs in the folder to JPG images.

    :param input_folder: Folder containing text files with URLs.
    :param output_folder: Folder to save the resulting JPG images.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, 'r') as file:
                urls = file.readlines()

            for i, url in enumerate(urls):
                url = url.strip()
                if url:
                    output_path = os.path.join(output_folder, f"{filename}_{i + 1}.jpg")
                    capture_web_to_image(url, output_path)

if __name__ == "__main__":
    # Input and output folders
    input_folder = input("Enter the path to the folder containing URL files: ").strip()
    output_folder = input("Enter the path to save the JPG images: ").strip()

    convert_folder_to_jpg(input_folder, output_folder)
    print("Conversion complete!")
