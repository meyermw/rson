The goal of the RSON project is to create a file format that is easy to edit, diff, and version control, that is a superset of [JSON](http://www.json.org/) and smaller than [YAML](http://www.yaml.org/spec/1.2/spec.html).

**New!!**  A [simplified version called rsonlite](http://pypi.python.org/pypi/rsonlite/0.1.0), which drops JSON compatibility, but is great for indented configuration files is now available.

There is a short manual available for RSON, and an example Python 2.x/3.x decoder is available.  See the [downloads section](http://code.google.com/p/rson/downloads/list) or use easy\_install or pip to get it from PyPI.  The example decoder is about as fast as the Python 2.6 JSON decoder.  It is much faster than the pure-Python PyYaml decoder v. 3.09, somewhat slower than the current subversion pure Python simplejson decoder, and markedly slower than simplejson or YAML C decoders.

> The example RSON decoder is quite flexible, and there is also an [example parser](http://groups.google.com/group/rson-discuss/browse_frm/thread/f1f6838dd8404917) for a superset of RSON that has XML semantics instead of JSON semantics.

To see an example of RSON in action, you can look at the default [rst2pdf](http://code.google.com/p/rst2pdf/) [default stylesheet](http://code.google.com/p/rst2pdf/source/browse/trunk/rst2pdf/styles/styles.style).

Project discussion and updates happens in the rson-discuss [google group](http://groups.google.com/group/rson-discuss).  Maybe at some point I will have time to add some more wiki pages and to improve the [manual](http://code.google.com/p/rson/wiki/Manual) [(PDF)](http://rson.googlecode.com/files/rson_0_06_manual.pdf).

The current version of RSON is 0.9, which has the following differences from 0.08:

  * Refactored, distributed as a package, placed under PyPI
  * Works with Python 3

0.08 had the following differences from 0.06:

  * No manual changes (manual is still at 0.06).
  * API enhanced to allow easier subclassing of some of the parser pieces.
  * rsonmac.py example added in tools (in subversion) to show example of macro and include file processing.

0.06 had the following differences from 0.05:

  * Trailing commas are no longer supported.  In RSON indented syntax, they are meaningless, and in JSON syntax, they are not necessary.
  * Keys for key/value pairs are restricted to strings.  Use-cases for more complicated keys are few and far between in configuration files.
  * The manual has been changed to reflect these changes, and also to improve the examples and syntax definitions.

0.05 had the following differences from 0.04:

  * No manual changes (manual is still at 0.04)
  * Some bugs fixed that affected the ability of client code to configure the handling of object types.

0.04 had the following differences from 0.03:

  * Cosmetic changes in the manual
  * A corner case where a correct document could incorrectly throw an exception was fixed.
  * The ability of client code to configure the handling of object and array types was improved.

0.03 had the following differences from 0.02:

  * Manual enhanced with more examples and syntax description
  * Code modified so that equal sign can be used with non-string scalars

0.02 was the first version with a manual.