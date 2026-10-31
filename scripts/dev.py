#!/usr/bin/env python3
"""Run the current UI and API together; stop only the child processes we own."""
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]


def main():
    api_port=int(os.environ.get('COCONUTS_PORT','8000'))
    web_port=int(os.environ.get('COCONUTS_WEB_PORT','5173'))
    python=os.environ.get('COCONUTS_PYTHON') or str(ROOT/'.venv/bin/python')
    if not Path(python).is_file():python=shutil.which(python) or sys.executable
    pnpm=os.environ.get('COCONUTS_PACKAGE_RUNNER') or shutil.which('pnpm')
    if not pnpm:raise SystemExit('pnpm is unavailable. Run start.command or install pnpm first.')
    for port in [api_port,web_port]:
        try:
            with socket.socket() as check:check.bind(('127.0.0.1',port))
        except OSError:raise SystemExit('Port %s is in use. Stop the old server, or set COCONUTS_PORT and COCONUTS_WEB_PORT.'%port)
    env=dict(os.environ)
    env['COCONUTS_API_TARGET']='http://127.0.0.1:%s'%api_port
    env.setdefault('COCONUTS_CORS_ORIGINS','http://127.0.0.1:%s,http://localhost:%s'%(web_port,web_port))
    children=[]
    def stop(signum,frame):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,stop)
    try:
        api=subprocess.Popen([python,'-m','backend.server','--port',str(api_port)],cwd=ROOT,env=env,start_new_session=True);children.append(api)
        for attempt in range(50):
            if api.poll() is not None:raise SystemExit('API exited during startup.')
            try:
                with urllib.request.urlopen(env['COCONUTS_API_TARGET']+'/api/health',timeout=.5):break
            except OSError:time.sleep(.1)
        else:raise SystemExit('API did not become ready.')
        ui=subprocess.Popen([pnpm,'run','dev','--port',str(web_port),'--strictPort'],cwd=ROOT,env=env,start_new_session=True);children.append(ui)
        while all(p.poll() is None for p in children):time.sleep(.2)
    except KeyboardInterrupt:pass
    finally:
        for process in children:
            if process.poll() is None:os.killpg(process.pid,signal.SIGTERM)
        for process in children:
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()


if __name__=='__main__':main()
