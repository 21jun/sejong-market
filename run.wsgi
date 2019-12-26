import sys

sys.path.insert(0, "/var/www/html")
sys.path.append("/home/ubuntu/.pyenv/versions/3.7.0")
sys.path.append("/home/ubuntu/.pyenv/versions/3.7.0/lib/python3.7/site-packages")

from app import app as application