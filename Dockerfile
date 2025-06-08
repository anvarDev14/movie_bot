FROM python:3.11-slim

# Zarur tizim paketlarini o'rnating (agar sizning kutubxonalar kompilyatsiya talab qiladigan bo'lsa)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt ni /app ga nusxalash
COPY requirements.txt /app/

# Talab qilingan Python kutubxonalarini o'rnating
RUN pip install --no-cache-dir -r requirements.txt

# Loyihani konteynerga nusxalash
COPY . /app/

# Dastur ishga tushishi
CMD ["python", "app.py"]
