from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import DocumentForm
from .topsis import CalculateTopsisScore
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re
import pandas as pd

regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = "datascience1311@gmail.com"
password = "qwerty@123"
context = ssl.create_default_context()

session = smtplib.SMTP('smtp.gmail.com', port)  # use gmail with port
session.ehlo()
session.starttls()
session.ehlo()
session.login(sender_email, password)

mail_content = '''Hello,
This is The Calculated Topsis Score with Ranking.
Thank You For using Our service.
'''


def calculateTopsis(request):
    if request.method == 'POST' and request.FILES['myfile']:

        message = MIMEMultipart()
        message['From'] = sender_email
        message['Subject'] = 'Calculated Topsis Score'
        message.attach(MIMEText(mail_content, 'plain'))
        myfile = request.FILES['myfile']
        print(myfile.size)
        email = request.POST.get("email")
        weight = request.POST.get("weight")
        impact = request.POST.get("impact")
        receiver_address = email
        print(receiver_address)
        message['To'] = receiver_address
        print(myfile, myfile.content_type, email, weight, impact)
        
        email = email.strip()
        weight = weight.split(",")
        impact = [x.strip() for x in impact.split(",")]

        if email == None or email == "" or not re.search(regex, email):
            return render(request, 'core/calculateTopsis.html', {
                'error_file': "Error : Enter valid Email Id",
                'uploaded_file_url': ""
            })
        if weight == None or weight == "":
            return render(request, 'core/calculateTopsis.html', {
                'error_file': "Error : Enter correct Weights",
                'uploaded_file_url': ""
            })
        for i, w in enumerate(weight):
            try:
                weight[i] = float(w.strip())
                continue
            except ValueError:
                if not w.isnumeric():
                    return render(request, 'core/calculateTopsis.html', {
                        'error_file': "Error : Incorrect Weights Format",
                        'uploaded_file_url': ""
                    })
                else:
                    weight[i] = int(w.strip())

        if impact == None or impact == "":
            return render(request, 'core/calculateTopsis.html', {
                'error_file': "Error : Enter corect impact values",
                'uploaded_file_url': ""
            })

        for i in impact:
            if i not in ["+", "-"]:
                return render(request, 'core/calculateTopsis.html', {
                    'error_file': "Error : Incorrect Impact Format",
                    'uploaded_file_url': ""
                })

        # try:
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print(filename)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)
        output_file = CalculateTopsisScore(uploaded_file_url, weight, impact)
        attach_file_name = output_file

        try:
            if output_file["error"] == True:
                return render(request, 'core/calculateTopsis.html', {
                    'error_file': "Error : {}".format(output_file["msg"]),
                    'uploaded_file_url': ""
                })

        except:
            pass
        # Open the file as binary mode
        try:

            attach_file = open(attach_file_name, 'rb')
            payload = MIMEBase('application', 'octate-stream',
                               name="".join(attach_file_name.split('/')[1:]))
            payload.set_payload((attach_file).read())
            encoders.encode_base64(payload)  # encode the attachment
            # add payload header with filename
            name = "".join(
                "".join(attach_file_name.split('/')[1:]).split(".")[0])
            payload.add_header('Content-Decomposition', 'attachment',
                               filename="".join(attach_file_name.split('/')[1:]))
            message.attach(payload)
            text = message.as_string()
            print("sending")
            session.sendmail(sender_email, receiver_address, text)
            # session.sendmail(message)
            print("sent")
            attach_file.close()
        except:
            return render(request, 'core/calculateTopsis.html', {
                'error_file': "Error : Email Not Sent",
                'uploaded_file_url': output_file
            })
        return render(request, 'core/calculateTopsis.html', {
            'error_file': "Email Sent",
            'uploaded_file_url': output_file
        })
        # except:
        #     return render(request, 'core/calculateTopsis.html', {
        #         'error_file': "Error : Some Error Occured",
        #         'uploaded_file_url': ""
        #     })
    return render(request, 'core/calculateTopsis.html', {
        'uploaded_file_url': ""
    })
