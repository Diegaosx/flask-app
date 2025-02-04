FROM python:3.9

WORKDIR /app

# Instalar dependências do sistema para o Chromium
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2

# Copiar dependências do Python e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar o Chromium via Playwright
RUN playwright install --with-deps chromium

COPY . .

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
