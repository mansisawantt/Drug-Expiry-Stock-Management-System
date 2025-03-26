import os
import smtplib
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

# Load environment variables from .env
load_dotenv()

# Email Credentials (from .env)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Use an App Password, not your Gmail password!
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Twilio Credentials (from .env)
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECEIVER_PHONE_NUMBER = os.getenv("RECEIVER_PHONE_NUMBER")

# Connect to SQLite Database
conn = sqlite3.connect("pharmacy.db")
today = datetime.today()
threshold_date = today + timedelta(days=180)  # Medicines expiring in 6 months

# Fetch near-expiry medicines
query = "SELECT medicine_name, expiry_date, stock_quantity FROM medicine_stock WHERE expiry_date <= ?"
df = pd.read_sql(query, conn, params=(threshold_date.strftime('%Y-%m-%d'),))
conn.close()

if not df.empty:
    message_body = " Near-Expiry Medicines Alert:\n"
    
    for _, row in df.iterrows():
        message_body += f"{row['medicine_name']} - Expiry: {row['expiry_date']} - Stock: {row['stock_quantity']}\n"

    # Limit SMS length (Twilio max = 1600 chars)
    sms_body = message_body[:1500] + "..." if len(message_body) > 1500 else message_body

    # Send Email Alert
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = " Near-Expiry Medicines Alert"
        msg.attach(MIMEText(message_body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(" Email alert sent successfully.")
    except Exception as e:
        print(f" Email alert failed: {e}")

    # Send SMS Alert
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=sms_body,
            from_=TWILIO_PHONE_NUMBER,
            to=RECEIVER_PHONE_NUMBER
        )
        print(f"✅ SMS alert sent successfully: {message.sid}")
    except Exception as e:
        print(f" SMS alert failed: {e}")
else:
    print("✅ No medicines expiring soon.")
