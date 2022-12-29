import os
from typing import Union
from datetime import timedelta
from django.utils.timezone import localtime, now

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import base64
import os

from pathlib import Path
from sendgrid import (Attachment, FileContent, FileName, FileType, Disposition)


# def sendgrid_send_mail(from_e, to_e, subj, cont):
#     sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
#     from_email = from_e
#     to_email = to_e
#     subject = subj
#     content = cont
#     mail = Mail(from_email, to_email, subject, content)
#     sg.client.mail.send.post(request_body=mail.get())


def file_attachment(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
            filename = Path(file_path).stem
        encoded_file = base64.b64encode(data).decode()
        attached_file = Attachment(
            FileContent(encoded_file),
            FileName(filename),
            FileType('application/vnd.ms-excel'),
            Disposition('attachment')
        )
        return attached_file


class SendMail:
    _default_subject = 'HRGroup'

    def __init__(self, from_e: str, to_es: [list, str], text: str, files: Union[list, tuple, set] = None):

        self.from_email = from_e
        self.to_emails = to_es
        self.files = files
        self.text = text

    def send(self):
        message = Mail(
            from_email=self.from_email,
            to_emails=self.to_emails,
            subject=self._default_subject + str(localtime(now() - timedelta(days=1)).date()),
            html_content=f'<strong>{self.text}</strong>',
            is_multiple=True
        )
        if self.files:
            message.attachment = [
                file_attachment(f_path) for f_path in self.files if f_path and file_attachment(f_path)
            ]
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        sg.send(message)



# SendMail(from_e='info@hrgroup.kg', to_es='m.ysakov.jcc@gmail.com', text='Hello world!').send()


