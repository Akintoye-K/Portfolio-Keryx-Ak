from flask import Flask, render_template, request
import smtplib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer
import os
from dotenv import find_dotenv, load_dotenv

# ---------------------------- APP AND DATABASE SETUP ------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_INFO", "sqlite:///projects.db")
# initialize the app with the extension
db.init_app(app)

# --- Model ---
class Project(db.Model):
    __tablename__ = "Projects"

    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(VARCHAR(250), nullable=False, unique=True)
    technologies = mapped_column(VARCHAR(250), nullable=False)
    description = mapped_column(VARCHAR(250), nullable=False)
    img_url = mapped_column(VARCHAR(250), nullable=False)

# --- Create DB ---
with app.app_context():
    db.create_all()

def send_mail(f_name, l_name, email, message):
    my_email = os.getenv("MY_EMAIL")  # <---- Sending Email
    password = os.getenv("MY_PASSWORD")  # <---- Password for this particular app

    with smtplib.SMTP("smtp.gmail.com", 587) as connection:  # <---- Creating the SMTP connection
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(
            from_addr=my_email,  # <---- Sender Address
            to_addrs=os.getenv("TO_EMAIL"),  # <---- Receiver Address
            msg=f"Subject:Message from User 💬 \n\nFirst Name: {f_name} \nLast Name: {l_name} \nEmail: {email} \nMessage: {message}".encode("utf-8")# <---- Contents of the Email ('Subject' and 'Body') / Encodes text to contain emojis
        )

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        f_name = request.form["f-name"]
        l_name = request.form["l-name"]
        email = request.form["email"]
        message = request.form["message"]
        send_mail(f_name=f_name, l_name=l_name, email=email, message=message)
        return render_template("final-portfolio.html", submitted=True)
    return render_template("final-portfolio.html", submitted = False)

@app.route("/projects")
def projects():
    with app.app_context():
        result = db.session.execute(db.select(Project).order_by(Project.title))
        all_projects = result.scalars()
        return render_template("projects.html", projects=all_projects)

if __name__ == "__main__":
    app.run(debug=True, port=5001)