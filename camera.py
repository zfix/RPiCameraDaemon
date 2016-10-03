import os
import sys
from subprocess import Popen, PIPE
import signal
import time
import atexit
from daemon3x import Daemon
import psutil
import signal
params = {'host': '8.8.8.8',
          'pidfile': '/tmp/camera.pid',
          }
params['cmd'] = 'gst-launch-1.0 rpicamsrc rotation=0 sensor-mode=5 preview=false bitrate=2000000 \
                    keyframe-interval=60 drc=high ! \
                    video/x-h264,width=1280,height=720,profile=high,framerate=0/30 ! \
                    h264parse ! flvmux ! rtmpsink location=rtmp://localhost/live/camera'

class MyDaemon(Daemon):
    '''
    '''
    def __init__(self, params):
        self.params = params
        self.pidfile = params['pidfile']
        self.cmd = params['cmd']
        self.logfile = params['logfile']

    def startprocs(self):
        self.logging('proc1 starting')
        self.proc = Popen(self.cmd.split(), stdout=PIPE, stderr=PIPE)
        self.logging('daemon started')

    def stopprocs(self):
        if psutil.pid_exists(self.proc2.pid):
            self.proc.terminate()

    def run(self):
        self.startprocs()
        while True:
            if self.proc.poll():
                self.logging('proc2 problem')
                self.stopprocs()
                self.startprocs()
            self.logging('gst is ok')
            time.sleep(2)

    def logging(self, msg):
        logfile = open(self.params['logfile'], 'a')
        logfile.write(msg + '\n')
        logfile.close()

    def pstop(self):
        pidfile = open(self.params['pidfile'], 'r')
        pid = int(pidfile.read())
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()


if __name__ == "__main__":
    daemon = MyDaemon(params)
    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.pstop()
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.stop()
            time.sleep(1)
            daemon.start()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
