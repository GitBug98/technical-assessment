from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_message_email(email, message):
    subject, from_email, to = message, 'test@project.com', email
    text_content = 'This is an important message.'
    html_content = f'<h1></h1>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return True