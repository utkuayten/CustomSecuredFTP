# Resmi Python imajını temel alıyoruz
FROM python:3.10-slim

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# Gerekli bağımlılıkları yüklüyoruz
RUN apt-get update && apt-get install -y \
    python3-tk \
    libxcb-xinerama0 \
    && apt-get clean

# Proje dosyalarını konteynere kopyalıyoruz
COPY . /app

# PYTHONPATH'i ayarlıyoruz
ENV PYTHONPATH=/app

# Gerekli Python bağımlılıklarını yüklüyoruz
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı çalıştırıyoruz
CMD ["python", "client_side/main.py"]
