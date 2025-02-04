FROM python:3.9

WORKDIR /app

# Copiar todos os arquivos do repositório para o contêiner
COPY . .

# Instalar as dependências do Python
RUN pip install -r requirements.txt

# Instalar Playwright e Chromium
RUN playwright install --with-deps chromium

# Rodar o Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
