# 🧩 Pub-Sub Log Aggregator  
**UTS Sistem Paralel dan Terdistribusi – Dhede Kusuma Ramadhan (11221045)**  

## 📘 Deskripsi Sistem  
**Pub-Sub Log Aggregator** adalah layanan berbasis **FastAPI** yang mengimplementasikan arsitektur *publish-subscribe* untuk mengumpulkan dan memproses log secara paralel.  
Sistem ini memiliki *idempotent consumer* yang menjamin setiap event hanya diproses sekali, meskipun terjadi pengiriman ulang (*at-least-once delivery*).  
Seluruh komponen dijalankan di dalam container menggunakan **Docker** agar terisolasi, portabel, dan mudah direplikasi.

---

## ⚙️ Fitur Utama  
- ✅ **Asynchronous Processing** menggunakan `asyncio.Queue`  
- 🔁 **Idempotent Consumer** untuk mencegah pemrosesan ganda  
- 💾 **Persistent Dedup Store (SQLite)** agar data tidak hilang meskipun container dimatikan  
- 🧠 **Event Deduplication** berdasarkan pasangan `(topic, event_id)`  
- 📊 **Monitoring Endpoint** untuk statistik dan daftar event  
- 🐳 **Dockerized Deployment** untuk eksekusi otomatis seluruh layanan  

---

## 🏗️ Arsitektur Sistem

```
+-------------+        +--------------------+        +--------------------+
|  Publisher  | -----> |  Aggregator (API)  | -----> |   Async Queue      |
+-------------+        +--------------------+        +---------+----------+
                                                           |
                                                           v
                                                    +--------------+
                                                    |  Consumer(s) |
                                                    | (async task) |
                                                    +------+-------+
                                                           |
                                                           v
                                               +---------------------------+
                                               |  Dedup Store (DB)         |
                                               |  SQLite persisted storage |
                                               +---------------------------+
```

Komponen utama:
- **Publisher:** mengirim event/log ke endpoint `/publish`.
- **Aggregator:** memvalidasi dan memasukkan event ke antrian.
- **Consumer:** memproses event secara paralel dan menyimpan hasil unik.
- **Dedup Store:** menyimpan kombinasi `(topic, event_id)` untuk deduplikasi.

---

## 🚀 Cara Menjalankan Proyek  

### 1️⃣ Persiapan  
Pastikan sudah menginstal:
- [Docker](https://www.docker.com/)
- [Python 3.10+](https://www.python.org/)

### 2️⃣ Build dan Jalankan Container  
```
docker build -t uts-aggregator .
docker run -p 8080:8080 uts-aggregator
```
