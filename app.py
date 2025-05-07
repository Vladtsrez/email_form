from flask import Flask, request, render_template, redirect
from flask_mail import Mail, Message
import sqlite3
import os

app = Flask(__name__)

# Настройки почты (используем Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tsvihuneditingcorp@gmail.com'        # <-- Вставь сюда свой Gmail
app.config['MAIL_PASSWORD'] = 'ybzn euin cuix gorb'      # <-- Gmail App Password, не обычный пароль

mail = Mail(app)

# Создаём базу данных, если нет
def init_db():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_email():
    user_email = request.form['email']

    # Сохраняем email в базу
    try:
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO subscribers (email) VALUES (?)', (user_email,))
        conn.commit()
        conn.close()
    except Exception as e:
        return render_template('index.html', message=f"Ошибка при сохранении email: {str(e)}")

    # Отправляем письмо с PDF
    try:
        msg = Message('Ваш PDF файл', sender=app.config['MAIL_USERNAME'], recipients=[user_email])
        msg.body = 'Спасибо за интерес! Во вложении находится PDF файл.'
        with app.open_resource("offer.pdf") as fp:
            msg.attach("offer.pdf", "application/pdf", fp.read())
        mail.send(msg)
        return render_template('index.html', message="Email sent!")
    except Exception as e:
        return render_template('index.html', message=f"Error while sending Email, please try again: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)