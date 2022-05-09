import os
import shutil
import tempfile
import http.server
import socketserver
import functools
import toml
from jinja2 import Environment, FileSystemLoader
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def generate(
    srcdir="./src",
    tpldir="./templates",
    distdir="./dist",
    cfgfile="./config.toml",
    globals={},
):
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = os.path.join(tmp, "dist")
        shutil.copytree(srcdir, tmpdir)
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
        if os.path.isfile(distdir):
            os.remove(distdir)
        if os.path.isdir(distdir):
            shutil.rmtree(distdir)
        shutil.copytree(tmpdir, distdir)


def serve(
    host="0.0.0.0",
    port=8000,
    srcdir="./src",
    tpldir="./templates",
    distdir="./dist",
    cfgfile="./config.toml",
    globals={},
):
    class EventHandler(FileSystemEventHandler):
        def on_any_event(self, event):
            print(
                "\033[1m - Change detected: '{}' {}.\033[m".format(
                    event.src_path, event.event_type
                )
            )
            generate(srcdir, tpldir, distdir, cfgfile, globals)

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
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[1m - Exiting.\033[m")
        observer.stop()
    observer.join()
