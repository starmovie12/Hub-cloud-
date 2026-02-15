# Python Image
FROM python:3.9-slim

# Install Chrome & Dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome (Latest Stable)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Set Work Directory
WORKDIR /app

# Copy Files
COPY . /app

# Install Python Requirements
RUN pip install --no-cache-dir -r requirements.txt

# Run the App
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
