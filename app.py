from flask import Flask, request, send_file
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

def capture_screenshot(url):
    """Tira um print da página e salva localmente"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        screenshot_path = "screenshot.png"
        page.screenshot(path=screenshot_path, full_page=True)
        browser.close()
        return screenshot_path

@app.route("/")
def home():
    return "Flask no EasyPanel está rodando!"

@app.route("/screenshot", methods=["GET"])
def screenshot():
    url = request.args.get("url")
    if not url:
        return {"error": "Informe a URL como parâmetro (?url=)"}, 400

    try:
        screenshot_path = capture_screenshot(url)
        return send_file(screenshot_path, mimetype="image/png")
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
