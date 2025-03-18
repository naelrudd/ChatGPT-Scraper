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
            
            # Konversi URL jika menggunakan domain chatgpt.com
            if 'chatgpt.com/share/' in url:
                url = url.replace('chatgpt.com', 'chat.openai.com')
            
            # Validasi final
            if not ('chat.openai.com/share/' in url):
                flash('URL tidak valid! Gunakan format share URL yang benar dari chat.openai.com', 'danger')
                return redirect(url_for('index'))
            
            # Setup dan jalankan scraping
            driver = setup_driver()
            driver.get(url)
            
            # ... kode scraping ...

            # Simpan ke database dengan URL
            chat_history = ChatHistory(user_id=current_user.id, url=url)
            db.session.add(chat_history)
            db.session.flush()

            # ... kode lainnya ... 