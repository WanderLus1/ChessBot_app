FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Download and extract Linux Stockfish binary
RUN curl -L -o stockfish.tar https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar && \
    mkdir -p stockfish && \
    tar -xvf stockfish.tar -C stockfish --strip-components=1 && \
    chmod +x stockfish/stockfish && \
    rm stockfish.tar

EXPOSE 7860

# Run with Waitress on Hugging Face default port
CMD ["waitress-serve", "--port=7860", "app:app"]