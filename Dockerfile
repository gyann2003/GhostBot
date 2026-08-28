FROM python:3.10-slim

# Chrome Install karne ka Naya aur Safe Tareeka (Bina apt-key ke)
RUN apt-get update && apt-get install -y wget curl gnupg
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
RUN sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update && apt-get install -y google-chrome-stable

# Bot ka code copy karna
WORKDIR /app
COPY . /app

# Requirements install karna
RUN pip install -r requirements.txt

# Bot ko Start karna
CMD ["python", "ghost.py"]
