import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open('uwsgi.ini', 'w', encoding="utf-8") as f:
    content = "[uwsgi]"+"\n"
    content += "http=0.0.0.0:8889"+"\n"
    content += "chdir=" + BASE_DIR+"\n"
    content += "wsgi-file=Credit_Score_Test/wsgi.py"+"\n"
    content += "process=1"+"\n"
    content += "threads=2"+"\n"
    content += "pidfile=uwsgi.pid"+"\n"
    content += "daemonize=uwsgi.log"+"\n"
    content += "master=true"
    f.write(content)
