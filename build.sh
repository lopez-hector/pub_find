#!/bin/bash

# Upgrade pip to the latest version.
pip install --upgrade pip

# Install packages from the requirements.txt file.
pip install -r requirements.txt

# If you want to force an upgrade of the packages in requirements.txt, use the following command instead:
# pip install --upgrade --force-reinstall -r requirements.txt

echo "Pip upgrade and package installation complete."