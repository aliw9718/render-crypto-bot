# استخدام صورة Python رسمية خفيفة
FROM python:3.11-slim

# تثبيت التبعيات الأساسية للبناء
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    gcc \
    g++ \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# تنزيل وتثبيت مكتبة TA-Lib C من المصدر
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

# نسخ ملف المتطلبات وتثبيته
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# تعيين الأمر الافتراضي لتشغيل البوت
CMD ["python", "main.py"]
