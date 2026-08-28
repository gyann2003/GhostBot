FROM python:3.10-slim

# Chrome Browser Install karne ka Hack
RUN apt-get update && apt-get install -y wget gnupg
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update && apt-get install -y google-chrome-stable

# Bot ka code copy karna
WORKDIR /app
COPY . /app

# Requirements install karna
RUN pip install -r requirements.txt

# Bot ko Start karna
CMD ["python", "ghost.py"]
