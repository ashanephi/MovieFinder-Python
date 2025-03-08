from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

app = Flask(__name__)

def analyze_image(image_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://lens.google.com/")

        # Upload Image
        upload_btn = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_btn.send_keys(image_path)

        time.sleep(7)  # Wait for processing

        # Extract Text
        all_text_elements = driver.find_elements(By.XPATH, "//div[@data-q] | //h2 | //span")
        all_text = [elem.text for elem in all_text_elements]
        
        # Look for movie title
        movie_title = next((text for text in all_text if "movie" in text.lower() or "film" in text.lower()), None)

        return {"movie": movie_title or "No movie title found"}

    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    image = request.files['file']
    image_path = os.path.join("uploads", image.filename)
    os.makedirs("uploads", exist_ok=True)
    image.save(image_path)

    result = analyze_image(image_path)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
