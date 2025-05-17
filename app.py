from flask import Flask, request, render_template
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ==== Почта (Gmail) ====
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
mail = Mail(app)

# ==== База данных Postgres ====
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:MaUPwxkGJJifakxsAwFtXybpUewshLzL@hopper.proxy.rlwy.net:14442/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==== Модель для хранения email ====
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

# ==== Создаём таблицу при запуске ====
with app.app_context():
    db.create_all()

# ==== Главная страница ====
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# ==== Обработка формы и отправка письма ====
@app.route('/send', methods=['POST'])
def send_email():
    user_email = request.form['email']

    # Сохраняем email в базу PostgreSQL
    try:
        new_subscriber = Subscriber(email=user_email)
        db.session.add(new_subscriber)
        db.session.commit()
    except Exception as e:
        return render_template('index.html', message=f"Error saving email: {str(e)}")

    # Отправляем письмо с PDF
    try:
        msg = Message('Your PDF file', sender=app.config['MAIL_USERNAME'], recipients=[user_email])
        msg.body = 'Thank you for your interest! Attached is a PDF file.'
        with app.open_resource("Where Emotion Meets Cinema.pdf") as fp:
            msg.attach("Where Emotion Meets Cinema.pdf", "application/pdf", fp.read())
        mail.send(msg)
        return render_template('index.html', message="Email sent successfully!")
    except Exception as e:
        return render_template('index.html', message=f"Error sending email: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)