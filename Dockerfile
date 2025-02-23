# استخدام صورة Python رسمية
FROM python:3.11-slim

# تثبيت التبعيات الأساسية
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# تثبيت TA-Lib C
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# إعداد بيئة العمل
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY . .

# تشغيل البوت
CMD ["python", "main.py"]
