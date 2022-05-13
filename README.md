# htsg - another SSG
"htsg" is a minimal SSG (Static Site Generator).  
This helps creating PURE HTML sites.

## Requirements
- Python3 (3.6+)

## Install

```
pip install htsg
```

## Usage
Here is a brief explanation. Also read the source.

### Example
visit [example](example)

### Generate site
Run in shell:

```
htsg
```

Run `htsg -h` to show more options.

Or, you can use in Python script:

```
import htsg

astdir = "./assets"
tpldir = "./templates"
distdir = "./dist"
cfgfile = "./config.toml"

htsg.generate(astdir, tpldir, distdir, cfgfile)
```

### Run development server
For developping, htsg has HTTP server. It watches files and regenerates site when sources changed.  
Run in shell:

```
htsg -s
```

Run `htsg -h` to show more options.

Or, in Python script:

```
import htsg

host = "0.0.0.0"
port = 8000
astdir = "./assets"
tpldir = "./templates"
distdir = "./dist"
cfgfile = "./config.toml"

htsg.serve(host, port, astdir, tpldir, distdir, cfgfile)
```

## Release note
### [v1.0.0](https://github.com/laddge/htsg/releases/tag/v1.0.0) (2022/05/13)
Initial release

## License
This project is under the MIT-License.  
See also [LICENSE](LICENSE).

## Author
Laddge
