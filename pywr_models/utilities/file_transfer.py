import os
from ftplib import FTP

host = "ftp.box.com"
username = os.environ['BOX_USERNAME']
password = os.environ['BOX_PASSWORD']
with FTP(host, username, password) as ftp:
    ftp.login()
    ftp.dir()