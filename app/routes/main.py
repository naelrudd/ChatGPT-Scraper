from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, ChatHistory, Prompt, Response
from app.utils import setup_driver, scrape_chatgpt

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash('URL tidak boleh kosong!', 'danger')
            return redirect(url_for('main.index'))
            
        try:
            chat_data = scrape_chatgpt(url)
            # Simpan data...
            flash('Data berhasil disimpan!', 'success')
            return redirect(url_for('main.history'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            
    return render_template('index.html')

@bp.route('/history')
@login_required
def history():
    chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at.desc()).all()
    return render_template('history.html', chats=chats) 