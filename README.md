UgliPyJs
========

UgliPyJs is a port of the [uglifier][] gem for python. It wraps the
[UglifyJS][] minification tool allowing you to minify your Javascript
files from your Python code.

Install
-------

```bash
$ pip install uglipyjs
```

Usage
-----

To minify your javascript code:

``` python
import uglipyjs
js = open('blah.js','r').read()
uglipyjs.compile(js)
```

You can also minify with source map:

``` python
import uglipyjs
js = open('blah.js','r').read()
uglipyjs.compile_with_map(js)
```

If you need to override the defaults pass a dict of options as a second
parameter to the compile function:

``` python
import uglipyjs
js = open('blah.js','r').read()
uglipyjs.compile(js,{'mangle':False})
```

License
-------

Copyright 2012 Will McKenzie

UgliPyJs is licensed under the MIT License, please see the LICENSE file
for more details.

  [uglifier]: https://github.com/lautis/uglifier
  [UglifyJS]: https://github.com/mishoo/uglifyjs