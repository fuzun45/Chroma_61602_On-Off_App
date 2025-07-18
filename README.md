# On-Off Test Sistemi - Chroma 61602

Bu proje, havacılık ve aviyonik testlerinde kullanılan Chroma 61602 test ekipmanını kontrol etmek için geliştirilmiş bir On-Off Test Sistemi uygulamasıdır.

## Özellikler

- Chroma 61602 cihazına USB veya RS-232 (seri port) üzerinden bağlanma.
- Voltaj ve frekans parametrelerini ayarlama (örneğin: 115V AC, 400Hz havacılık standardı).
- Cihazın çıkışını manuel olarak açıp kapatma.
- Otomatik test döngüsü başlatma: belirlenen açık/kapalı sürelerde ve döngü sayısında cihazı kontrol etme.
- Sürekli test modu (durdurulana kadar döngü devam eder).
- Test sırasında detaylı log alma.
- Hata ve durum bildirimleri.

## Gereksinimler

- Python 3.7 veya üzeri
- [pyvisa](https://pypi.org/project/PyVISA/) paketi (`pip install pyvisa`)
- tkinter (Python ile birlikte gelir)
- VISA kütüphanesi (örn. NI-VISA) kurulu olmalı

## Kurulum ve Çalıştırma

1. Cihazı bilgisayarınıza USB veya RS-232 (seri port) ile bağlayın.
2. Python 3.7 veya üzeri yüklü olduğundan emin olun.
3. Gerekli Python kütüphanelerini yükleyin:
   ```bash
   pip install pyvisa
   
