# prepares pi for reading the chrome driver and finding its location
sudo rm /var/lib/apt/lists* -vf
sudo apt-get update
sudo apt-get install chromium-chromedriver