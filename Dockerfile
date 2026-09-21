FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    fonts-dejavu \
    ca-certificates \
    fonts-liberation \
    xvfb \
    unzip \
    dbus-x11 \
    gnupg \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    libu2f-udev \
    xdg-utils \
    --no-install-recommends \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable && google-chrome-stable --version \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y jq

# Set up Xvfb and working directory
ENV DISPLAY=:99
RUN mkdir -p /tmp/.xvfb && chmod 1777 /tmp/.xvfb
WORKDIR /app



# Configure environment
ENV MPLCONFIGDIR=/tmp/matplotlib \
    XDG_CACHE_HOME=/tmp/.cache \
    XDG_CONFIG_HOME=/tmp/.config \
    XDG_DATA_HOME=/tmp/.local/share \
    FONTCONFIG_PATH=/etc/fonts \
    FONTCONFIG_FILE=/etc/fonts/fonts.conf \
    FONTCONFIG_CACHE=/tmp/fontconfig \
    GRADIO_TEMP_DIR=/tmp/gradio \
    CHROMEDRIVER_PATH=/usr/local/bin/chromedriver \
    CHROME_BIN=/usr/bin/google-chrome-stable

# Create directories with correct permissions
RUN mkdir -p ${XDG_CACHE_HOME} && chmod 777 ${XDG_CACHE_HOME} \
    && mkdir -p ${XDG_CONFIG_HOME} && chmod 777 ${XDG_CONFIG_HOME} \
    && mkdir -p ${XDG_DATA_HOME} && chmod 777 ${XDG_DATA_HOME} \
    && mkdir -p ${FONTCONFIG_CACHE} && chmod 777 ${FONTCONFIG_CACHE} \
    && mkdir -p /app/flagged && chmod 777 /app/flagged \
    && mkdir -p /tmp/.local/share/applications \
    && touch /tmp/.local/share/applications/mimeapps.list \
    && chmod 777 /tmp/.local/share/applications/mimeapps.list

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ChromeDriver - Manual version specification
# Check Chrome version first and then install matching ChromeDriver

# RUN CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | cut -d'.' -f1) \
#     && echo "Chrome major version: $CHROME_VERSION" \
#     && CHROME_DRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) \
#     && echo "Installing ChromeDriver version: $CHROME_DRIVER_VERSION" \
#     && wget -q https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
#     && unzip chromedriver_linux64.zip \
#     && rm chromedriver_linux64.zip \
#     && mv chromedriver /usr/local/bin/ \
#     && chmod +x /usr/local/bin/chromedriver

# Hardcoded ChromeDriver version (replace with the version you need)
# RUN wget -q https://huggingface.co/datasets/Juna190825/chromedriver/resolve/main/chromedriver \
#    && mv chromedriver /usr/local/bin/ \
#    && chmod +x /usr/local/bin/chromedriver

COPY install_chromedriver.sh /tmp/install_chromedriver.sh
# RUN apt-get install -y dos2unix && dos2unix /tmp/install_chromedriver.sh
# RUN bash /tmp/install_chromedriver.sh && /tmp/install_chromedriver.sh
RUN bash -c '\
    CHROME_VERSION=$(google-chrome-stable --version | awk "{print \$3}" | cut -d"." -f1); \
    echo "Detected Chrome major version: $CHROME_VERSION"; \
    if [ "$CHROME_VERSION" -ge 115 ]; then \
        CHROMEDRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | \
            jq -r ".channels.Stable.downloads.chromedriver[0].version"); \
        DRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | \
            jq -r ".channels.Stable.downloads.chromedriver[0].url"); \
        echo "Using ChromeDriver version: $CHROMEDRIVER_VERSION from $DRIVER_URL"; \
        wget -q "$DRIVER_URL" -O chromedriver.zip; \
        unzip chromedriver.zip; \
        mv chromedriver-linux64/chromedriver /usr/local/bin/; \
    else \
        CHROMEDRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE_"$CHROME_VERSION"); \
        echo "Using legacy ChromeDriver version: $CHROMEDRIVER_VERSION"; \
        wget -q https://chromedriver.storage.googleapis.com/"$CHROMEDRIVER_VERSION"/chromedriver_linux64.zip -O chromedriver.zip; \
        unzip chromedriver.zip; \
        mv chromedriver /usr/local/bin/; \
    fi; \
    rm -rf chromedriver.zip chromedriver-linux64; \
    chmod +x /usr/local/bin/chromedriver'




# Verify installations
RUN echo "Chrome version:" && google-chrome-stable --version \
    && echo "ChromeDriver version:" && chromedriver --version

# Ensure proper port exposure
EXPOSE 7860
EXPOSE 9222

# Add health check
HEALTHCHECK --interval=30s --timeout=30s \
  CMD curl -f http://localhost:7860 || exit 1

# Copy application
COPY . .

# Start script
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & python app.py"]
