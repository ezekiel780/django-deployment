#!/bin/sh
set -e

# Usage: ./Scripts/generate-self-signed.sh example.com
DOMAIN=${1:-lipschitz}
OUT_DIR=./certs
LIVE_DIR="$OUT_DIR/live/lipschitz"
WWW_DIR="$OUT_DIR/www"
mkdir -p "$LIVE_DIR" "$WWW_DIR"

# Generate key and cert
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$LIVE_DIR/privkey.pem" \
  -out "$LIVE_DIR/fullchain.pem" \
  -subj "/C=US/ST=State/L=City/O=Org/CN=$DOMAIN"

echo "Self-signed cert generated at $LIVE_DIR/fullchain.pem and privkey.pem"
