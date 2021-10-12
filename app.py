from concurrent.futures import ThreadPoolExecutor

import cairosvg
import csv
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_mail import Mail, Message
import time
import os

from dotenv import load_dotenv
load_dotenv('.env')

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers = 10)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET')
sockio = SocketIO(app)

EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = EMAIL_USERNAME
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

class Template:
    def __init__(self, template_path):
        with open(template_path, 'r') as template_file:
            self.template_string = template_file.read()

    def to_str(self, data = {}):
        outstr = self.template_string
        for key in data:
            outstr = outstr.replace("[{}]".format(key), data[key])
        return outstr

def export_and_send(template, name, email):
    with app.app_context():
        time.sleep(1)
        sockio.emit("status", {"email": email, "status":"🟧 Running"})
        cairosvg.svg2pdf(bytestring=template.to_str({"name":name}), write_to="./out/cert_{}.pdf".format(email))
        print("[{}] Finished generating certificate".format(email))
        try:
            msg = Message(
                'Congratulations',
                sender=('GDSC JSSSTU', EMAIL_USERNAME),
                recipients=[email]
            )
            #msg.html = render_template('email.html')
            msg.body = 'Here is your certificate!'
            with app.open_resource("out/cert_{}.pdf".format(email)) as fp:
                msg.attach("out/cert_{}.pdf".format(email), 'application/pdf', fp.read())
            mail.send(msg)
            sockio.emit("status", {"email": email, "status":"🟩 Done"})
        except Exception as e:
            sockio.emit("status", {"email": email, "status":"🟥 Failed"})
            print(e)
        return email


@app.route('/', methods=['GET', 'POST'])
def index():
    temp = Template('./cert_template/android.svg')
    list_file = open('list.csv', 'r')
    list_reader = csv.reader(list_file)
    next(list_reader) # header
    
    name_email_list = []

    for line in list_reader:
        name = line[0].strip()
        email = line[1].strip()
        name_email_list.append({"name" : name, "email" : email})
        executor.submit(export_and_send, temp, name, email)
    list_file.close()
    return render_template("index.html", name_email = name_email_list)

if __name__ == "__main__":
    sockio.run(app, debug=True)


    
