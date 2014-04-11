import PyV8
import json
import os
import io
from chardet.universaldetector import UniversalDetector

class UglipyJS:

    Error = execjs.Error

    # Default options for compilation
    __DEFAULTS__ = {
    	"encoding": "utf8",
        "warnings": False,
        "mangle": {}, # Mangle variable and function names, use :vars to skip function mangling
        "from_string": False,
        "source_root": None, # The URL of the directory which contains :source_filename
        "input_source_map": None, # The contents of the source map describing the input
        "output_source_map": None, # The output filename for the minified source map

        # output options
        "output": {
            "indent_start"  : 0,     # start indentation on every line (only when 'beautify')
            "indent_level"  : 4,     # indentation level (only when `beautify`)
            "quote_keys"    : False, # quote all keys in object literals?
            "space_colon"   : True,  # add a space after colon signs?
            "ascii_only"    : False, # output ASCII-safe? (encodes Unicode characters as ASCII)
            "inline_script" : False, # escape "</script"?
            "width"         : 80,    # informative maximum line width (for beautified output)
            "max_line_len"  : 32000, # maximum line length (for non-beautified output)
            #"ie_proof"      : True,  # output IE-safe code?
            "beautify"      : False, # beautify output?
            "bracketize"    : False, # use brackets every time?
            "comments"      : False, # output comments?
            "semicolons"    : True   # use semicolons to separate statements? (otherwise, newlines)
        },

        # compressor options
        "compressor": {
            "sequences"     : True,  # join consecutive statemets with the "comma operator"
            "properties"    : True,  # optimize property access: a["foo"] -> a.foo
            "dead_code"     : True,  # discard unreachable code
            "drop_debugger" : True,  # discard "debugger" statements
            "unsafe"        : False, # some unsafe optimizations (see below)
            "conditionals"  : True,  # optimize if-s and conditional expressions
            "comparisons"   : True,  # optimize comparisons
            "evaluate"      : True,  # evaluate constant expressions
            "booleans"      : True,  # optimize boolean expressions
            "loops"         : True,  # optimize loops
            "unused"        : True,  # drop unused variables/functions
            "hoist_funs"    : True,  # hoist function declarations
            "hoist_vars"    : False, # hoist variable declarations
            "if_return"     : True,  # optimize if-s followed by return/continue
            "join_vars"     : True,  # join var declarations
            "cascade"       : True,  # try to cascade 'right' into 'left' in sequences
            "side_effects"  : True,  # drop side-effect-free statements
            "warnings"      : True,  # warn about potentially dangerous optimizations/code
            "global_defs"   : {}     # global definitions
        }
        
    }

    source_path = os.path.join(os.path.dirname(__file__), 'uglify.js')
    source_map_path = os.path.join(os.path.dirname(__file__), 'source-map.min.js')
    es5_fallback_path = os.path.join(os.path.dirname(__file__), 'es5.js')

    # Initialize new context for UgliPyJS with given options
    #
    # options - Hash of options to override UgliPyJS.DEFAULTS
    def __init__(self, options = None):
        self._options = UglipyJS.__DEFAULTS__

        if options:
            output = None
            compressor = None

            if "output" in options:
                output = self._options['output']
                output.update(options['output'])
                del self._options['output']
                del options['output']

            if "compressor" in options:
                compressor = self._options['compressor']
                compressor.update(options['compressor'])
                del self._options['compressor']
                del options['compressor']

            self._options.update(options)

            if output:
                self._options['output'] = output            

            if compressor:
                self._options['compressor'] = compressor

        self.env = ";\n".join([
                io.open(UglipyJS.es5_fallback_path, "r",encoding=self._options['encoding']).read(),
                io.open(UglipyJS.source_map_path, "r",encoding=self._options['encoding']).read(),
                "var MOZ_SourceMap = this.sourceMap",
                io.open(UglipyJS.source_path, "r",encoding=self._options['encoding']).read()
            ])

        self.env.replace(';;',';')
        self._context = PyV8.JSContext()

    def compile(self,source):
        return self.really_compile(source,False)

    def compile_with_map(self,source):
        return self.really_compile(source,True)


    # Minifies JavaScript code
    #
    # source should be a String or IO object containing valid JavaScript.
    #
    # Returns minified code as String
    def really_compile(self,source,generate_map):   

        #source = source.replace('\\xa0', ' ')
        #source = source.replace('\t',' ')

        js = """var files = %s,
                    options = UglifyJS.defaults(%s, {
                        spidermonkey : false,
                        outSourceMap : null,
                        sourceRoot   : null,
                        inSourceMap  : null,
                        fromString   : false,
                        warnings     : false,
                        mangle       : {},
                        output       : null,
                        compress     : {}
                    });

                UglifyJS.base54.reset();

                // 1. parse
                var toplevel = null,
                    sourcesContent = {};

                if (typeof files == "string")
                    files = [ files ];
            
                files.forEach(function(file){
                    var code = file
                    
                    sourcesContent[file] = code;
                    toplevel = UglifyJS.parse(code, {
                        filename: options.fromString ? "?" : file,
                        toplevel: toplevel
                    });
                });

                // 2. compress
                if (options.compress) {
                    var compress = { warnings: options.warnings };
                    UglifyJS.merge(compress, options.compress);
                    toplevel.figure_out_scope();
                    var sq = UglifyJS.Compressor(compress);
                    toplevel = toplevel.transform(sq);
                }

                // 3. mangle
                if (options.mangle) {
                    toplevel.figure_out_scope();
                    toplevel.compute_char_frequency();
                    toplevel.mangle_names(options.mangle);
                }

                // 4. output
                var inMap = options.inSourceMap;
                var output = {};
                if (typeof options.inSourceMap == "string") {
                    inMap = options.inSourceMap;
                }

                if (options.outSourceMap) {
                    output.source_map = UglifyJS.SourceMap({
                        file: options.outSourceMap,
                        orig: inMap,
                        root: options.sourceRoot
                    });

                    if (options.sourceMapIncludeSources) {
                        for (var file in sourcesContent) {
                            if (sourcesContent.hasOwnProperty(file)) {
                                options.source_map.get().setSourceContent(file, sourcesContent[file]);
                            }
                        }
                    }

                }

                if (options.output) {
                    UglifyJS.merge(options.output,output);
                }

                var stream = UglifyJS.OutputStream(output);
                toplevel.print(stream);
                return {
                    code : stream + "",
                    map  : output.source_map + ""
                };"""

        options = {
            "inSourceMap": self._options['input_source_map'],
            "outSourceMap": self._options['output_source_map'],
            "sourceRoot": self._options['source_root'],
            "warnings": self._options['warnings'],
            "mangle": not not self._options['mangle'],
            "output": self._options['output'],
            "compress": self._options['compressor']
        }

        self._context.enter()

        #response = self._context.exec_(js % (json.dumps(source),json.dumps(options)))
        js = js % (json.dumps(source),json.dumps(options))
        response = self._context.eval("%s;\n%s" % (self.env,js))
        response[u'code'] = response[u'code'].encode(self._options['encoding'])

        return response

# Minifies JavaScript code using implicit context.
#
# source should be a String or IO object containing valid JavaScript.
# options contain optional overrides to UgliPyJS.DEFAULTS
#
# Returns minified code as String
def compile(source, options = None):
    instance = UglipyJS(options or {})
    return instance.compile(source)

# Minifies JavaScript code and generates a source map using implicit context.
#
# source should be a String or IO object containing valid JavaScript.
# options contain optional overrides to Uglifier::DEFAULTS
#
# Returns a pair of [minified code as String, source map as a String]
def compile_with_map(source,options=None):
    instance = UglipyJS(options or {})
    return instance.compile_with_map(source)
