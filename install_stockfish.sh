#!/usr/bin/env bash
set -e

# Target directory
mkdir -p stockfish

# Only download if the Linux binary isn't already present (caching optimization)
if [ ! -f stockfish/stockfish ]; then
  echo "Downloading Stockfish Linux binary..."
  
  # Official Stockfish Linux x86-64 release URL
  curl -sL "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64.tar" -o stockfish.tar
  
  # Extract
  tar -xf stockfish.tar
  
  # Move the binary into the stockfish folder and make it executable
  mv stockfish/stockfish-ubuntu-x86-64 stockfish/stockfish
  chmod +x stockfish/stockfish
  
  # Cleanup
  rm -rf stockfish.tar
  echo "Stockfish setup complete."
fi