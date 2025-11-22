import os
from mailjet_rest import Client

MJ_API_PUBLIC = os.getenv("MJ_APIKEY_PUBLIC")
MJ_API_PRIVATE = os.getenv("MJ_APIKEY_PRIVATE")

mailjet = Client(auth=(MJ_API_PUBLIC, MJ_API_PRIVATE), version='v3.1')

def send_reset_email(to_email: str, reset_link: str):
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "amankadam1116@gmail.com",
                    "Name": "ElectroSoft"
                },
                "To": [
                    { "Email": to_email }
                ],
                "Subject": "Password Reset Request",
                "HTMLPart": f"""
                <h3>Password Reset</h3>
                <p>Click the link below to reset your password:</p>
                <a href="{reset_link}">{reset_link}</a>
                <p>This link expires in 30 minutes.</p>
                """
            }
        ]
    }
    return mailjet.send.create(data=data)
