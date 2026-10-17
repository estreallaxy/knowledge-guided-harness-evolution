#!/bin/bash
# Download adversarial images from Visual-Adversarial-Examples-Jailbreak-Large-Language-Models

echo "Downloading adversarial images for VLM evaluation..."

# Create directory for adversarial images
mkdir -p data/adversarial_images

# Clone the repository (sparse checkout to only get images)
cd data
if [ ! -d "Visual-Adversarial-Examples-Jailbreak-Large-Language-Models" ]; then
    git clone --depth 1 https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models.git
fi

# Copy adversarial images to our data directory
cp -r Visual-Adversarial-Examples-Jailbreak-Large-Language-Models/adversarial_images/* adversarial_images/

echo "✓ Adversarial images downloaded to data/adversarial_images/"
echo "Available images:"
ls -lh adversarial_images/

cd ..
