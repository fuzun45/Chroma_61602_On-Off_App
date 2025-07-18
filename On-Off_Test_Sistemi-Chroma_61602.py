import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyvisa
import time
import threading
from datetime import datetime


class Chroma61602Controller:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.instrument = None
        self.visa_resource = None
        self.stop_event = threading.Event()
        
    def connect(self, timeout: int = 5000):
        try:
            resources = self.rm.list_resources()
            # USB ve RS232 (ASRL) portları dahil et
            chroma_devices = [
                r for r in resources
                if ('ASRL' in r)
            ]
            
            if not chroma_devices:
                return False, "Chroma cihazı bulunamadı!"
                
            self.visa_resource = chroma_devices[0]
            self.instrument = self.rm.open_resource(self.visa_resource)
            self.instrument.timeout = timeout

            # RS-232 (seri port) ayarları
            if 'ASRL' in self.visa_resource:
                self.instrument.baud_rate = 9600  # Gerekirse değiştir
                self.instrument.data_bits = 8
                self.instrument.parity = pyvisa.constants.Parity.none
                self.instrument.stop_bits = pyvisa.constants.StopBits.one
                self.instrument.write_termination = '\r'
                self.instrument.read_termination = '\r'

            # USB için genellikle bu ayarlara gerek yoktur
            else:
                self.instrument.write_termination = '\n'
                self.instrument.read_termination = '\n'
            
            idn = self.instrument.query("*IDN?")
            self.instrument.write("*CLS")
            
            return True, f"{self.visa_resource} üzerinden bağlandı: {idn.strip()}"
            
        except Exception as e:
            return False, f"Bağlantı hatası: {e}"
    
    def disconnect(self):
        if self.instrument:
            try:
                self.instrument.write("OUTPut OFF")
                self.instrument.close()
            except:
                pass
            self.instrument = None
        try:
            self.rm.close()
        except:
            pass
    
    def output_on(self):
        if self.instrument:
            self.instrument.write("OUTPut ON")
            return True
        return False
    
    def output_off(self):
        if self.instrument:
            self.instrument.write("OUTPut OFF")
            return True
        return False
    
    def get_output_state(self):
        if self.instrument:
            try:
                response = self.instrument.query("OUTPut?")
                return response.strip().upper() == "ON"
            except:
                return False
        return False
    
    def set_voltage(self, voltage: float):
        if self.instrument:
            self.instrument.write(f"VOLTage {voltage}")
    
    def set_frequency(self, frequency: float):
        if self.instrument:
            self.instrument.write(f"FREQuency {frequency}")

class AvionicsChromaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("On-Off Test Sistemi - Chroma 61602")
        #self.root.iconbitmap('icon.ico')
        self.root.geometry("550x650")
        self.root.configure(bg='#f0f0f0')
        
        self.controller = Chroma61602Controller()
        self.is_connected = False
        self.cycle_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        
        # Başlık
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = tk.Label(title_frame, text="On-Off Test Sistemi", 
                              font=('Arial', 14, 'bold'), bg='#f0f0f0')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Chroma 61602 - Aviyonik Test Ekipmanı", 
                                 font=('Arial', 10), bg='#f0f0f0', fg='#666')
        subtitle_label.pack()
        
        # Cihaz bağlantısı
        connection_frame = tk.LabelFrame(self.root, text="Cihaz Bağlantısı", 
                                       font=('Arial', 10, 'bold'))
        connection_frame.pack(fill='x', padx=10, pady=5)
        
        conn_button_frame = tk.Frame(connection_frame)
        conn_button_frame.pack(fill='x', padx=5, pady=5)
        
        self.connect_btn = tk.Button(conn_button_frame, text="Bağlan", 
                                    command=self.connect_device, width=10)
        self.connect_btn.pack(side='left', padx=2)
        
        self.disconnect_btn = tk.Button(conn_button_frame, text="Bağlantıyı Kes", 
                                       command=self.disconnect_device, width=12)
        self.disconnect_btn.pack(side='left', padx=2)
        
        self.status_label = tk.Label(conn_button_frame, text="Durum: Bağlı değil", 
                                    fg='red', font=('Arial', 9))
        self.status_label.pack(side='left', padx=10)
        
        # Güç parametreleri
        power_frame = tk.LabelFrame(self.root, text="Güç Parametreleri", 
                                   font=('Arial', 10, 'bold'))
        power_frame.pack(fill='x', padx=10, pady=5)
        
        # Voltaj
        voltage_frame = tk.Frame(power_frame)
        voltage_frame.pack(fill='x', padx=5, pady=3)
        
        tk.Label(voltage_frame, text="Voltaj (V):",width=15).pack(side='left', anchor='w')
        self.voltage_var = tk.StringVar(value="115")
        voltage_entry = tk.Entry(voltage_frame, textvariable=self.voltage_var, width=10)
        voltage_entry.pack(side='left', padx=5)
        tk.Label(voltage_frame, text="(Aviyonik: 115V AC)", 
                fg='#666', font=('Arial', 8)).pack(side='left', padx=5)
        
        # Frekans
        freq_frame = tk.Frame(power_frame)
        freq_frame.pack(fill='x', padx=5, pady=3)
        
        tk.Label(freq_frame, text="Frekans (Hz):", width=15).pack(side='left', anchor='w')
        self.freq_var = tk.StringVar(value="400")
        freq_entry = tk.Entry(freq_frame, textvariable=self.freq_var, width=10)
        freq_entry.pack(side='left', padx=5)
        tk.Label(freq_frame, text="(Havacılık standardı: 400Hz)", 
                fg='#666', font=('Arial', 8)).pack(side='left', padx=5)
        
        apply_btn = tk.Button(power_frame, text="Parametreleri Uygula", 
                             command=self.apply_settings)
        apply_btn.pack(pady=5)
        
        # Manuel kontrol
        manual_frame = tk.LabelFrame(self.root, text="Manuel Kontrol", 
                                    font=('Arial', 10, 'bold'))
        manual_frame.pack(fill='x', padx=10, pady=5)
        
        self.output_btn = tk.Button(manual_frame, text="Çıkış: KAPALI", 
                                   command=self.toggle_output, width=15,
                                   bg='#ffcccc')
        self.output_btn.pack(pady=5)
        
        # Test döngüsü
        cycle_frame = tk.LabelFrame(self.root, text="Otomatik Test Döngüsü", 
                                   font=('Arial', 10, 'bold'))
        cycle_frame.pack(fill='x', padx=10, pady=5)
        
        # Açık süre
        on_time_frame = tk.Frame(cycle_frame)
        on_time_frame.pack(fill='x', padx=5, pady=2)
        
        tk.Label(on_time_frame, text="Açık Süre (s):",width=15).pack(side='left', anchor='w')
        self.on_time_var = tk.StringVar(value="10")
        on_time_entry = tk.Entry(on_time_frame, textvariable=self.on_time_var, width=10)
        on_time_entry.pack(side='left', padx=5)
        
        # Kapalı süre
        off_time_frame = tk.Frame(cycle_frame)
        off_time_frame.pack(fill='x', padx=5, pady=2)
        
        tk.Label(off_time_frame, text="Kapalı Süre (s):",width=15).pack(side='left', anchor='w')
        self.off_time_var = tk.StringVar(value="5")
        off_time_entry = tk.Entry(off_time_frame, textvariable=self.off_time_var, width=10)
        off_time_entry.pack(side='left', padx=5)
        
        # Döngü sayısı
        cycle_count_frame = tk.Frame(cycle_frame)
        cycle_count_frame.pack(fill='x', padx=5, pady=2)
        
        tk.Label(cycle_count_frame, text="Döngü Sayısı:",width=15).pack(side='left', anchor='w')
        self.cycle_count_var = tk.StringVar(value="10")
        cycle_count_entry = tk.Entry(cycle_count_frame, textvariable=self.cycle_count_var, width=10)
        cycle_count_entry.pack(side='left', padx=5)
        
        # Test butonları
        test_button_frame = tk.Frame(cycle_frame)
        test_button_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_cycle_btn = tk.Button(test_button_frame, text="Test Başlat", 
                                        command=self.start_cycle, width=12)
        self.start_cycle_btn.pack(side='left', padx=2)
        
        self.start_continuous_btn = tk.Button(test_button_frame, text="Sürekli Test", 
                                             command=self.start_continuous, width=12)
        self.start_continuous_btn.pack(side='left', padx=2)
        
        self.stop_cycle_btn = tk.Button(test_button_frame, text="Durdur", 
                                       command=self.stop_cycle, width=10,
                                       bg='#ffcccc')
        self.stop_cycle_btn.pack(side='left', padx=2)
        
        # Log alanı
        log_frame = tk.LabelFrame(self.root, text="Test Logları", 
                                 font=('Arial', 10, 'bold'))
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, 
                                                 font=('Courier', 9))
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # İlk log mesajı
        self.log_message("Havacılık test sistemi hazır")
        self.log_message("Cihaza bağlanın ve test parametrelerini ayarlayın")
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def connect_device(self):
        self.log_message("Cihaza bağlanılıyor...")
        success, message = self.controller.connect()
        
        if success:
            self.is_connected = True
            self.status_label.configure(text="Durum: Bağlı", fg='green')
            self.log_message(f"Başarılı: {message}")
        else:
            self.log_message(f"Hata: {message}")
            messagebox.showerror("Bağlantı Hatası", message)
            
    def disconnect_device(self):
        self.controller.disconnect()
        self.is_connected = False
        self.status_label.configure(text="Durum: Bağlı değil", fg='red')
        self.log_message("Cihaz bağlantısı kesildi")
        
    def apply_settings(self):
        if not self.is_connected:
            messagebox.showwarning("Uyarı", "Önce cihaza bağlanın!")
            return
            
        try:
            voltage = float(self.voltage_var.get())
            frequency = float(self.freq_var.get())
            
            self.controller.set_voltage(voltage)
            self.controller.set_frequency(frequency)
            
            self.log_message(f"Parametreler ayarlandı: {voltage}V, {frequency}Hz")
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayı değerleri girin!")
            
    def toggle_output(self):
        if not self.is_connected:
            messagebox.showwarning("Uyarı", "Önce cihaza bağlanın!")
            return
            
        current_state = self.controller.get_output_state()
        
        if current_state:
            self.controller.output_off()
            self.output_btn.configure(text="Çıkış: KAPALI", bg='#ffcccc')
            self.log_message("Çıkış kapatıldı")
        else:
            self.controller.output_on()
            self.output_btn.configure(text="Çıkış: AÇIK", bg='#ccffcc')
            self.log_message("Çıkış açıldı")
            
    def start_cycle(self):
        if not self.is_connected:
            messagebox.showwarning("Uyarı", "Önce cihaza bağlanın!")
            return
            
        try:
            on_time = float(self.on_time_var.get())
            off_time = float(self.off_time_var.get())
            cycles = int(self.cycle_count_var.get())
            
            self.controller.stop_event.clear()
            self.cycle_thread = threading.Thread(target=self.cycle_worker, 
                                                args=(on_time, off_time, cycles))
            self.cycle_thread.start()
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayı değerleri girin!")
            
    def start_continuous(self):
        if not self.is_connected:
            messagebox.showwarning("Uyarı", "Önce cihaza bağlanın!")
            return
            
        try:
            on_time = float(self.on_time_var.get())
            off_time = float(self.off_time_var.get())
            
            self.controller.stop_event.clear()
            self.cycle_thread = threading.Thread(target=self.continuous_worker, 
                                                args=(on_time, off_time))
            self.cycle_thread.start()
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayı değerleri girin!")
            
    def stop_cycle(self):
        if self.cycle_thread and self.cycle_thread.is_alive():
            self.controller.stop_event.set()
            self.log_message("Test durduruldu")
            self.controller.output_off()
            self.output_btn.configure(text="Çıkış: KAPALI", bg='#ffcccc')
            
    def cycle_worker(self, on_time, off_time, cycles):
        self.log_message(f"Test döngüsü başladı: {cycles} döngü, {on_time}s açık, {off_time}s kapalı")
        
        for cycle in range(cycles):
            if self.controller.stop_event.is_set():
                break
                
            self.log_message(f"Döngü {cycle + 1}/{cycles}")
            
            # Çıkışı aç
            self.controller.output_on()
            self.root.after(0, lambda: self.output_btn.configure(text="Çıkış: AÇIK", bg='#ccffcc'))
            
            # Açık kalma süresi
            for i in range(int(on_time * 10)):
                if self.controller.stop_event.is_set():
                    break
                time.sleep(0.1)
                
            if self.controller.stop_event.is_set():
                break
                
            # Çıkışı kapat
            self.controller.output_off()
            self.root.after(0, lambda: self.output_btn.configure(text="Çıkış: KAPALI", bg='#ffcccc'))
            
            # Kapalı kalma süresi (son döngü değilse)
            if cycle < cycles - 1:
                for i in range(int(off_time * 10)):
                    if self.controller.stop_event.is_set():
                        break
                    time.sleep(0.1)
                    
        self.log_message("Test döngüsü tamamlandı")
        
    def continuous_worker(self, on_time, off_time):
        self.log_message("Sürekli test başladı (Durdur butonuna basın)")
        
        cycle = 0
        while not self.controller.stop_event.is_set():
            cycle += 1
            self.log_message(f"Sürekli test döngüsü {cycle}")
            
            # Çıkışı aç
            self.controller.output_on()
            self.root.after(0, lambda: self.output_btn.configure(text="Çıkış: AÇIK", bg='#ccffcc'))
            
            # Açık kalma süresi
            for i in range(int(on_time * 10)):
                if self.controller.stop_event.is_set():
                    break
                time.sleep(0.1)
                
            if self.controller.stop_event.is_set():
                break
                
            # Çıkışı kapat
            self.controller.output_off()
            self.root.after(0, lambda: self.output_btn.configure(text="Çıkış: KAPALI", bg='#ffcccc'))
            
            # Kapalı kalma süresi
            for i in range(int(off_time * 10)):
                if self.controller.stop_event.is_set():
                    break
                time.sleep(0.1)
                
        self.log_message("Sürekli test durduruldu")
        
    def on_closing(self):
        if self.cycle_thread and self.cycle_thread.is_alive():
            self.controller.stop_event.set()
            self.cycle_thread.join(timeout=2)
            
        self.controller.disconnect()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AvionicsChromaGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
