import feedparser
import ntplib
from time import *
from datetime import datetime
import pytz
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import *
import multiprocessing
import html2text
import facebook as fb
from ctypes import c_wchar_p
import sys
import pinterest
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import base64
import config
import requests


def check_value(url, pattern):
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

def check_and_close(url, window, pattern):
    value = check_value(url, pattern)
    if value:
        window.close()
        return value
    return None

def on_url_changed(url, window, pattern):
    result = check_and_close(url, window, pattern)
    if result:
        window.close()
        
        return result

def oauth(url, app):
    pattern = r"access_token=(.*?)&data_access_expiration_time="
    window = QWidget()
    window.setMinimumSize(700, 700)
    window.setWindowTitle("RSS Manager Facebook")
    window.setWindowIcon(QtGui.QIcon("RSSManagerLogo.png"))
    layout = QVBoxLayout(window)
    web_view = QWebEngineView()
    layout.addWidget(web_view)

    value = []
    value.append("")

    def load_finished():
        value[0] = check_and_close(web_view.url().toString(), window, pattern)

    def load_finished2():
        value[0] = on_url_changed(web_view.url().toString(), window, pattern)


    web_view.loadFinished.connect(load_finished)
    web_view.page().urlChanged.connect(load_finished2)
    window.show()
    web_view.setUrl(QUrl(url))
    app.exec()
    return value[0]

def oauth2(url, app):
    pattern = r"code=(.*?)&"
    window = QWidget()
    window.setMinimumSize(700, 700)
    window.setWindowTitle("RSS Manager Pinterest")
    window.setWindowIcon(QtGui.QIcon("RSSManagerLogo.png"))
    layout = QVBoxLayout(window)
    web_view = QWebEngineView()
    layout.addWidget(web_view)
    value = []
    value.append("")

    def load_finished():

        value[0] = check_and_close(web_view.url().toString(), window, pattern)

            #return value
    def load_finished2():
        value[0] = on_url_changed(web_view.url().toString(), window, pattern)

            #print(value)
            #return value
        
    web_view.loadFinished.connect(load_finished)
    web_view.page().urlChanged.connect(load_finished2)
    window.show()
    web_view.setUrl(QUrl(url))
    app.exec()
    return value[0]



def Update(url, dict1, dictQ, exe, spec):
    #x = 0
    while True:
        if exe.is_set():
            return
        
        #print(x)
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.title not in list(dictQ.keys()):
                #print(entry.summary + "\n")
                dict1[entry.title] = html2text.html2text(entry.summary)
                
                #print(dict1[entry.title])
        sleep(1)
        #print(dict1.keys())
    return

def Sender(txt2, date, APIkey, link2, run, sent, fbbool, pinbool, pinapi, username, board, entry):
    sent.set()
    #print("1: " + "".join(APIkey))
    #print("2: " + "".join(pinapi))
    dt_object = datetime.strptime("".join(date), "%Y/%m/%d %H:%M:%S")
    current_time = datetime.now()
    # Get the local timezone
    local_timezone = current_time.astimezone().tzinfo
    # Get the UTC timezone
    utc_timezone = pytz.utc
    # Compare the offsets
    is_utc = local_timezone.utcoffset(current_time) == utc_timezone.utcoffset(current_time)
    #ltz = get_localzone()
    dt2 = dt_object
    #print(str(dt_object)) 
    if not is_utc:
        #utc = pytz.timezone("UTC")
        dt_object = dt2.astimezone(pytz.utc)
        
        #print("and " + str(local_timezone.utcoffset(current_time)))
    #print(str(dt_object)) 
    #print(str(datetime.utcnow().astimezone(pytz.utc))) 
    sent.set()
    while datetime.now().astimezone(pytz.utc) < dt_object:
        #print("HI")
        if not sent.is_set():
            return
        sleep(0.001)
    
    print("Sending...")
    fbbool2 = "".join(fbbool)
    if (fbbool2 == "yes" or fbbool2 == "y") and sent.is_set():
        pageAPI = fb.GraphAPI(str("".join(APIkey)))
        pageAPI.put_object("me","feed",message=str("".join(txt2)),link=str("".join(link2)))
    pinbool2 = "".join(pinbool)
    if (pinbool2 == "yes" or pinbool2 == "y") and sent.is_set():
        pint = pinterest.Pinterest(token="".join(pinapi))
        #pint.board().create("RSS", description="Updates")
        pboard = "".join(username) + "/" + "".join(board)
        pint.pin().create(pboard, str("".join(txt2)), str("".join(link2)))
    return

    

class MessageEdit(QWidget):
    def __init__(self, src, dictQ, entry, APIkey, m2, run, sent, fbbool, pinbool, pinapi, username, board, spec):
        #super().__init__()
        super().__init__()
        self.label = QLabel("Another Window")
        self.setWindowTitle("Message Edit")
        self.setGeometry(100, 100, 400, 200)
        self.setWindowIcon(QtGui.QIcon("RSSManagerLogo.png"))
        self.layout = QVBoxLayout()
        self.m2 = m2
        self.run = run
        self.sent = sent
        self.Ui(src, dictQ, entry, APIkey)
        self.setLayout(self.layout)
        self.show()
        self.fbbool = fbbool
        self.pinbool = pinbool
        self.pinapi = pinapi
        self.username = username
        self.board = board
        self.spec = spec
        #self.spec2 = spec2
        
        
    def getter(self, DT, txt, dictQ, entry, APIkey, link):
        #time = DT.time()
        prev = 0
        y = 0
        
        for x in list(self.spec.keys()):
            if x not in self.sent:
                self.sent[x] =self.m2.Event()
            if x == entry and self.sent[x].is_set():
                prev = self.spec[x]
                y = x
                self.spec[x] = 999
                self.sent[x].clear()
                self.spec[entry] = prev
        
        #print(DT.dateTime().toString(DT.displayFormat()))
        #date = self.m2.Value(c_wchar_p, str(DT.dateTime().toString(DT.displayFormat())))
        date = tuple(str(DT.dateTime().toString(DT.displayFormat())))
        #txt2 = self.m2.Value(c_wchar_p, str(txt.toPlainText()))
        txt2 = tuple(str(txt.toPlainText()))
        #link2 = self.m2.Value(c_wchar_p, link)
        link2 = tuple(link)
        #APIkey2 = self.m2.Value(c_wchar_p, APIkey)
        APIkey2 = tuple(APIkey)
        dictQ[entry] = str(txt.toPlainText())
        self.run.set()
        
        #self.spec2.update(self.spec)
        s = multiprocessing.Process(target=Sender, args=(txt2, date, APIkey2, link2, self.run, self.sent[y], tuple(self.fbbool), tuple(self.pinbool), tuple(self.pinapi), tuple(self.username), tuple(self.board), tuple(entry),))
        s.start()
        self.close()
        #if self.spec[entry] != 999:
            #self.spec[entry] == 999
        #s.join()
        
    def Ui(self, src, dictQ, entry, APIkey):
        label = QLabel(self)
        label.setText("Edit the time to send the post (24 hour clock):")
        label.setFont(QFont("Calibri", 15))
        label2 = QLabel(self)
        label2.setText("Edit the text below:")
        label2.setFont(QFont("Calibri", 15))
        label3 = QLabel(self)
        label3.setText("Edit the link below (insert all links here; only one link per post):")
        label3.setFont(QFont("Calibri", 15))
        DT = QDateTimeEdit(self)
        DT.setDateTime(QDateTime.currentDateTime())
        DT.setDisplayFormat("yyyy/MM/dd hh:mm:ss")
        txt = QPlainTextEdit(self)
        txt.insertPlainText(src)
        txt.move(0,0)
        txt.resize(400,200)
        txt3 = QPlainTextEdit(self)
        txt3.insertPlainText("Insert all links here. Only one link per post.")
        txt3.move(0,0)
        txt3.resize(400,100)
        push = QPushButton("Schedule!", self)
        push.clicked.connect(lambda: self.getter(DT, txt, dictQ, entry, APIkey, str(txt3.toPlainText())))
        self.layout.addWidget(label)
        self.layout.addWidget(DT)
        self.layout.addWidget(label2)
        self.layout.addWidget(txt)
        self.layout.addWidget(label3)
        self.layout.addWidget(txt3)
        self.layout.addWidget(push)
        

def viewing(listWidget, dict1):
    #print("Hi")
    listWidget.clear()
    row = 0
    dictb = dict1
    #dictb = dict(reversed(list(dict1.items())))
    for x in list(dictb.keys()):
        listWidget.insertItem(row, x)
        row += 1

#def tick(run, sent, dictQ, entry):
        #while not sent.is_set():
            #sleep(0.001)
        #del dictQ[entry]
        

def moveToQ(entryDel, listWidget, dict1, dictQ, listWidget2, run, sent):
    dictQ[entryDel] = dict1[entryDel]
    del dict1[entryDel] 
    row = 0
    listWidget.clearSelection()
    viewing(listWidget, dict1)
    #p = multiprocessing.Process(target=tick, args=(run, sent, dictQ, entryDel,))
    #p.start()
    viewing(listWidget2, dictQ)

def setting(item, widget, feed, dict1, dictQ, APIkey, m2, run, sent, widget2, fbbool, pinbool, pinapi, username, board, spec):
    #message = QMessageBox()
    #r = 0
    x = 0
    for entry in list(dict1.keys()):
        if (item.text() == entry):
            #sender = QApplication([])
            ent = entry + "\n\n" + str(dict1[entry])

            window = MessageEdit(ent, dictQ, entry, APIkey, m2, run, sent, fbbool, pinbool, pinapi, username, board, spec)
            #sender.exec()

            #message.exec()
            #print("Good")
            moveToQ(entry, widget, dict1, dictQ, widget2, run, sent)
            return None
    return None

def settingQ(item, widget, feed, dictQ, APIkey, m2, run, sent, fbbool, pinbool, pinapi, username, board, spec):
    #message = QMessageBox()
    #r = 0
    x = 0
    for entry in list(dictQ.keys()):
        if (item.text() == entry):
            #sender = QApplication([])
            ent = entry + "\n\n" + str(dictQ[entry])
            #print(dictQ[entry])
            
            window = MessageEdit(ent, dictQ, entry, APIkey, m2, run, sent, fbbool, pinbool, pinapi, username, board, spec)
            #sender.exec()
            #message.exec()
            #print("Good")
            #moveToQ(entry, widget, dict1, dictQ)
            #p = multiprocessing.Process(target=tick, args=(run, sent, dictQ, entry,))
            #p.start()
            viewing(widget, dictQ)
            return None
    return None

def exec(app, exe):
    app.exec()
    exe.set()


def main(url, dict1, dictQ, exe, fbapi, fbbool, pinapi, pinbool, username, board, spec):
    #Accepts user input for an RSS URL
    #print(url)
    sleep(1)
    fbapi = "".join(fbapi)
    pinapi = "".join(pinapi)
    fbbool = "".join(fbbool)
    pinbool = "".join(pinbool)
    username = "".join(username)
    board = "".join(board)
    m2 = multiprocessing.Manager()
    run = m2.Event()
    #sent = m2.Event()
    sent = {}
    feed = feedparser.parse(url)
    app = QApplication([])
    window = QWidget()
    window.setGeometry(100,100,1024,800)
    window.setWindowTitle("RSS Manager")
    window.setWindowIcon(QtGui.QIcon("RSSManagerLogo.png"))
    #fbapi = ""
    pageAPI = fb.GraphAPI(fbapi)
    label = QLabel(window)
    label.setText("Incoming RSS feed. Double-click on an item to schedule a post:")
    #label.setFont(QFont("Calibri", 15))
    label2 = QLabel(window)
    label2.setText("Scheduled posts and past posts. Double-click to edit/resend/reschedule:")
    #label2.setFont(QFont("Calibri", 15))

    listWidget = QListWidget()
    row = 0
    #print(dict1.keys())
    for i in list(dict1.keys()):
        
        listWidget.insertItem(row, i)
        row += 1

    listWidgetQ = QListWidget()
    row = 0
    #spec2 = m2.dict()
    #print(dict1.keys())
    for i in list(dictQ.keys()):
        
        listWidgetQ.insertItem(row, i)
        row += 1
    def on_item_activatedQ(item):
        settingQ(item, listWidgetQ, feed, dictQ, fbapi, m2, run, sent, fbbool, pinbool, pinapi, username, board, spec)

    listWidgetQ.itemActivated.connect(on_item_activatedQ)

    def on_item_activated(item):
        setting(item, listWidget, feed, dict1, dictQ, fbapi, m2, run, sent, listWidgetQ, fbbool, pinbool, pinapi, username, board, spec)

    listWidget.itemActivated.connect(on_item_activated)

    button = QPushButton("Load!")

    def viewer():
        viewing(listWidget, dict1)

    btnconnect = button.clicked.connect(viewer)

    
    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.addWidget(listWidget)
    layout.addWidget(button)
    layout.addWidget(label2)
    layout.addWidget(listWidgetQ)
    window.setLayout(layout)
    window.show()
    sys.exit(exec(app, exe))

if __name__ == "__main__":
    url = ""
    while "http" not in url:
        url = input("What is the URL of your RSS feed?\n") 
    #print(url)
    fbapi = ""
    fbbool = ""
    app = QApplication(sys.argv)
    access_token = ""
    while (fbbool != "yes" and fbbool != "y") and (fbbool != "no" and fbbool != "n"):
        fbbool = input("Do you want to connect to your Facebook Page? ([Y]es/[N]o)\n")
        fbbool = fbbool.lower()
        #print(fbbool)
    if fbbool == "yes" or fbbool == "y":
        fbapi = oauth("https://www.facebook.com/v19.0/dialog/oauth?client_id=" + config.fbcid +"&redirect_uri=https://www.facebook.com/connect/login_success.html&state=\"{st=strss4039,ds=89034759}\"&response_type=token&config_id=" + config.config_id, app)
        if fbapi:
            print("Connected to social media!")
    pinbool = ""
    pinapi = ""
    while (pinbool != "yes" and pinbool != "y") and (pinbool != "no" and pinbool != "n"):
        pinbool = input("Do you want to connect to your Pinterest? ([Y]es/[N]o)\n")
        pinbool = pinbool.lower()
    username = ""
    board = ""
    if pinbool == "yes" or pinbool == "y":
        pincode = ""
        pincode = oauth2("https://www.pinterest.com/oauth/?client_id=" + config.pinid + "&redirect_uri=https://github.com/emirelease/RSS-Manager&response_type=code&scope=boards:read,pins:read,boards:write,pins:write&state=\"{st=1890349,ds=490466}\"", app)
        authbytes = config.auth.encode("utf-8")
        b64 = base64.b64encode(authbytes).decode("utf-8")  
        payload = {
            "grant_type": "authorization_code",
            "code": pincode,
            "redirect_uri": "https://github.com/emirelease/RSS-Manager"
        }
        headers = {
            "Authorization": "Basic " + b64,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post("https://api.pinterest.com/v5/oauth/token", data=payload, headers=headers)
        data = response.json()
        access_token = data.get("access_token", "").replace("pina_", "")
        if access_token:
            print("Connected to social media!")
        confirm = ""
        while (confirm != "yes" and confirm != "no") and (confirm != "y" and confirm != "n"):
            username = input("Type in your Pinterest username (case-sensitive):\n")
            confirm = input("Is " + "\"" + username + "\"" + " your username? ([Y]es/[N]o)\n")
        confirm = ""
        while (confirm != "yes" and confirm != "no") and (confirm != "y" and confirm != "n"):
            board = input("Type in the Pinterest board you want to use (case-sensitive):\n")
            confirm = input("Is " + "\"" + board + "\"" + " the correct board? ([Y]es/[N]o)\n")
    m1 = multiprocessing.Manager()
    dict1 = m1.dict()
    dictQ = m1.dict()
    spec = m1.dict()
    exe = m1.Event()
    updater = multiprocessing.Process(target=Update, args=(url,dict1,dictQ,exe,spec))
    # Start the process
    pinapi = access_token
    print(fbapi)
    m = multiprocessing.Process(target=main,args=(url,dict1,dictQ,exe, tuple(fbapi), tuple(fbbool), tuple(pinapi), tuple(pinbool), tuple(username), tuple(board), spec))
    updater.start()
    #sleep(1)
    m.start()
    updater.join()
    m.join()
    
