from flask import Flask, request, send_file
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

def capture_screenshot(url):
    """Tira um print da página e salva localmente"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Simula um navegador real
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        # Carrega a página e espera o carregamento completo
        page.goto(url, timeout=60000)  # Espera até 60s para carregar
        page.wait_for_load_state("networkidle")  # Espera até não haver mais requisições pendentes

        # Scroll para garantir carregamento de imagens dinâmicas
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        page.wait_for_timeout(3000)  # Espera 3 segundos após o scroll

        # Define o caminho do screenshot
        screenshot_path = "screenshot.png"
        page.screenshot(path=screenshot_path, full_page=True)
        
        browser.close()
        return screenshot_path

@app.route("/")
def home():
    return "Flask Screenshot API está rodando!"

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
