import re
import urlparse
import threading
import Queue
import time
import requests
import sys
from consle_width import getTerminalSize
class ScanningClass(threading.Thread):
    def __init__(self,options):
        self.dir_200 = self.thread_list = self.dir = self.dir_list = self.urls = []
        self.num = self.found_count = self.status = self.scan_count = self.thread_count = 0
        self.dir1 = self.URL = ""
        self.options = options
        self.msg_queue = Queue.Queue()
        self.dir_list = str(options.DicFile).split(',')
        self.filename=""
        self.STOP_ME = False
        self.start_time = time.time()
        self.lock = threading.Lock()
        threading.Thread(target=self._print_msg).start()
        self.console_width = getTerminalSize()[0] - 2
        (self.filename,self.URL)=self.urlHandling(self.options.URL)
        self.OutputFile = "%s.txt" % (self.filename)
        if self.options.ThreadNum != None:
            self.ThreadNum = options.ThreadNum
        else:
            self.ThreadNum= 50
        if self.options.OutputFile != None:
            self.OutputFile = options.OutputFile
        else:
            self.OutputFile = self.filename + ".txt"
        for dir in self.dir_list:
            self.dir1 = "dic/" + dir
            self.readdic(self.dir1)
    def urlHandling(self,url):
        if not url.startswith('http://') and not url.startswith('https://'):
                self.filename = url
                self.url = 'http://' + self.url
        else:
            self.url = urlparse.urlparse(url).netloc
            self.filename = self.url
            self.url = 'http://' + self.url
        return self.filename, self.url
    def readdic(self,dir):
        dic = []
        self.queue = Queue.Queue()
        try:
            f = open(dir,'r')
            while True:
                line = f.readline()
                if line:
                    line = line.strip('\n')
                    dic.append(line)
                else:
                    break
            f.close()
        except IOError as e:
            print "%s Does not exist, please check the file name" % (dir)
            exit(0)
        for i in range(len(dic)):
            str = dic[i]
            if str.startswith('/'):
                url = self.URL + str
                self.queue.put(url)
            else:
                url = self.URL + "/" + str
                self.queue.put(url)
        if self.queue.qsize() > 0:
            pass
        else:
            print 'The dictionary file is empty !'
            exit(0)
    def write(self):
        try:
            f = open(self.OutputFile,'w')
        except IOError as e:
            print "Open %s exception" % (self.OutputFile)
        f.write("200 pages:\n")
        for x in self.dir_200:
            f.write(x + "\n")
        f.close()
    def _update_scan_count(self):
        self.lock.acquire()
        self.scan_count += 1
        self.lock.release()
    def _print_msg(self):
        while not self.STOP_ME:
            try:
                _msg = self.msg_queue.get(timeout=0.1)
            except:
                continue
            if _msg == 'status':
                msg = '%s found | %s remaining | %s scanned in %.2f seconds | threads %s' % (
                    self.found_count, self.queue.qsize(), self.scan_count, time.time() - self.start_time, self.thread_count)
                sys.stdout.write('\r' + ' ' * (self.console_width - len(msg)) + msg)
            elif _msg.startswith('[+]'):
                sys.stdout.write('\r' + _msg + ' ' * (self.console_width - len(_msg)))
            else:
                sys.stdout.write('\r' + _msg + ' ' * (self.console_width - len(_msg)) + '\n')
            sys.stdout.flush()


    def run(self):
        self.start_time=time.time()
        for i in range(self.ThreadNum):
            t = threading.Thread(target=self._openurl,name=str(i))
            t.setDaemon(True)
            t.start()
        while self.thread_count >= 1:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt, e:
                self.msg_queue.put('\n[WARNING] User aborted, wait all slave threads to exit, current(%i)' % threading.activeCount())
                sys.stdout.flush()
                self.STOP_ME = True
        self.STOP_ME = True
    def _openurl(self):
        self.lock.acquire()
        self.thread_count += 1
        self.lock.release()
        html_result = 0
        while not self.queue.empty() and self.STOP_ME == False:
            try:
                payload = self.queue.get(timeout=1.0)
                html_result = requests.get(payload,timeout=3)
                self.msg_queue.put('status')
            except:
                pass
            if html_result != 0:
                if html_result.status_code == 200 :
                    self.msg_queue.put("[+]%s\t\t\t\t\t\t\t" % (payload))
                    self.msg_queue.put('status')
                    self.found_count += 1
                    self.dir_200.append(payload)
            self._update_scan_count()
        self.lock.acquire()
        self.thread_count -= 1
        self.lock.release()
        self.msg_queue.put('status')




