from concurrent.futures import ThreadPoolExecutor, as_completed
import cairosvg
import csv
from flask import Flask
from flask_mail import Mail, Message
import os

from dotenv import load_dotenv
load_dotenv('.env')

app = Flask(__name__)

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
        print("[{}] Worker Thread started".format(email))
        cairosvg.svg2pdf(bytestring=template.to_str({"name":name}), write_to="./out/cert_{}.pdf".format(email))
        print("[{}] Finished generating certificate".format(email))

        # todo: Figure out how to send email
        # send email to user
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

        return email

@app.route('/', methods=['GET', 'POST'])
def index():
    
    temp = Template('./template/android.svg')
    list_file = open('list.csv', 'r')
    list_reader = csv.reader(list_file)
    next(list_reader) # header
    
    futures = set()

    with ThreadPoolExecutor(max_workers = 5) as executor:
        for line in list_reader:
            name = line[0].strip()
            email = line[1].strip()
            futures.add(executor.submit(export_and_send, temp, name, email))
        for future in as_completed(futures):
            print("[main] Finished sending email to {}".format(future.result()))
    list_file.close()

    return "Messages Sent"


if __name__ == "__main__":
    app.run(debug=True)


    
