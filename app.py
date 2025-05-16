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
        return render_template('index.html', message=f"Ошибка при сохранении email: {str(e)}")

    # Отправляем письмо с PDF
    try:
        msg = Message('Ваш PDF файл', sender=app.config['MAIL_USERNAME'], recipients=[user_email])
        msg.body = 'Спасибо за интерес! Во вложении находится PDF файл.'
        with app.open_resource("Where Emotion Meets Cinema.pdf") as fp:
            msg.attach("Where Emotion Meets Cinema.pdf", "application/pdf", fp.read())
        mail.send(msg)
        return render_template('index.html', message="Email успешно отправлен!")
    except Exception as e:
        return render_template('index.html', message=f"Ошибка при отправке письма: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)