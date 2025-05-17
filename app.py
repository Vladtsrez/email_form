from flask import Flask, request, render_template
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
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

    # Сохраняем email в базу
    try:
        new_subscriber = Subscriber(email=user_email)
        db.session.add(new_subscriber)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return render_template('index.html', message="This email is already subscribed.")
    except Exception as e:
        return render_template('index.html', message=f"Error saving email: {str(e)}")

    # Отправляем email с PDF, баннером и соц.сетями
    try:
        msg = Message('Thank You for Subscribing!', sender=app.config['MAIL_USERNAME'], recipients=[user_email])

        # HTML письмо
        html_body = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 0; margin: 0;">
              <div style="max-width: 600px; margin: 30px auto; background: white; padding: 20px; border-radius: 10px; border: 1px solid #eee;">
              <img src="cid:banner" alt="Banner" style="width: 100%; border-radius: 10px;">
                    <h2 style="color: #164243; text-align: center; margin-top: 30px;">Welcome to Evolve Inspiration!</h2>
                    <p style="font-size: 16px;">Thank you for subscribing. Please find your PDF file attached to this email.</p>

                    <div style="text-align: center; margin: 30px 0;">
                      <a href="#" style="background-color: #164243; color: white; padding: 12px 25px; border-radius: 6px; text-decoration: none; font-weight: bold;">Download PDF</a>
                    </div>

                    <p>If you have any questions, feel free to reply to this message. We’re happy to help!</p>

                    <hr style="margin: 30px 0;">

                    <p style="font-size: 16px;">Follow us on social media:</p>
                    <p>
                      <a href="https://www.instagram.com/evolve.ins" target="_blank" style="margin-right: 15px;">
                        <img src="cid:instagram" alt="Instagram">
                      </a>
                      <a href="https://www.youtube.com/@evolveinsp" target="_blank" style="margin-right: 15px;">
                        <img src="cid:youtube" alt="YouTube">
                      </a>
                      <a href="https://www.tiktok.com/@evolve.in" target="_blank">
                        <img src="https://cdn-icons-png.flaticon.com/24/3046/3046122.png" alt="TikTok">
                      </a>
                    </p>
                    <br>
                    <p style="font-size: 13px; color: #888;">Best regards,<br>The Evolve Inspiration Team</p>
                </div>
            </body>
        </html>
        """

        msg.html = html_body

        # Прикрепляем PDF
        with app.open_resource("Where Emotion Meets Cinema.pdf") as fp:
            msg.attach("Where Emotion Meets Cinema.pdf", "application/pdf", fp.read())

        # Встраиваем баннер
        with app.open_resource("static/Header-YT-2@3x.png") as img:
            msg.attach("banner", "image/jpeg", img.read(), 'inline', headers={'Content-ID': '<banner>'})

        # Встраиваем Instagram иконку
        with app.open_resource("static/img/Instagram-icon.png") as img:
            msg.attach("instagram", "image/png", img.read(), 'inline', headers={'Content-ID': '<instagram>'})

        # Встраиваем YouTube иконку
        with app.open_resource("static/img/youtube.svg") as img:
            msg.attach("youtube", "image/svg+xml", img.read(), 'inline', headers={'Content-ID': '<youtube>'})

        mail.send(msg)
        return render_template('index.html', message="Email successfully sent!")
    except Exception as e:
        return render_template('index.html', message=f"Error sending email: {str(e)}")
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)