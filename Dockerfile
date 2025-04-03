FROM python:3.9

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    espeak-ng \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências Python
RUN pip install -r requirements.txt

# Instala Playwright e Chromium
RUN playwright install --with-deps chromium

# Expõe a porta
EXPOSE 5000

# Inicia o app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
