# 🕷️ W-Crawler

> **Python ile geliştirilmiş hızlı, çok iş parçacıklı ve terminal tabanlı Web Crawler.**

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux%20%7C%20Windows-orange?style=for-the-badge)]()

---

## 📖 **W-Crawler Nedir?**

**W-Crawler**, Python ile geliştirilmiş **terminal tabanlı bir Web Crawler ve Web Discovery aracıdır.**

Belirtilen bir web sitesini tarayarak aynı domain içerisindeki sayfaları keşfeder, HTTP durum kodlarını analiz eder ve HTML içerisindeki çeşitli kaynakları çıkarır.

---

## ✨ **Özellikler**

- 🌐 **Web sitesi crawling**
- 🔗 **Dahili link keşfi**
- 🧵 **Multi-thread desteği**
- 📊 **HTTP status code analizi**
- 📧 **E-mail keşfi**
- 📞 **Telefon numarası keşfi**
- 📝 **HTML form tespiti**
- 🖼️ **Görsel URL keşfi**
- 📜 **JavaScript kaynak keşfi**
- 🎨 **CSS kaynak keşfi**
- 🤖 **robots.txt desteği**
- 📏 **Ayarlanabilir crawl depth**
- ⏱️ **Request timeout ayarı**
- 💤 **Request delay ayarı**
- 💾 **JSON çıktı desteği**
- 📝 **TXT çıktı desteği**
- 🧵 **Thread sayısı ayarlama**
- 🖥️ **Terminal tabanlı kullanım**
- 📱 **Termux uyumluluğu**
- 🛑 **Ctrl+C ile güvenli durdurma**

---

## 🛠️ **Gereksinimler**

- **Python 3.8+**
- **Requests**
- **BeautifulSoup4**

---

## 📥 **Kurulum**

### 1️⃣ **Repoyu Klonla**

```bash
git clone https://github.com/KULLANICI_ADIN/W-Crawler.git
cd W-Crawler
```

### 2️⃣ **Gerekli Kütüphaneleri Yükle**

```bash
pip install requests beautifulsoup4
```

### 📱 **Termux Kurulumu**

```bash
pkg update
pkg upgrade
pkg install python git
pip install requests beautifulsoup4
```

---

## 🚀 **Kullanım**

```bash
python w-crawler.py
```

Program gerekli ayarları senden isteyecektir:

```text
[?] Hedef URL: https://example.com
[?] Maksimum crawl depth [2]: 3
[?] Thread sayısı [5]: 10
[?] Request timeout [10]: 10
[?] İstekler arası delay [0]: 0.2
[?] robots.txt kurallarına uyulsun? [E/h]: E
```

---

## ⚙️ **Ayarlar**

| Ayar | Açıklama | Varsayılan |
|---|---|---:|
| **URL** | Taranacak hedef web sitesi | `-` |
| **Crawl Depth** | Maksimum tarama derinliği | `2` |
| **Threads** | Eş zamanlı worker sayısı | `5` |
| **Timeout** | HTTP request timeout | `10` |
| **Delay** | İstekler arasındaki bekleme | `0` |
| **Robots** | `robots.txt` kontrolü | **Açık** |

---

## 🧵 **Multi-Thread Sistemi**

W-Crawler aynı anda birden fazla URL üzerinde çalışabilir.

Örneğin:

```text
Threads: 5
```

ayarında crawler aynı anda birden fazla worker kullanır.

**Daha yüksek thread sayısı her zaman daha iyi performans sağlamaz.**

Hedef sunucu, internet bağlantısı ve cihaz kaynaklarına göre uygun bir değer kullanılması önerilir.

---

## 📏 **Crawl Depth**

Crawl Depth, crawler'ın bağlantıları ne kadar derine kadar takip edeceğini belirler.

```text
Depth 0
└── https://example.com/

Depth 1
├── https://example.com/about
├── https://example.com/contact
└── https://example.com/blog

Depth 2
├── https://example.com/blog/post-1
├── https://example.com/blog/post-2
└── https://example.com/contact/map
```

**Depth değerinin yükseltilmesi daha fazla URL keşfedilmesine neden olabilir.**

---

## 🤖 **robots.txt**

W-Crawler varsayılan olarak hedef sitenin:

```text
https://example.com/robots.txt
```

dosyasını kontrol eder.

Crawler, izin verilmeyen URL'leri taramamaya çalışır.

---

## 📊 **Tarama İstatistikleri**

Tarama sonunda W-Crawler aşağıdaki bilgileri gösterir:

```text
[*] Süre       : 12.42 saniye
[*] Ziyaret    : 48
[*] URL keşfi  : 73
[*] Sonuç      : 48
[*] E-mail     : 3
[*] Telefon    : 2
[*] Link       : 164
```

---

## 💾 **Çıktı Dosyaları**

W-Crawler iki farklı formatta sonuç oluşturabilir.

### 📄 **JSON**

```text
w-crawler-results.json
```

JSON dosyası tarama sonuçlarını yapılandırılmış şekilde saklar.

### 📝 **TXT**

```text
w-crawler-results.txt
```

TXT dosyası sonuçları daha kolay okunabilecek şekilde listeler.

---

## 📁 **Proje Yapısı**

```text
W-Crawler/
│
├── w-crawler.py
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🧰 **Kullanılan Kütüphaneler**

### 📦 **Requests**

HTTP istekleri için kullanılır.

### 🍲 **BeautifulSoup4**

HTML parsing ve veri çıkarma işlemleri için kullanılır.

### 🧵 **concurrent.futures**

Multi-thread crawling işlemleri için kullanılır.

### 🔗 **urllib**

URL parsing ve URL yönetimi için kullanılır.

### 📦 **json**

Tarama sonuçlarını JSON formatında kaydetmek için kullanılır.

### 🔍 **re**

E-mail ve telefon numarası adaylarını tespit etmek için kullanılır.

---

## 🔐 **Güvenlik ve Sorumlu Kullanım**

**W-Crawler bir web keşif aracıdır.**

Aracı yalnızca:

- ✅ **Kendi web sitelerinizde**
- ✅ **Yetkiniz bulunan sistemlerde**
- ✅ **Test/lab ortamlarında**
- ✅ **İzin verilmiş güvenlik testlerinde**

kullanmanız önerilir.

### ❌ **Yetkisiz Kullanım**

W-Crawler aşağıdaki amaçlarla tasarlanmamıştır:

- ❌ **Şifre kırma**
- ❌ **Credential stuffing**
- ❌ **Exploit çalıştırma**
- ❌ **Yetkisiz erişim**
- ❌ **Formlara otomatik saldırı**
- ❌ **Güvenlik açığı istismarı**
- ❌ **DoS / DDoS saldırıları**

**Aracı kullanırken hedef sistemin kullanım şartlarına ve yürürlükteki yasalara uyun.**

---

## 🐛 **Hata Bildirme**

Bir hata bulduysanız GitHub üzerinden **Issue** oluşturabilirsiniz.

Issue içerisinde mümkün olduğunca şu bilgileri paylaşın:

```text
Python sürümü:
İşletim sistemi:
W-Crawler sürümü:
Hata mesajı:
Kullandığınız komut:
Hatanın oluştuğu işlem:
```

---

## 💡 **Katkıda Bulunma**

Projeye katkıda bulunmak istiyorsanız:

```bash
git clone https://github.com/KULLANICI_ADIN/W-Crawler.git
cd W-Crawler
git checkout -b feature/yeni-ozellik
```

Değişikliklerinizi yaptıktan sonra **Pull Request** gönderebilirsiniz.

---

## 📜 **Lisans**

Bu proje **MIT License** altında yayımlanmıştır.

Detaylar için `LICENSE` dosyasına bakabilirsiniz.

---

## ⭐ **Destek**

Projeyi faydalı bulduysanız GitHub üzerinde:

**⭐ Star vermeyi unutmayın!**

---

## 🕷️ **W-Crawler**

```text
██╗    ██╗      ██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗
██║    ██║     ██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗
██║ █╗ ██║     ██║     ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝
██║███╗██║     ██║     ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗
╚███╔███╔╝     ╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║
 ╚══╝╚══╝       ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝
```

> **Fast • Simple • Multi-Threaded • Terminal-Based • Python**

---

## 👨‍💻 **Developer**

**W-Crawler**, web keşif ve crawler çalışmalarını kolaylaştırmak amacıyla geliştirilmiştir.

**Made with 🐍 Python**

---

## ⭐ **W-Crawler'a Star Ver!**

Eğer proje işine yaradıysa GitHub reposuna ⭐ **Star** bırakmayı unutma!

**W-Crawler — Crawl. Discover. Analyze.**
*By Muhammet Atilla Altan...*
