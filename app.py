from flask import Flask, request, jsonify, send_file
from playwright.sync_api import sync_playwrightimport os
from kokoro import KPipeline
import soundfile as sf
import uuid

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

def generate_instagram_screenshot(instagram_url):
    """Cria um HTML temporário com o embed do Instagram e tira o print"""

    # Gera o código embed do Instagram
    embed_html = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ display: flex; justify-content: center; align-items: center; height: 100vh; background: #fff; }}
                blockquote {{ width: 600px; max-width: 100%; }}
            </style>
        </head>
        <body>
            <blockquote class='instagram-media' data-instgrm-version='14'>
                <a href='{instagram_url}'></a>
            </blockquote>
            <script async src="https://www.instagram.com/embed.js"></script>
        </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="pt-BR",  # Define idioma como português (Brasil)
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        )
        page = context.new_page()

        # Carregar HTML diretamente no navegador
        page.set_content(embed_html)
        page.wait_for_load_state("networkidle")  # Espera o carregamento completo

        # Aguarda um tempo extra para garantir que o post foi embutido corretamente
        page.wait_for_timeout(3000)

        # Define o caminho do screenshot
        screenshot_path = "instagram_screenshot.png"
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

@app.route("/screenshot/instagram", methods=["GET"])
def screenshot_instagram():
    instagram_url = request.args.get("url")
    
    if not instagram_url:
        return {"error": "Informe a URL do post do Instagram (?url=)"}, 400

    try:
        screenshot_path = generate_instagram_screenshot(instagram_url)
        return send_file(screenshot_path, mimetype="image/png")
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    
    instance = data.get('instance')
    number = data.get('number')
    text = data.get('text')
    apikey = data.get('apikey')
    
    if not all([instance, number, text, apikey]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    url = f"https://zap.redegram.com/message/sendText/{instance}"
    headers = {
        'Content-Type': 'application/json',
        'apikey': apikey
    }
    payload = {
        'number': number,
        'text': text
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return jsonify(response.json()), response.status_code


# Rota TTS
@app.route("/tts", methods=["POST"])
def tts():
    data = request.json

    # Validação dos parâmetros
    required = ["voice", "text", "speed"]
    if not all(param in data for param in required):
        return jsonify({"error": "Missing parameters"}), 400

    try:
        # Inicializa o pipeline do Kokoro
        pipeline = KPipeline(lang_code='a')  # 'a' para autodetectar idioma

        # Gera o áudio
        generator = pipeline(
            text=data["text"],
            voice=data["voice"],
            speed=data["speed"]  # Ajuste de velocidade (ex: 1.0 = normal)
        )

        # Salva o áudio em um arquivo temporário
        audio_data = next(generator)[2]  # Pega o primeiro chunk de áudio
        filename = f"{uuid.uuid4()}.wav"
        sf.write(filename, audio_data, 24000)

        # Retorna o arquivo como resposta
        return send_file(
            filename,
            mimetype="audio/wav",
            as_attachment=True,
            download_name="output.wav"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Remove o arquivo temporário
        if 'filename' in locals():
            os.remove(filename)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
