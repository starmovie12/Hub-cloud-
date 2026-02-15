# 1. Python Image (Stable Version)
FROM python:3.9-slim-bookworm

# 2. Install Basic Tools
# Humne bekar ke packages hata diye hain
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Google Chrome (The Smart Way)
# Ye command direct Chrome download karegi aur uske liye zaroori
# saare drivers khud dhoond kar install karegi. No manual errors!
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# 4. Set Working Directory
WORKDIR /app

# 5. Copy Files
COPY . /app

# 6. Install Python Requirements
RUN pip install --no-cache-dir -r requirements.txt

# 7. Run the App
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
