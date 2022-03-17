import ssl
import smtplib
from typing import Protocol


class EmailServerProtocol(Protocol):
    def __init__(self, smtp_server: str, smtp_port: int, address: str, password: str):
        """"""

    def send_verification_code(self, email: str, code: int) -> None:
        """"""


class EmailServer:
    def __init__(self, smtp_server: str, smtp_port: int, address: str, password: str):
        self.is_logged_in = False
        self.email = address
        self.password = password
        self.context = ssl.create_default_context()
        self._server = smtplib.SMTP(smtp_server, smtp_port)
        self._server.starttls(context=self.context)

    @property
    def server(self):
        if not self.is_logged_in:
            self._server.login(self.email, self.password)
            self.is_logged_in = True
        return self._server

    def send_verification_code(self, email: str, code: int) -> None:
        subject = "Verify your email"
        body = f"Please verify your email by entering the following code: {code}"
        self._send_mail(email, subject, body)

    def _send_mail(self, email: str, subject: str, body: str):
        message = f"Subject: {subject}\n\n{body}"
        self.server.sendmail(self.email, email, message)


class FakeEmailServer:
    def __init__(self, smtp_server: str, smtp_port: int, address: str, password: str):
        pass

    def send_verification_code(self, email: str, code: int) -> None:
        pass
