import os
import time
import threading
import shutil
import tempfile
import http.server
import socketserver
import functools
import hashlib
import toml
from jinja2 import Environment, FileSystemLoader
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class _spinner:
    """_spinner.
    """

    def __init__(self, prefix, quiet):
        """__init__.

        Parameters
        ----------
        prefix :
            prefix
        quiet :
            quiet
        """
        self.prefix = prefix
        self.quiet = quiet
        self.done = False

    def _loop(self):
        """_loop.
        """
        if self.quiet:
            return
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
        """start.
        """
        if self.quiet:
            return
        self.done = False
        th = threading.Thread(target=self._loop)
        th.setDaemon(True)
        th.start()

    def stop(self):
        """stop.
        """
        if self.quiet:
            return
        self.done = True
        print(f"\r{self.prefix} ... done.")


def generate(
    astdir="./assets",
    tpldir="./templates",
    distdir="./dist",
    cfgfile="./config.toml",
    cfgdict={},
    quiet=False,
):
    """generate.

    Parameters
    ----------
    astdir :
        astdir
    tpldir :
        tpldir
    distdir :
        distdir
    cfgfile :
        cfgfile
    cfgdict :
        cfgdict
    quiet :
        quiet
    """
    if not quiet:
        print("---")
        print(f"astdir  = '{astdir}'")
        print(f"tpldir  = '{tpldir}'")
        print(f"distdir = '{distdir}'")
        print("---")
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = os.path.join(tmp, "dist")
        sp = _spinner("Copying assets", quiet)
        sp.start()
        shutil.copytree(astdir, tmpdir)
        sp.stop()
        sp = _spinner("Rendering", quiet)
        sp.start()
        if cfgdict:
            config = cfgdict
        else:
            with open(cfgfile) as f:
                config = toml.load(f)
        env = Environment(loader=FileSystemLoader(tpldir, encoding="utf8"))
        if "global" in config:
            env.globals = config.pop("global")
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
        sp = _spinner("Copying all files to distdir", quiet)
        sp.start()
        if os.path.isfile(distdir):
            os.remove(distdir)
        if os.path.isdir(distdir):
            shutil.rmtree(distdir)
        shutil.copytree(tmpdir, distdir)
        sp.stop()


class _req_handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        http.server.SimpleHTTPRequestHandler.end_headers(self)


def serve(
    host="0.0.0.0",
    port=8000,
    astdir="./assets",
    tpldir="./templates",
    distdir="./dist",
    cfgfile="./config.toml",
    cfgdict={},
):
    """serve.

    Parameters
    ----------
    host :
        host
    port :
        port
    astdir :
        astdir
    tpldir :
        tpldir
    distdir :
        distdir
    cfgfile :
        cfgfile
    cfgdict :
        cfgdict
    """
    print("---")
    print(f"astdir  = '{astdir}'")
    print(f"tpldir  = '{tpldir}'")
    print(f"distdir = '{distdir}'")
    print("---")
    hashes = {}

    class EventHandler(FileSystemEventHandler):
        """EventHandler.
        """

        def on_any_event(self, event):
            """on_any_event.

            Parameters
            ----------
            event :
                event
            """
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
            for _ in range(4):
                try:
                    generate(astdir, tpldir, distdir, cfgfile, cfgdict, True)
                except Exception:
                    pass
                else:
                    return
            generate(astdir, tpldir, distdir, cfgfile, cfgdict, True)

    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, astdir, recursive=True)
    observer.schedule(event_handler, tpldir, recursive=True)
    observer.schedule(event_handler, cfgfile)
    try:
        observer.start()
        handler = functools.partial(
            _req_handler, directory=distdir
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
            generate(astdir, tpldir, distdir, cfgfile, cfgdict, True)
            print("\033[1m - Generated.\033[m")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[1m - Exiting.\033[m")
        observer.stop()
    observer.join()
