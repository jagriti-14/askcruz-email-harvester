import os
import imaplib
import email
from email.header import decode_header

HOST = os.environ["MAILCOW_HOST"]
PORT = int(os.environ.get("MAILCOW_PORT", 993))
USERNAME = os.environ["MAILCOW_USERNAME"]
PASSWORD = os.environ["MAILCOW_PASSWORD"]


def decode_str(value):
    if value is None:
        return ""
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="replace")
    return decoded


def extract_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in disposition:
                return part.get_payload(decode=True).decode(errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                return part.get_payload(decode=True).decode(errors="replace")
        return ""
    else:
        return msg.get_payload(decode=True).decode(errors="replace")


def fetch_all_emails():
    mail = imaplib.IMAP4_SSL(HOST, PORT)
    mail.login(USERNAME, PASSWORD)
    mail.select("INBOX")

    status, data = mail.search(None, "ALL")
    message_nums = data[0].split()
    print(f"Found {len(message_nums)} messages.\n")

    for num in message_nums:
        status, msg_data = mail.fetch(num, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        from_addr = decode_str(msg["From"])
        subject = decode_str(msg["Subject"])
        date = msg["Date"]
        body = extract_body(msg)

        print("=" * 60)
        print(f"From:    {from_addr}")
        print(f"Subject: {subject}")
        print(f"Date:    {date}")
        print(f"Body (first 200 chars):\n{body[:200]}")
        print()

    mail.logout()


if __name__ == "__main__":
    fetch_all_emails()