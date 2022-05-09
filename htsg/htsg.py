import os
import time
import threading
import shutil
import tempfile
import http.server
import socketserver
import functools
import hashlib
from contextlib import redirect_stdout
import toml
from jinja2 import Environment, FileSystemLoader
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class _spinner:
    def __init__(self, prefix):
        self.prefix = prefix
        self.done = False

    def _loop(self):
        spinners = ["/", "-", "\\", "|"]
        i = 0
        while True:
            if self.done:
                break
            sp = spinners[i]
            print(f"\r{self.prefix} ... {sp}", end="")
            i = (i + 1) % 4
            time.sleep(.2)

    def start(self):
        self.done = False
        threading.Thread(target=self._loop).start()

    def stop(self):
        self.done = True
        print(f"\r{self.prefix} ... done.")


def generate(
    srcdir="./src",
    tpldir="./templates",
    distdir="./dist",
    cfgfile="./config.toml",
    globals={},
):
    print("---")
    print(f"srcdir  = '{srcdir}'")
    print(f"tpldir  = '{tpldir}'")
    print(f"distdir = '{distdir}'")
    print(f"cfgfile = '{cfgfile}'")
    print("---")
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = os.path.join(tmp, "dist")
        sp = _spinner("Copying static files")
        sp.start()
        shutil.copytree(srcdir, tmpdir)
        sp.stop()
        sp = _spinner("Rendering")
        sp.start()
        env = Environment(loader=FileSystemLoader(tpldir, encoding="utf8"))
        env.globals = globals
        with open(cfgfile) as f:
            config = toml.load(f)
        for item in config.values():
            path = os.path.join(tmpdir, item["path"])
            tpl = env.get_template(item["template"])
            if "params" in item:
                params = item["params"]
            else:
                params = {}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(tpl.render(params))
        sp.stop()
        sp = _spinner("Copying all files to distdir")
        sp.start()
        if os.path.isfile(distdir):
            os.remove(distdir)
        if os.path.isdir(distdir):
            shutil.rmtree(distdir)
        shutil.copytree(tmpdir, distdir)
        sp.stop()


def serve(
    host="0.0.0.0",
    port=8000,
    srcdir="./src",
    tpldir="./templates",
    distdir="./dist",
    cfgfile="./config.toml",
    globals={},
):
    print("---")
    print(f"srcdir  = '{srcdir}'")
    print(f"tpldir  = '{tpldir}'")
    print(f"distdir = '{distdir}'")
    print(f"cfgfile = '{cfgfile}'")
    print("---")
    hashes = {}

    class EventHandler(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.event_type == "closed":
                return
            if event.event_type == "modified":
                if event.is_directory:
                    return
                if os.path.isfile(event.src_path):
                    with open(event.src_path, "rb") as f:
                        if (
                            hashes.get(event.src_path)
                            == hashlib.md5(f.read()).hexdigest()
                        ):
                            return
            if os.path.isfile(event.src_path):
                with open(event.src_path, "rb") as f:
                    hashes[event.src_path] = hashlib.md5(f.read()).hexdigest()
            else:
                hashes.pop(event.src_path, None)
            print(
                "\033[1m - Change detected: '{}' {}. Regenerating.\033[m".format(
                    event.src_path, event.event_type
                )
            )
            with redirect_stdout(open(os.devnull, "w")):
                generate(srcdir, tpldir, distdir, cfgfile, globals)

    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, srcdir, recursive=True)
    observer.schedule(event_handler, tpldir, recursive=True)
    observer.schedule(event_handler, cfgfile)
    try:
        observer.start()
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler, directory=distdir
        )
        with socketserver.TCPServer((host, port), handler) as httpd:
            httpd.allow_reuse_address = True
            print(
                "\033[1m - "
                + f"Serving on {host} port {port} (http://{host}:{port}/) ...\033[m"
            )
            print(
                "\033[31;1m - This is a development server. "
                + "Do not use it in a production deployment.\033[m"
            )
            with redirect_stdout(open(os.devnull, "w")):
                generate(srcdir, tpldir, distdir, cfgfile, globals)
            print("\033[1m - Generated.\033[m")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[1m - Exiting.\033[m")
        observer.stop()
    observer.join()
