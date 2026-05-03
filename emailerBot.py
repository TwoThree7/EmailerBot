import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def scrape_indeed():
    print("Starting Chrome driver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        url = "https://uk.indeed.com/jobs?q=brickwork&l=leeds"
        print(f"Navigating to: {url}")
        driver.get(url)
        html = driver.page_source
        print("Page source acquired successfully.")
        return html
    finally:
        print("Closing Chrome driver.")
        driver.quit()


def extract_job_links(input_file, output_file):
    print(f"Reading {input_file} for processing...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, "html.parser")
        job_headers = soup.find_all("h2", class_=lambda x: x and "jobTitle" in x)
        print(f"Found {len(job_headers)} potential job headers.")
        extracted_elements = []
        for header in job_headers:
            link_tag = header.find("a")
            if link_tag:
                extracted_elements.append(str(link_tag))
        with open(output_file, "w", encoding="utf-8") as f:
            for item in extracted_elements:
                f.write(item + "\n\n")
        print(f"Extraction complete. {len(extracted_elements)} links written to {output_file}.")
    except Exception as e:
        print(f"Error during extraction: {e}")


def send_job_email(sender_email, sender_password, receiver_email, job_list_html):
    print(f"Preparing email for {receiver_email}...")
    msg = MIMEMultipart('alternative')
    msg['From'] = f"Job Notifier <{sender_email}>"
    msg['To'] = receiver_email
    msg['Subject'] = "Latest Brickwork Jobs in Leeds"

    job_items_html = ""
    soup = BeautifulSoup(job_list_html, "html.parser")
    links = soup.find_all("a")
    for link in links:
        title = link.get_text(strip=True)
        href = link.get('href', '#')
        if href.startswith('/'):
            href = f"https://uk.indeed.com{href}"

        job_items_html += f"""
        <div style="padding: 15px; margin-bottom: 10px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f9f9f9;">
            <h3 style="margin: 0 0 10px 0; color: #2d2d2d; font-family: Arial, sans-serif;">{title}</h3>
            <a href="{href}" style="background-color: #2557a7; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; font-weight: bold; font-family: Arial, sans-serif; display: inline-block;">View Job</a>
        </div>
        """

    full_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                <h2 style="color: #2557a7; border-bottom: 2px solid #2557a7; padding-bottom: 10px;">New Job Matches</h2>
                <p>Hello, we found the following roles for you:</p>
                {job_items_html}
                <p style="font-size: 12px; color: #777; margin-top: 20px;">
                    This is an automated alert.
                </p>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(full_html, 'html'))
    try:
        print("Connecting to SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == "__main__":
    MY_EMAIL = "tradereddie30@gmail.com"
    MY_PASS = "zrsh wbsf lrki usbo"
    RECIPIENT = "Mickhasabrick@gmail.com"

    print("--- Execution Started ---")
    html_raw = scrape_indeed()

    print("Saving raw HTML to local file...")
    with open("html.txt", "w", encoding="utf-8") as file:
        file.write(html_raw)

    extract_job_links("html.txt", "trimmed_links.txt")

    print("Checking for links to email...")
    with open("trimmed_links.txt", "r", encoding="utf-8") as f:
        links_data = f.read()

    if links_data.strip():
        send_job_email(MY_EMAIL, MY_PASS, RECIPIENT, links_data)
    else:
        print("No job links found to send.")
    print("--- Execution Finished ---")
