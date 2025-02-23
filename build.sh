#!/bin/bash

# تثبيت التبعيات الأساسية
apt-get update && apt-get install -y build-essential wget

# تنزيل وتثبيت مكتبة TA-Lib C
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
make install
cd ..

# تثبيت متطلبات Python
pip install -r requirements.txt
