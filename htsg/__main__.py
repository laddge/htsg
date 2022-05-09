import argparse
from . import generate as _generate
from . import serve as _serve
from . import __version__


def generate():
    parser = argparse.ArgumentParser(
        prog="htsg",
        description="htsg - Python3 site generator using Jinja2"
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
    args = parser.parse_args()
    if args.version:
        print(f"htsg version {__version__}")
    else:
        _generate(**vars(args))


def serve():
    parser = argparse.ArgumentParser(
        prog="htsg.serve",
        description="htsg.serve - Development server for htsg"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="host address (default: '0.0.0.0')"
    )
    parser.add_argument(
        "--port",
        default=8000,
        help="port (default: 8000)",
        type=int
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
    args = parser.parse_args()
    if args.version:
        print(f"htsg version {__version__}")
    else:
        _serve(**vars(args))


if __name__ == "__main__":
    generate()
