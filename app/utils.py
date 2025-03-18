from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def get_chrome_version():
    """Mendapatkan versi Chrome dari registry Windows"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        return version
    except:
        return None

def setup_driver():
    try:
        print("Menginisialisasi Chrome Driver...")
        
        # Konfigurasi Chrome Options yang lebih sederhana
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Cek versi Chrome
        chrome_version = get_chrome_version()
        if chrome_version:
            print(f"Terdeteksi Chrome versi: {chrome_version}")
        
        # Gunakan chromedriver dari folder project
        driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
        print(f"Menggunakan ChromeDriver dari: {driver_path}")
        
        if not os.path.exists(driver_path):
            raise Exception(f"ChromeDriver tidak ditemukan di: {driver_path}")
            
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print("Chrome Driver berhasil diinisialisasi!")
        return driver
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error saat inisialisasi driver: {error_msg}")
        print("\nSaran troubleshooting:")
        print("1. Pastikan chromedriver.exe ada di folder yang sama dengan app.py")
        print(f"2. Versi Chrome Anda: {get_chrome_version() or 'Tidak terdeteksi'}")
        print("3. Pastikan versi ChromeDriver sesuai dengan versi Chrome")
        raise Exception("Gagal menginisialisasi Chrome Driver. Lihat pesan error di atas.")

def scrape_chatgpt(url):
    driver = None
    try:
        driver = setup_driver()
        print(f"Memulai scraping dari URL: {url}")
        driver.get(url)
        
        # Tunggu hingga halaman dimuat
        print("Menunggu halaman dimuat...")
        wait = WebDriverWait(driver, 20)
        
        # Coba beberapa selector yang berbeda untuk ChatGPT
        selectors = [
            ".markdown",  # Selector untuk konten markdown
            ".text-base",  # Selector untuk teks dasar
            "[data-message-author-role]",  # Selector berdasarkan peran author
            ".message-content"  # Selector untuk konten pesan
        ]
        
        messages = []
        for selector in selectors:
            try:
                print(f"Mencoba selector: {selector}")
                elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                if elements:
                    messages = elements
                    print(f"Berhasil menemukan {len(elements)} pesan dengan selector {selector}")
                    break
            except Exception as e:
                print(f"Selector {selector} tidak berhasil: {str(e)}")
                continue
        
        if not messages:
            raise Exception("Tidak dapat menemukan pesan chat dengan semua selector yang dicoba")
        
        # Siapkan struktur data untuk menyimpan hasil
        chat_data = {
            'messages': []
        }
        
        # Ekstrak teks dari setiap pesan
        for msg in messages:
            try:
                content = msg.text.strip()
                if content:  # Hanya tambahkan pesan yang tidak kosong
                    chat_data['messages'].append({
                        'content': content,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
            except Exception as e:
                print(f"Error saat mengekstrak pesan: {str(e)}")
                continue
            
        print(f"Berhasil mengambil {len(chat_data['messages'])} pesan")
        return chat_data
        
    except Exception as e:
        print(f"Error saat scraping: {str(e)}")
        raise e
    finally:
        if driver:
            print("Menutup browser...")
            try:
                driver.quit()
            except:
                pass 