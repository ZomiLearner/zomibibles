# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including Chrome's required libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# --- Install Chrome for Testing (stable, official source) ---
# Pin a specific version for reproducible builds.
# Check latest at: https://googlechromelabs.github.io/chrome-for-testing/
ARG CHROME_VERSION=153.0.8010.52

RUN wget -q -O /tmp/chrome-linux64.zip \
      "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip" \
    && unzip /tmp/chrome-linux64.zip -d /opt/ \
    && ln -s /opt/chrome-linux64/chrome /usr/local/bin/chrome \
    && ln -s /opt/chrome-linux64/chrome /usr/local/bin/google-chrome \
    && ln -s /opt/chrome-linux64/chrome /usr/local/bin/google-chrome-stable \
    && rm /tmp/chrome-linux64.zip

# --- Install matching ChromeDriver ---
RUN wget -q -O /tmp/chromedriver-linux64.zip \
      "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip /tmp/chromedriver-linux64.zip -d /opt/ \
    && ln -s /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /opt/chromedriver-linux64/chromedriver \
    && rm /tmp/chromedriver-linux64.zip

# Verify installations (fails the build early if something's wrong)
RUN chrome --version && chromedriver --version

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Railway will assign via the $PORT variable
EXPOSE $PORT

# Build-time: concatenate the .py files into one
RUN cat setup_selenium.py bible_scrapping_helper.py fetch_tbs_verse.py get_bible_verses.py fetch_tbs_bible.py >> combined.py

# Run the app using Uvicorn, binding to 0.0.0.0 and the dynamic port
# CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
CMD ["sh", "-c", "python3 combined.py & uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
