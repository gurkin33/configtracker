import json
import smtplib
import ssl
from concurrent.futures import ThreadPoolExecutor
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from api.config import GlobalConfig
from configtracker import Decrypter


class MailService:

    SETTINGS_FILE = f"{GlobalConfig.SETTINGS_DIR}/smtp.json"
    LOGO_IMAGE = f"{GlobalConfig.TEMPLATES_DIR}/logo.png"

    def __init__(self):
        self.settings = {}
        self.params = {
            "title": "",
            "preheader": "",
            "base_body_class": ""
        }
        self.subject = 'Config-tracker'
        self.template = 'hello.html'
        self.template_txt = ""
        if not path.isfile(self.SETTINGS_FILE):
            raise Exception("SMTP Config not found")
        else:
            try:
                with open(self.SETTINGS_FILE, 'r') as settings:
                    self.settings = json.load(settings)
            except:
                raise Exception("Cannot read SMTP config file")

        self.params["base_url"] = self.settings["base_url"]

    def set_subject(self, subject: str):
        self.subject = subject
        return self

    def set_title(self, title: str):
        self.params['title'] = title
        return self

    def set_parameter(self, param_name: str, param_value):
        self.params[param_name] = param_value
        return self

    def add_parameters(self, params: dict):
        self.params = {**self.params, **params}
        return self

    def set_template(self, template: str):
        self.template = template
        return self

    # def set_template_txt(self, template_txt: str):
    #     env = Environment(
    #         loader=FileSystemLoader(f"{TEMPLATES_DIR}/mails"),
    #         autoescape=select_autoescape(['html', 'xml'])
    #     )
    #
    #     template = env.get_template(template_txt)
    #     self.template_txt = template.render(self.params)
    #     return self

    @classmethod
    def send_reports(cls, notifications, repos):
        # print(notifications)
        with ThreadPoolExecutor(20, thread_name_prefix="thread_id") as executor:
            for email in notifications['emails'].keys():
                # print(email)
                executor.submit(cls._send_reports, email, notifications, repos)
    @classmethod
    def _send_reports(cls, email, notifications, repos):
        ms = cls()
        ms.set_parameter('configs', notifications['configs'])
        ms.set_parameter('repos', repos)
        ms.set_template('report.html').set_subject(f'ConfigTracker - Report ')
        ms.set_parameter('user_configs', notifications['emails'][email])
        ms.send(email)

    def send(self, emails):
        _emails = ", ".join(emails) if isinstance(emails, list) else emails
        context = ssl._create_unverified_context()

        if self.settings['secure'] == 'ssl':
            server = smtplib.SMTP_SSL(self.settings['server'], self.settings['port'], context=context, timeout=30)
            # server.login(self.settings['username'], self.settings['password'])
        elif self.settings['secure'] == 'tls':
            server = smtplib.SMTP(self.settings['server'], self.settings['port'], timeout=30)
            server.starttls(context=context)  # Secure the connection
            # server.login(self.settings['username'], self.settings['password'])
        else:
            server = smtplib.SMTP(self.settings['server'], self.settings['port'], timeout=30)

        if self.settings['auth']:
            server.login(self.settings['username'], Decrypter.run(self.settings['password']))

        message = MIMEMultipart("mixed")  # sending TEXT and attachments
        # message = MIMEMultipart("alternative") # sending HTML and TEXT
        # more info about multipart:
        # https://stackoverflow.com/questions/3902455/mail-multipart-alternative-vs-multipart-mixed

        message["Subject"] = self.subject
        message["From"] = self.settings['from']
        message["To"] = _emails

        # source:
        # https://docs.aws.amazon.com/ses/latest/dg/send-email-raw.html
        message_body = MIMEMultipart('alternative')

        # Create the plain-text and HTML version of your message
        # text = self.template_txt
        # try:
        env = Environment(
            loader=FileSystemLoader(f"{GlobalConfig.TEMPLATES_DIR}/mails"),
            autoescape=select_autoescape(['html', 'xml'])
        )

        self.set_parameter('logo_id', "logo.png")

        template = env.get_template(self.template)
        html = template.render(self.params)
        # except Exception as e:
        #     # print(f'Mail template error - {e}')
        #     return

        # Turn these into plain/html MIMEText objects
        # part1 = MIMEText(text, "plain")  # disabled! because we use multipart/mixed
        part2 = MIMEText(html, "html", "utf-8")

        # Attach Image
        fp = open(self.LOGO_IMAGE, 'rb')  # Read image
        msg_image = MIMEImage(fp.read())
        fp.close()

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        # message.attach(part1)  # disabled! because we use multipart/mixed
        message_body.attach(part2)

        # Define the image's ID as referenced above
        msg_image.add_header('Content-ID', f"<{self.params['logo_id']}>")
        msg_image.add_header('Content-Disposition', f"attachment; filename={self.params['logo_id']}")
        message.attach(message_body)
        message.attach(msg_image)

        server.sendmail(self.settings['from'], _emails, message.as_string())
        return
