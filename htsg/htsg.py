import os
import shutil
import toml
from jinja2 import Environment, FileSystemLoader


def generate(
    srcdir="./src", tpldir="./templates", distdir="./dist", cfgfile="./config.toml"
):
    if os.path.isfile(distdir):
        os.remove(distdir)
    if os.path.isdir(distdir):
        shutil.rmtree(distdir)
    shutil.copytree(srcdir, distdir)
    env = Environment(loader=FileSystemLoader(tpldir, encoding="utf8"))
    with open(cfgfile) as f:
        config = toml.load(f)
    for item in config.values():
        path = os.path.join(distdir, item["path"])
        tpl = env.get_template(item["template"])
        if "params" in item:
            params = item["params"]
        else:
            params = {}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(tpl.render(params))
