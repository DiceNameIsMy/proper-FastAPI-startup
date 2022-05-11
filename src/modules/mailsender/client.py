from abc import ABC, abstractmethod

import ssl
import smtplib


class ABCMailSender(ABC):
    def __init__(self, smtp_server: str, smtp_port: int, address: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.address = address
        self.password = password

    @abstractmethod
    def send(self, recipient_email: str, subject: str, body: str) -> None:
        pass


class MailSenderClient(ABCMailSender):
    def send(self, recipient_email: str, subject: str, body: str) -> None:
        context = ssl.create_default_context()
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls(context=context)
        server.login(self.address, self.password)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(self.address, recipient_email, message)


class FakeMailSender(ABCMailSender):
    def send(self, recipient_email: str, subject: str, body: str) -> None:
        pass


def new_mailsender(
    smtp_server: str, smtp_port: int, address: str, password: str, fake: bool = False
) -> ABCMailSender:
    if fake:
        return FakeMailSender(smtp_server, smtp_port, address, password)
    else:
        return MailSenderClient(smtp_server, smtp_port, address, password)
