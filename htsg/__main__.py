import argparse
from . import generate
from . import serve
from . import __version__


parser = argparse.ArgumentParser(
    prog="htsg",
    description="htsg - Python3 site generator using Jinja2"
)
parser.add_argument(
    "-s", "--serve",
    action='store_true',
    help="serve development server"
)
parser.add_argument(
    "--srcdir",
    default="./src",
    help="source directory (default: './src')"
)
parser.add_argument(
    "--tpldir",
    default="./templates",
    help="template directory (default: './templates')",
)
parser.add_argument(
    "--distdir",
    default="./dist",
    help="distribution directory (default: './dist')"
)
parser.add_argument(
    "--cfgfile",
    default="./config.toml",
    help="configuration file (default: './config.toml')"
)
parser.add_argument(
    "--globals",
    default={},
    help="global variables (default: {})",
    type=dict
)
parser.add_argument(
    "--version",
    action='store_true',
    help="show version"
)
group = parser.add_argument_group("optional arguments for '--serve'")
group.add_argument(
    "--host",
    default="0.0.0.0",
    help="host address (default: '0.0.0.0')"
)
group.add_argument(
    "--port",
    default=8000,
    help="port (default: 8000)",
    type=int
)
args = parser.parse_args()
if args.version:
    print(f"htsg version {__version__}")
else:
    params = vars(args)
    params.pop("version")
    if args.serve:
        params.pop("serve")
        serve(**params)
    else:
        params.pop("serve")
        params.pop("host")
        params.pop("port")
        generate(**params)
