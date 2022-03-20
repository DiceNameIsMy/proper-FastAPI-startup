import ssl
import smtplib


def send_mail(
    repcipient_email: str,
    subject: str,
    body: str,
    smtp_server: str,
    smtp_port: int,
    address: str,
    password: str,
    fake_send: bool,
) -> None:
    if fake_send:
        return
    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls(context=context)
    server.login(address, password)
    message = f"Subject: {subject}\n\n{body}"
    server.sendmail(address, repcipient_email, message)
