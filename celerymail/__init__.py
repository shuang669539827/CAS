from .tasks import send_html_mail_task, send_msg


def send_html_mail(subject, html_content, recipient_list, filepath=None):
    return send_html_mail_task.delay(subject, html_content, recipient_list, filepath=filepath)
