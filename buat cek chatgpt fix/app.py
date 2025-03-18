import os
# Matikan warning SQLAlchemy
os.environ['SQLALCHEMY_WARN_20'] = '0'
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.models import db, User, ChatHistory, Prompt, Response
from app import login_manager
import pymysql
import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/chatgpt_scraper'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching during development

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def initialize_database():
    """Inisialisasi database dengan aman"""
    try:
        # Nonaktifkan foreign key checks
        db.session.execute('SET FOREIGN_KEY_CHECKS=0')
        
        # Drop tabel dalam urutan yang benar
        tables = ['responses', 'prompts', 'chat_histories', 'users']
        for table in tables:
            db.session.execute(f'DROP TABLE IF EXISTS {table}')
        
        # Aktifkan kembali foreign key checks
        db.session.execute('SET FOREIGN_KEY_CHECKS=1')
        
        # Buat ulang semua tabel
        db.create_all()
        db.session.commit()
        print("Database berhasil diinisialisasi!")
        
    except Exception as e:
        print(f"Error saat inisialisasi database: {e}")
        db.session.rollback()
        raise

def setup_driver():
    """Setup Chrome WebDriver dengan konfigurasi yang lebih baik"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Tambahan untuk menghindari deteksi
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver

# Function scraping dengan Selenium dan WebDriverWait
def scrape_chatgpt(url):
    # Setup driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    # Tambahkan preferences untuk menghindari deteksi bot
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Gunakan Chrome tanpa webdriver-manager
    driver = webdriver.Chrome(options=options)
    
    try:
        # Jika URL menggunakan format /c/, ubah ke format yang benar
        if '/c/' in url:
            # Hapus trailing slash jika ada
            url = url.rstrip('/')
            # Ambil conversation ID
            conv_id = url.split('/c/')[-1]
            # Gunakan format URL yang benar
            url = f"https://chat.openai.com/c/{conv_id}"
        
        print(f"Mengakses URL: {url}")  # Debug print
        driver.get(url)
        
        # Tunggu loading selesai
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Tambahkan delay
        time.sleep(5)
        
        # Debug: ambil screenshot
        driver.save_screenshot("page_loaded.png")
        
        # Print page source untuk debugging
        print("Page source:", driver.page_source[:500])  # Print 500 karakter pertama
        
        chatgpt = []
        
        # Coba berbagai selector
        selectors = [
            {
                'prompt': "div[data-message-author-role='user']",
                'response': "div[data-message-author-role='assistant']"
            },
            {
                'prompt': ".text-base",
                'response': ".markdown"
            },
            {
                'prompt': ".whitespace-pre-wrap",
                'response': ".markdown"
            },
            {
                'prompt': "div.text-message-content",
                'response': "div.response-content"
            }
        ]
        
        success = False
        for selector in selectors:
            try:
                print(f"Mencoba selector: {selector}")  # Debug print
                
                # Scroll ke bawah untuk memuat semua konten
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Tunggu setelah scroll
                
                prompt_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector['prompt']))
                )
                response_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector['response']))
                )
                
                print(f"Ditemukan {len(prompt_elements)} prompt dan {len(response_elements)} response")  # Debug print
                
                if prompt_elements and response_elements:
                    prompts = [el.text.strip() for el in prompt_elements if el.text.strip()]
                    responses = [el.text.strip() for el in response_elements if el.text.strip()]
                    
                    if prompts and responses:
                        success = True
                        for i in range(min(len(prompts), len(responses))):
                            chatgpt.append({
                                'prompt': prompts[i],
                                'response': responses[i]
                            })
                        break
            
            except Exception as e:
                print(f"Error dengan selector {selector}: {str(e)}")  # Debug print
                continue
        
        if not success:
            raise Exception("Tidak dapat menemukan elemen chat dengan semua selector yang dicoba")
        
        if not chatgpt:
            raise Exception("Berhasil menemukan elemen tetapi tidak ada data yang bisa diambil")

    except Exception as e:
        print(f"Error utama: {str(e)}")  # Debug print
        driver.save_screenshot("error_final.png")
        raise

    finally:
        driver.quit()

    return chatgpt

def save_to_txt(chatgpt, file_path='output.txt'):
    """Simpan data prompt dan respons ke file teks tanpa format poin-poin."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for i, chat in enumerate(chatgpt):
                file.write(f"Prompt {i + 1}:\n{chat['prompt']}\n\n")
                file.write(f"Response {i + 1}:\n{chat['response']}\n\n")
        print(f"Data berhasil disimpan ke {file_path}")
    except Exception as e:
        print(f"Error saat menyimpan ke file: {e}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validasi input tidak boleh kosong
        if not username or not password:
            flash('Username dan password harus diisi!', 'error')
            return redirect(url_for('login'))
            
        user = User.query.filter_by(username=username).first()
        
        # Cek apakah username ada
        if not user:
            flash('Username tidak terdaftar dalam sistem', 'error')
            return redirect(url_for('login'))
        
        # Jika username ada, cek passwordnya
        if user.check_password(password):
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Password yang Anda masukkan salah', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"Mencoba registrasi user: {username}")  # Debug log
            
            # Validasi input
            if not username or not password:
                flash('Username dan password harus diisi!', 'error')
                return redirect(url_for('register'))
            
            # Cek username sudah ada atau belum
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username sudah digunakan', 'error')
                return redirect(url_for('register'))
            
            # Buat user baru dengan commit dalam blok try
            with db.session.begin_nested():
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
            
            # Commit final
            db.session.commit()
            print(f"User berhasil dibuat dengan id: {user.id}")  # Debug log
            
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Error saat registrasi: {str(e)}")  # Debug log
            db.session.rollback()
            flash('Terjadi kesalahan saat registrasi', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil logout', 'success')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        driver = None
        try:
            # Validasi URL
            if not url:
                flash('URL tidak boleh kosong!', 'danger')
                return redirect(url_for('index'))
            
            # Ubah URL ke format yang benar
            if 'chatgpt.com/share/' in url:
                # Ambil ID dari URL
                share_id = url.split('/share/')[-1].strip()
                # Buat URL baru
                url = f"https://chat.openai.com/share/{share_id}"
            
            print(f"Mencoba mengakses: {url}")  # Debug log
            
            # Setup dan jalankan scraping
            driver = setup_driver()
            driver.get(url)
            
            # Tunggu dan ambil elemen dengan selector yang lebih spesifik
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-message-author-role='user']"))
            )
            
            # Scroll untuk memuat semua konten
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Ambil prompt dan response dengan selector yang lebih tepat
            prompts = driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='user']")
            responses = driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
            
            if not prompts or not responses:
                driver.quit()
                flash('Tidak dapat menemukan percakapan di URL tersebut.', 'danger')
                return redirect(url_for('index'))

            # Simpan ke database
            chat_history = ChatHistory(
                user_id=current_user.id,
                url=url
            )
            db.session.add(chat_history)
            db.session.flush()

            # Bersihkan teks respons agar hanya berupa paragraf
            def clean_response_text(text):
                """Membersihkan dan memformat teks respons."""
                import re
                
                # Hapus spasi berlebih di awal dan akhir
                text = text.strip()
                
                # Split teks menjadi baris-baris
                lines = text.split('\n')
                formatted_lines = []
                
                for line in lines:
                    # Hapus semua whitespace di awal dan akhir
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Cek apakah baris adalah item list dengan angka
                    if re.match(r'^[\d]+[\.\)]', line):
                        # Hapus indentasi tambahan setelah angka
                        line = re.sub(r'^(\d+[\.\)])\s+', r'\1 ', line)
                        formatted_lines.append(line)
                    # Cek apakah baris dimulai dengan bullet point
                    elif re.match(r'^\-|\*|•', line):
                        # Hapus indentasi tambahan setelah bullet point
                        line = re.sub(r'^[\-\*•]\s+', '• ', line)
                        formatted_lines.append(line)
                    # Cek apakah baris adalah judul/kategori
                    elif ':' in line and len(line.split(':')[0].strip()) <= 30:
                        formatted_lines.append(line)
                    # Cek apakah baris dimulai dengan kata kunci list
                    elif any(line.lower().startswith(word) for word in ['pertama', 'kedua', 'ketiga', 'keempat', 'kelima',
                                                                          'langkah', 'tahap', 'bagian', 'point', 'poin']):
                        formatted_lines.append("• " + line)
                    # Baris normal tanpa indentasi
                    else:
                        # Hapus semua indentasi dan spasi berlebih
                        line = ' '.join(line.split())
                        formatted_lines.append(line)
                
                # Gabungkan baris-baris dengan single newline
                return '\n'.join(formatted_lines)

            # Modifikasi bagian scraping untuk membersihkan teks
            for prompt_elem, response_elem in zip(prompts, responses):
                prompt_text = clean_response_text(prompt_elem.text.strip())
                response_text = clean_response_text(response_elem.text.strip())
                
                if prompt_text and response_text:
                    prompt = Prompt(text=prompt_text, chat_id=chat_history.id)
                    db.session.add(prompt)
                    db.session.flush()
                    
                    response = Response(text=response_text, prompt_id=prompt.id)
                    db.session.add(response)

            db.session.commit()
            driver.quit()

            flash('Data berhasil disimpan!', 'success')
            return redirect(url_for('history_detail', chat_id=chat_history.id))

        except Exception as e:
            if driver:
                driver.quit()
            db.session.rollback()
            flash(f'Error saat scraping: {str(e)}', 'danger')
            return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/history')
@login_required
def history():
    chats = ChatHistory.query\
        .filter_by(user_id=current_user.id)\
        .order_by(ChatHistory.created_at.desc())\
        .all()
    
    # Ambil chat pertama sebagai default jika ada
    selected_chat = chats[0] if chats else None
    
    return render_template('history.html', 
                         chats=chats,
                         selected_chat=selected_chat)  # Tambahkan selected_chat ke context

@app.route('/history/<int:chat_id>')
@login_required
def history_detail(chat_id):
    # Ambil chat yang dipilih dan semua chat history
    selected_chat = ChatHistory.query.filter_by(
        id=chat_id, 
        user_id=current_user.id
    ).first_or_404()
    
    chats = ChatHistory.query.filter_by(user_id=current_user.id)\
        .order_by(ChatHistory.created_at.desc())\
        .all()
    
    return render_template('history.html', 
                         selected_chat=selected_chat, 
                         chats=chats)

@app.route('/history/<int:chat_id>/text')
@login_required
def history_text(chat_id):
    try:
        chat = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
        
        def clean_text(text):
            """Membersihkan teks dari emoji, tanda baca, dan karakter khusus"""
            import re
            
            # Pattern untuk emoji
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # simbol & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # bendera (iOS)
                u"\U00002702-\U000027B0"  # Dingbats
                u"\U000024C2-\U0001F251" 
                u"\U0001f926-\U0001f937"
                u"\U00010000-\U0010ffff"
                u"\u2600-\u26FF"          # simbol miscellaneous
                u"\u2700-\u27BF"          # Dingbats
                u"\u2B50"                 # bintang
                u"\u200d"                 # zero width joiner
                u"\u200b"                 # zero width space
                u"]+", flags=re.UNICODE)
            
            # Hapus emoji
            text = emoji_pattern.sub('', text)
            
            # Hapus semua karakter khusus dan tanda baca
            text = re.sub(r'[^\w\s]', ' ', text)
            
            # Hapus spasi berlebih
            text = ' '.join(text.split())
            
            return text
        
        # Format teks
        text_parts = []
        
        for i, prompt in enumerate(chat.prompts, 1):
            # Format prompt dengan huruf kecil dan hapus karakter khusus
            prompt_text = prompt.text.strip().lower()
            prompt_text = clean_text(prompt_text)
            text_parts.append(f"prompt {i}")  # Hapus tanda #
            text_parts.append(prompt_text)
            text_parts.append("")  # Baris kosong
            
            # Format response dengan huruf kecil dan hapus karakter khusus
            if prompt.responses and prompt.responses[0]:
                response_text = prompt.responses[0].text.strip().lower()
                
                # Split menjadi baris-baris
                lines = response_text.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    # Bersihkan setiap baris
                    line = clean_text(line)
                    
                    if line:  # Hanya tambahkan baris yang tidak kosong
                        cleaned_lines.append(line)
                
                # Gabungkan kembali dengan newline
                response_text = '\n'.join(cleaned_lines)
                
                text_parts.append(f"response {i}")  # Hapus tanda #
                text_parts.append(response_text)
                text_parts.append("")  # Baris kosong
                text_parts.append("")  # Tambahan baris kosong antara setiap set prompt-response
        
        # Gabungkan semua teks
        final_text = '\n'.join(text_parts)
        
        # Buat response dengan tipe konten text/plain
        response = app.make_response(final_text)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        return response
        
    except Exception as e:
        print(f"Error in history_text: {str(e)}")
        return "Error: Tidak dapat mengambil teks chat", 500

@app.route('/save-chat', methods=['POST'])
@login_required
def save_chat():
    chat_id = request.form.get('chat_id')
    if not chat_id:
        flash('Chat ID tidak ditemukan!', 'danger')
        return redirect(url_for('history'))

    # Ambil data chat dari database
    chat_history = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    prompts = Prompt.query.filter_by(chat_id=chat_id).all()
    responses = Response.query.join(Prompt).filter(Prompt.chat_id == chat_id).all()

    # Format data sebagai list of dict
    chatgpt = [{'prompt': p.text, 'response': r.text} for p, r in zip(prompts, responses)]

    # Simpan ke file
    save_to_txt(chatgpt, file_path=f"chat_{chat_id}.txt")

    flash('Data berhasil disimpan ke file!', 'success')
    return redirect(url_for('history_detail', chat_id=chat_id))

@app.route('/change-theme', methods=['POST'])
@login_required
def change_theme():
    theme = request.form.get('theme', 'light')
    if theme in ['light', 'dark']:
        current_user.theme_preference = theme
        db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        try:
            # Cek koneksi database
            db.session.execute(text('SELECT 1'))
        except Exception as e:
            print("Membuat database dan tabel...")
            # Nonaktifkan foreign key checks
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=0'))
            
            # Buat tabel dalam urutan yang benar
            db.session.execute(text('DROP TABLE IF EXISTS responses'))
            db.session.execute(text('DROP TABLE IF EXISTS prompts'))
            db.session.execute(text('DROP TABLE IF EXISTS chat_histories'))
            db.session.execute(text('DROP TABLE IF EXISTS users'))
            
            # Aktifkan kembali foreign key checks
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=1'))
            
            # Buat semua tabel
            db.create_all()
            print("Database dan tabel berhasil dibuat!")
    
    app.run(debug=True, host='0.0.0.0', port=5001)