"""
download pubmed-baseline citation xml files from FTP to local
ftp site: 'ftp.ncbi.nlm.nih.gov'
"""

from ftplib import FTP
import os
ftp = FTP('ftp.ncbi.nlm.nih.gov')
ftp.login()
ftp.cwd("pubmed/baseline")
listing = []
ftp.retrlines("LIST", listing.append)
files = [f for f in listing if f.endswith('.xml.gz') or f.endswith('txt')]
# download the file
fid = 0
while fid < len(files):
    try:
        words = files[fid].split(None, 8)
        filename = words[-1].lstrip()
        print(f"download file {filename}")
        local_filename = f"../data/raw/{filename}"
        lf = open(local_filename, "wb")
        ftp.retrbinary("RETR " + filename, lf.write, 8*1024)
        lf.close()
        fid = fid + 1
    except:
        ftp = FTP('ftp.ncbi.nlm.nih.gov')
        ftp.login()
        ftp.cwd("pubmed/baseline")
        listing = []
        ftp.retrlines("LIST", listing.append)
        files = [f for f in listing if f.endswith('.xml.gz') or f.endswith('txt')]

