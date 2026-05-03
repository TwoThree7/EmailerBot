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
import time


def main():
    radius = 25
    searchWord = 'bricklayer'


    url = 'https://uk.indeed.com/jobs?q=' + searchWord + '&l=Leeds%2C+West+Yorkshire&fromage=7&radius=' + str(radius)
    indeedHtml = scapeIndeed(url)
    with open("indeedHtml.txt", "a", encoding="utf-8") as file:
        file.write(indeedHtml)
    extract_job_links_Indeed("indeedHtml.txt", "trimmed_linksText.txt", searchWord)

    #gumtree_url = "https://www.gumtree.com/search?search_category=jobs&q=brickwork&search_location=leeds"
    #gumTreeHtml = scrape_gumtree(gumtree_url)
    #with open("gumtreeHtml.txt", "a", encoding="utf-8") as file:
     #   file.write(gumTreeHtml)
    #extract_gumtree_links("gumtreeHtml.txt", "trimmed_linksText.txt")

    searchWord = 'bricklayer+gangs'
    url = 'https://uk.indeed.com/jobs?q=' + searchWord + '&l=Leeds%2C+West+Yorkshire&fromage=7&radius=' + str(radius)
    indeedHtml = scapeIndeed(url)
    with open("indeedHtml.txt", "a", encoding="utf-8") as file:
        file.write(indeedHtml)
    extract_job_links_Indeed("indeedHtml.txt", "trimmed_linksText.txt", searchWord)

    MY_EMAIL = "tradereddie30@gmail.com"
    MY_PASS = "zrsh wbsf lrki usbo"
    RECIPIENT = "mickhasabrick@gmail.com"

    with open("trimmed_linksText.txt", "r", encoding="utf-8") as f:
        all_links = f.read()

    if all_links.strip():
        send_job_email(MY_EMAIL, MY_PASS, RECIPIENT, all_links)


def scapeIndeed(url):
    print("Starting Chrome driver (Indeed)...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        print(f"Navigating to Indeed: {url}")
        driver.get(url)
        time.sleep(5)
        html = driver.page_source
        print("Indeed source acquired.")
        return html
    finally:
        print("Closing Chrome driver.")
        driver.quit()


def extract_job_links_Indeed(input_file, output_file, jobName):
    print(f"Extracting Indeed links from {input_file}...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, "html.parser")
        job_headers = soup.find_all("h2", class_=lambda x: x and "jobTitle" in x)
        extracted_elements = []
        for header in job_headers:
            link_tag = header.find("a")
            if link_tag:
                extracted_elements.append(str(link_tag))
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- INDEED: {jobName} ---\n")
            for item in extracted_elements:
                f.write(item + "\n\n")
        print(f"Indeed extraction complete. {len(extracted_elements)} links appended.")
    except Exception as e:
        print(f"Error during Indeed extraction: {e}")


def scrape_gumtree(url):
    print("Starting Chrome driver (Gumtree)...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        print(f"Navigating to Gumtree: {url}")
        driver.get(url)
        time.sleep(5)
        html = driver.page_source
        print("Gumtree source acquired.")
        return html
    finally:
        print("Closing Chrome driver.")
        driver.quit()


def extract_gumtree_links(input_file, output_file):
    print(f"Extracting Gumtree links from {input_file}...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, "html.parser")
        job_links = soup.find_all("a", class_=lambda x: x and "listing-link" in x)
        extracted_elements = []
        for link in job_links:
            if link.get_text(strip=True):
                extracted_elements.append(str(link))
        with open(output_file, "a", encoding="utf-8") as f:
            f.write("\n--- GUMTREE RESULTS ---\n")
            for item in extracted_elements:
                f.write(item + "\n\n")
        print(f"Gumtree extraction complete. {len(extracted_elements)} items appended.")
    except Exception as e:
        print(f"Error during Gumtree extraction: {e}")


def send_job_email(sender_email, sender_password, receiver_email, job_list_html):
    print(f"Sending formatted email to {receiver_email}...")

    # Generate a unique timestamp to prevent Gmail from threading/clipping
    timestamp = time.strftime('%H:%M:%S')

    msg = MIMEMultipart('alternative')
    msg['From'] = f"MB Brickwork Jobs <{sender_email}>"
    msg['To'] = receiver_email
    msg['Subject'] = f"Latest Job Matches: Leeds ({timestamp})"

    job_items_html = ""
    soup = BeautifulSoup(job_list_html, "html.parser")
    links = soup.find_all("a")

    for link in links:
        title = link.get_text(strip=True)
        href = link.get('href', '#')
        if href.startswith('/'):
            if "gumtree" in str(link).lower():
                href = f"https://www.gumtree.com{href}"
            else:
                href = f"https://uk.indeed.com{href}"


        job_items_html += f"""
        <div style="padding:14px 16px; margin-bottom:10px; border-left:4px solid #FFD000; border-top:1px solid #e8e8e8; border-right:1px solid #e8e8e8; border-bottom:1px solid #e8e8e8; border-radius:6px; background-color:#fafafa;">
            <p style="margin:0 0 10px 0; font-family:Arial,Helvetica,sans-serif; font-size:15px; font-weight:700; color:#1a1a1a;">{title}</p>
            <a href="{href}" style="display:inline-block; background-color:#1a1a1a; color:#FFD000; padding:7px 18px; text-decoration:none; border-radius:4px; font-weight:700; font-family:Arial,Helvetica,sans-serif; font-size:13px; letter-spacing:0.5px; border:0;">View Listing</a>
        </div>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MB Brickwork - Job Matches</title>
<style>
    /* Absolute reset for all tables to remove ghost borders */
    table, td {{ border-collapse: collapse !important; mso-table-lspace: 0pt !important; mso-table-rspace: 0pt !important; border: 0 !important; }}
    img {{ border: 0 !important; outline: none !important; text-decoration: none; }}
    body {{ margin: 0 !important; padding: 0 !important; width: 100% !important; }}
</style>
</head>
<body style="margin:0; padding:0; background-color:#ffffff; font-family:Arial,Helvetica,sans-serif; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%;">

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#ffffff; border:0;">
  <tr>
    <td align="center" style="padding:30px 0; border:0;">
      <table width="620" cellpadding="0" cellspacing="0" border="0" style="max-width:620px; width:100%; border:0;">

        <tr>
          <td style="padding:0; line-height:0; font-size:0; border:0;">
            <svg width="100%" viewBox="0 0 620 90" xmlns="http://www.w3.org/2000/svg" style="display:block;">
              <rect width="620" height="90" fill="#1a1a1a"/>
              <polygon points="0,0 72,8 35,55" fill="rgba(255,208,0,0.58)" stroke="rgba(180,120,0,0.5)" stroke-width="0.7"/>
              <polygon points="72,8 140,0 115,48" fill="rgba(255,232,80,0.33)" stroke="rgba(200,145,0,0.38)" stroke-width="0.7"/>
              <polygon points="72,8 115,48 35,55" fill="rgba(240,180,0,0.46)" stroke="rgba(175,115,0,0.48)" stroke-width="0.7"/>
              <polygon points="140,0 210,14 115,48" fill="rgba(255,220,40,0.24)" stroke="rgba(195,138,0,0.33)" stroke-width="0.7"/>
              <polygon points="210,14 280,0 255,52" fill="rgba(255,195,0,0.52)" stroke="rgba(165,108,0,0.55)" stroke-width="0.7"/>
              <polygon points="115,48 210,14 175,72" fill="rgba(255,208,0,0.40)" stroke="rgba(180,120,0,0.45)" stroke-width="0.7"/>
              <polygon points="210,14 255,52 175,72" fill="rgba(255,232,80,0.30)" stroke="rgba(200,145,0,0.35)" stroke-width="0.7"/>
              <polygon points="280,0 355,10 310,58" fill="rgba(240,180,0,0.55)" stroke="rgba(175,115,0,0.50)" stroke-width="0.7"/>
              <polygon points="255,52 310,58 240,82" fill="rgba(255,220,40,0.38)" stroke="rgba(195,138,0,0.42)" stroke-width="0.7"/>
              <polygon points="355,10 420,0 390,45" fill="rgba(255,195,0,0.48)" stroke="rgba(165,108,0,0.52)" stroke-width="0.7"/>
              <polygon points="310,58 390,45 345,88" fill="rgba(255,208,0,0.35)" stroke="rgba(180,120,0,0.40)" stroke-width="0.7"/>
              <polygon points="390,45 420,0 470,18" fill="rgba(255,232,80,0.52)" stroke="rgba(200,145,0,0.48)" stroke-width="0.7"/>
              <polygon points="420,0 500,5 470,18" fill="rgba(240,180,0,0.28)" stroke="rgba(175,115,0,0.32)" stroke-width="0.7"/>
              <polygon points="470,18 500,5 540,38" fill="rgba(255,220,40,0.55)" stroke="rgba(195,138,0,0.50)" stroke-width="0.7"/>
              <polygon points="500,5 580,0 555,32" fill="rgba(255,195,0,0.38)" stroke="rgba(165,108,0,0.42)" stroke-width="0.7"/>
              <polygon points="540,38 555,32 580,75" fill="rgba(255,208,0,0.50)" stroke="rgba(180,120,0,0.55)" stroke-width="0.7"/>
              <polygon points="555,32 580,0 620,12" fill="rgba(255,232,80,0.42)" stroke="rgba(200,145,0,0.45)" stroke-width="0.7"/>
              <polygon points="580,75 620,12 620,90" fill="rgba(240,180,0,0.32)" stroke="rgba(175,115,0,0.36)" stroke-width="0.7"/>
              <polygon points="0,55 35,55 0,90" fill="rgba(255,220,40,0.44)" stroke="rgba(195,138,0,0.48)" stroke-width="0.7"/>
              <polygon points="35,55 175,72 80,90" fill="rgba(255,195,0,0.30)" stroke="rgba(165,108,0,0.34)" stroke-width="0.7"/>
              <polygon points="175,72 240,82 200,90" fill="rgba(255,208,0,0.52)" stroke="rgba(180,120,0,0.50)" stroke-width="0.7"/>
              <polygon points="240,82 345,88 290,90" fill="rgba(255,232,80,0.36)" stroke="rgba(200,145,0,0.40)" stroke-width="0.7"/>
              <polygon points="345,88 470,75 430,90" fill="rgba(240,180,0,0.48)" stroke="rgba(175,115,0,0.44)" stroke-width="0.7"/>
              <polygon points="470,75 540,38 560,90" fill="rgba(255,220,40,0.28)" stroke="rgba(195,138,0,0.32)" stroke-width="0.7"/>
              <polygon points="540,38 580,75 560,90" fill="rgba(255,195,0,0.55)" stroke="rgba(165,108,0,0.52)" stroke-width="0.7"/>
              <rect x="0" y="0" width="620" height="3" fill="#FFD000"/>
            </svg>
          </td>
        </tr>

        <tr>
          <td align="center" style="background-color:#1a1a1a; padding:28px 40px 24px; border:0;">
            <table cellpadding="0" cellspacing="0" border="0" style="border:0;">
              <tr>
                <td align="center" style="border:0;">
                  <span style="font-family:Georgia,'Times New Roman',serif; font-size:52px; font-weight:700; color:#FFD000; letter-spacing:-2px; line-height:1;">MB</span>
                </td>
                <td style="padding:0 18px; border:0;">
                  <div style="width:1px; height:58px; background-color:rgba(255,208,0,0.35);"></div>
                </td>
                <td align="left" style="vertical-align:middle; border:0;">
                  <div style="font-family:Arial,Helvetica,sans-serif; font-size:26px; font-weight:700; color:#ffffff; letter-spacing:3px; line-height:1.15;">BRICK</div>
                  <div style="font-family:Arial,Helvetica,sans-serif; font-size:26px; font-weight:300; color:#FFD000; letter-spacing:5px; line-height:1.15;">WORK</div>
                  <div style="font-family:Arial,Helvetica,sans-serif; font-size:9px; font-weight:400; color:rgba(255,255,255,0.40); letter-spacing:2.5px; margin-top:4px;">CONSTRUCTION SPECIALISTS</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td style="padding:0; background-color:#ffffff; border:0;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:0;">
              <tr>
                <td width="22" style="width:22px; background-color:#1a1a1a; border:0;">&nbsp;</td>

                <td style="padding:28px 24px; vertical-align:top; background-color:#ffffff; border:0;">
                  <h2 style="margin:0 0 6px 0; font-family:Arial,Helvetica,sans-serif; font-size:20px; font-weight:700; color:#1a1a1a;">New Job Matches</h2>
                  <p style="margin:0 0 20px 0; font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#888888;">Latest listings &mdash; Leeds area</p>

                  {job_items_html}

                </td>

                <td width="22" style="width:22px; background-color:#1a1a1a; border:0;">&nbsp;</td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td align="center" style="padding:20px 0; border:0;">
            <p style="margin:0; font-family:Arial,Helvetica,sans-serif; font-size:11px; color:#888888;">MB Brickwork Construction Specialists &mdash; Leeds</p>
            <p style="margin:4px 0 0 0; font-family:Arial,Helvetica,sans-serif; font-size:11px; color:#aaaaaa;">Sent at {timestamp} &mdash; Job Alerts Subscribed</p>

            <div style="display:none; white-space:nowrap; font:15px courier; line-height:0; color:#ffffff;">
                {"&nbsp; " * 60} {timestamp}
            </div>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>

</body>
</html>"""

    msg.attach(MIMEText(full_html, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    main()
