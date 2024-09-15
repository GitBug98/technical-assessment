from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_borrowing_confirmation_email(user_email, book_title):
    send_mail(
        'Borrowing Confirmation',
        f'You have successfully borrowed {book_title}.',
        'library@example.com',
        [user_email],
        fail_silently=False,
    )

@shared_task
def send_borrowing_reminder_email(user_email, book_title, return_due_date):
    days_remaining = (return_due_date - timezone.now().date()).days
    if days_remaining <= 3:
        send_mail(
            'Borrowing Reminder',
            f'Reminder: Your book "{book_title}" is due for return in {days_remaining} days.',
            'library@example.com',
            [user_email],
            fail_silently=False,
        )
