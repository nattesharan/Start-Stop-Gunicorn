import os
import signal
import commands
import argparse
import time
PID_FILE = 'chat-app.pid'

def get_pid():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            return int(f.read())
    else:
        print '[Error]: pid file not exists!'
        return None

def rm_pidfile():
    if os.path.exists(PID_FILE):
        print '[Remove File]: %s' % PID_FILE
        os.remove(PID_FILE)

def Quit():
    pid = get_pid()
    if pid:
        print '>>> Quiting ......'
        try:
            os.kill(pid, signal.SIGQUIT)
        except OSError, e:
            print '[Failed]: Server haven\'t start yet!'
def Stop():
    pid = get_pid()
    if pid:
        print '>>> Stoping ......'
        try:
            os.kill(pid, signal.SIGTERM)
            print '[Successed]: ok!'
        except OSError, e:
            print '[Failed]: <pid: %d> has gone!' % pid

def Reload():
    pid = get_pid()
    if pid:
        print '>>> Reloading ......'
        try:
            os.kill(pid, signal.SIGHUP)
        except OSError, e:
            print '[Failed]: Server haven\'t start yet!'

def start():
    if os.path.exists(PID_FILE):
        pid = get_pid()
        print '<< Server already started! >>'
    else:
        print '>>> Starting server ......'
        run_cmd = 'venv/bin/gunicorn -b :8000 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 main:app --pid {} --reload --daemon'.format(PID_FILE)
        print '[Run Command]: %s' % run_cmd
        code, output = commands.getstatusoutput(run_cmd)

        if code == 0:
            time.sleep(8)
            pid = get_pid()
            try:
                os.kill(pid, 0)
                print '''
                [Successed]:
                ===========
                    pid      =  %d
                    pidfile  =  %s
                                ''' % (pid, PID_FILE)
            except OSError, e:
                print '''
                [Failed]:
                ========
                    Process start failed.
                    Permission denied? You may run this script as `root'.
                '''
                rm_pidfile()
        else:
            print '[Failed]: status=[%d], output=[%s]' % (code, output)
def restart():
    Quit()
    time.sleep(6)
    start()

def main():
    parser = argparse.ArgumentParser(description='Manage the gunicorn(just like apache) server.')
    parser.add_argument('--start', action='store_true', help='Start your wsgi application')
    parser.add_argument('--quit', action='store_true', help='[Unrecomanded!] Quick shutdown. ')
    parser.add_argument('--stop', action='store_true', help='Graceful shutdown. Waits for workers to finish their current requests up to the graceful timeout.')
    parser.add_argument('--reload', action='store_true', help='Reload the configuration, start the new worker processes with a new configuration and gracefully shutdown older workers.')
    parser.add_argument('--restart', action='store_true', help='[Unrecomanded!] Simply `quit\' the server then `start\' it')
    args = parser.parse_args()

    for label, func in {'start': start,
                        'restart':restart,
                        'quit': Quit,
                        'stop': Stop,
                        'reload': Reload }.iteritems():
        if getattr(args, label):
            func()
            break
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
