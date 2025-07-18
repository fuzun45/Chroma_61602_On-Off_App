
# On-Off Test Sistemi – **Chroma 61602**  
Aviyonik AC Güç Kaynağı Kontrol ve Otomasyon Aracı
---

Bu proje, **Chroma 61602** serisi programlanabilir AC güç kaynağını (ve muadilleri)  
RS-232 veya USB-TMC üzerinden kontrol etmek için hazırlanmış, Python + Tkinter tabanlı  
basit ama işlevsel bir **GUI uygulamasıdır**. Hedef kullanım senaryosu;  
havacılık/aviyonik test laboratuvarlarında -özellikle 115 V AC @ 400 Hz besleme gerektiren  
cihazlar için- tekrarlı **On/Off çevrim** (cycle) testleri ve manuel çıkış yönetimidir.

---

## 💡 Özellikler
| Başlık | Açıklama |
|---|---|
| **Tak-çalıştır bağlantı** | Uygulama açıldığında VISA kaynaklarını arar, ilk ASRL (RS-232) veya USB cihazı otomatik seçer. |
| **Temel güç ayarları** | Voltaj (V) ve frekans (Hz) alanları; havacılık standardı **115 V / 400 Hz** varsayılanıyla gelir. |
| **Manual çıkış anahtarı** | “Çıkış: **AÇIK / KAPALI**” butonu ile anlık kontrol. |
| **Otomatik çevrim testi** | Kullanıcı tanımlı **açık süresi**, **kapalı süresi** ve **toplam döngü sayısı**. |
| **Sürekli test kipi** | Sonsuz döngü (Stop butonu ile durdurulur); HALT komutu testten çıkar. |
| **İş parçacıklı (threaded) tasarım** | GUI donmaz; test sırasında loglar gerçek zamanlı akar. |
| **Zaman damgalı log penceresi** | Her olay — bağlantı, komut, hata — `[SS:dd:sn]` formatıyla kaydedilir. |
| **Temiz çıkış** | Pencere kapatılırken test iptal edilir, güç çıkışı kapatılır, VISA oturumu kapanır. |

---

## ⚙️ Sistem Gereksinimleri
* **Python 3.8+** (Windows 10/11, 32 bit veya 64 bit)  
* **PyVISA >= 1.13** `pip install pyvisa`  
* **Tkinter** – Python standart kütüphanesinde yer alır  
* **VISA arka ucu (backend)**  
  * Tercih #1 **NI-VISA Runtime** (tam GPIB/USB-TMC/RS-232 desteği)  
  * Tercih #2 Sürücüsüz çözüm için **pyvisa-py** `pip install pyvisa-py`

> **Not 1** USB-TMC yerine RS-232 kullanıyorsanız _chroma cihazının_ baud rate’ini  
> **19200 8N1** olacak şekilde ayarlayın (kodda varsayılan budur).  
> **Not 2** LAN (TCPIP::…) arayüzü eklemek isterseniz `pyvisa.resources.MessageBasedResource`  
> içeren satırlara IP URI’nızı yazmanız yeterlidir.

---

## 🖥️ Kurulum

```bash
# 1) Sanal ortam (opsiyonel ama tavsiye edilir)
python -m venv venv
venv\Scripts\activate

# 2) Gereksinimleri kur
pip install pyvisa            # zorunlu
pip install pyvisa-py         # NI-VISA kurmayacaksanız
pip install pyserial pyusb    # USB veya seri port genişletmeleri için gerekebilir
pip install psutil zeroconf   #Hataları engellemek amaçlı
```

NI-VISA kullanacaksanız:  
<https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html> adresinden
işletim sisteminize uygun **Runtime sürümü** indirin → kurulum sonrası PC’yi yeniden başlatın.

---

## 🚀 Çalıştırma

```bash
python main.py     # veya dosya adı neyse
```

1. **Bağlan** butonuna tıklayın.  
   *Durum: Bağlı* yeşile dönerse cihaz tanınmıştır.  
2. Voltaj / frekans parametrelerini girip **Parametreleri Uygula**‘ya basın.  
3. Manuel test için **Çıkış: KAPALI/AÇIK**,  
   otomatik çevrim için **Test Başlat** veya **Sürekli Test** butonlarını kullanın.  
4. Log penceresini inceleyin; hata oluşursa kırmızı uyarı alırsınız.  
5. **Durdur** ile çevrimi sonlandırabilir, pencereyi kapatarak güvenli çıkış yapabilirsiniz.

---

## 📦 PyInstaller ile Tek Dosya (.exe) Derleme

```bash
# 64-bit EXE (NI-VISA kurulu hedef makineler için)
pyinstaller main.py --onefile --name Chroma61602GUI

# Kurulumsuz, pyvisa-py gömülü 32-bit EXE
py -3.11-32 -m pip install pyinstaller pyvisa pyvisa-py
py -3.11-32 -m pyinstaller main.py --onefile --noupx ^
    --hidden-import pyvisa_py --name Chroma61602GUI-x86
pyinstaller --onefile --noupx --hidden-import pyvisa_py --hidden-import serial.tools.list_ports --hidden-import pyserial --hidden-import psutil --hidden-import zeroconf --windowed --name Chroma61602GUI
```

* `--noupx` Defender’ın “This app can’t run on your PC” uyarılarını azaltır.  
* Her mimari (x86/x64) için **ayrı** derleme şarttır.  

---

## 🐞 Bilinen Sorunlar / SSS

| Hata / Davranış | Çözüm |
|---|---|
| **“Could not locate a VISA implementation”** | NI-VISA kurun **veya** `ResourceManager('@py')` + `pyvisa-py` kullanın. |
| **Çıkış ON/OFF komutları çalışmıyor** | Cihaz adresi yanlış olabilir ↔ SCPI portu kitlenmiş olabilir. Güç kaynağını yeniden başlatın. |
| **GUI donuyor** | Test thread’i kapatılırken `time.sleep` döngüsüne girilmiş olabilir. Durdur butonu ile çıkış yapın. |
| **Bağlantı bulunamadı** | Windows Aygıt Yöneticisi’nde COM portu görünüyor mu? USB-TMC için **USB Test & Measurement Device** etiketi kontrol edin. |

---

## 🤝 Katkıda Bulunma

1. Fork → yeni dal (`feature/xxx`) → değişiklik → **Pull Request**.  
2. Kod standartı olarak *PEP8* + 120 karakter satır sınırı.  
3. Yeni cihaz desteği (Chroma 615xx, Chroma 63800, vb.) eklemek isteyenlere açık çağrı!

---

## 📜 Lisans

MIT Lisansı – Ayrıntı için `LICENSE` dosyasına bakınız.  
> “Kod açıktır; sorumluluk kullanıcıdadır.”

---

### ✈️ Happy testing & safe skies!
