#tasks.py

# from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
# Add this to your task
from django.core.mail import get_connection

# @shared_task(bind=True)
def send_notification_mail(target_mail):
    mail_subject = "Your order is confirmed!"
    message = "Thank You for Buying Products from Daily Shopping!"
    try:
        send_mail(
            subject=mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=target_mail if isinstance(target_mail, list) else [target_mail],
            fail_silently=False,
        )
        print("Sent mail successfully!!")
        return "Done"
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise
