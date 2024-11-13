import os
from dotenv import load_dotenv
import imaplib
import email
from bs4 import BeautifulSoup
import requests

load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

# connect to email
def connect_to_email():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")
    return mail

# find all unsubscribe links from html content
def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    links = [link["href"] for link in soup.find_all("a", href=True) if "unsubscribe" in link["href"].lower()]
    return links

# clicking each link
def click_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            print(f"Successfully clicked link: {link}")
        else:
            print(f"Failed to click link: {link}\n Error code: {response.status_code}")
    except Exception as e:
        print(f"Error with {link}\n Error: {str(e)}")


# search through mail for emails that contain the text unsubscribe
def search_for_email():
    mail = connect_to_email()
    _, search_data = mail.search(None, '(BODY "unsubscribe")')
    data = search_data[0].split()

    links = []

    for num in data:
        _, data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    links.extend(extract_links_from_html(html_content))
        else:
            content_type = msg.get_content_type()
            content = msg.get_payload(decode=True).decode()

            if content_type == "text/html":
                links.extend(extract_links_from_html(content))

    mail.logout()
    return links

# save links to a file
def save_links(links):
    with open("links.txt", "w") as f:
        f.write("\n".join(links))

links = search_for_email()
for link in links:
    click_link(link)

save_links(links)