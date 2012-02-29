import execjs
import json
import os

class UglipyJS:

	Error = execjs.Error

  	# Default options for compilation
  	__DEFAULTS__ = {
    	"mangle": True, # Mangle variable and function names, use :vars to skip function mangling
    	"toplevel": False, # Mangle top-level variable names
    	"except": ["$super"], # Variable names to be excluded from mangling
    	"max_line_length": 32 * 1024, # Maximum line length
    	"squeeze": True, # Squeeze code resulting in smaller, but less-readable code
    	"seqs": True, # Reduce consecutive statements in blocks into single statement
    	"dead_code": True, # Remove dead code (e.g. after return)
    	"lift_vars": False, # Lift all var declarations at the start of the scope
    	"unsafe": False, # Optimizations known to be unsafe in some situations
    	"copyright": True, # Show copyright message
    	"ascii_only": False, # Encode non-ASCII characters as Unicode code points
    	"inline_script": False, # Escape </script
    	"quote_keys": False, # Quote keys in object literals
    	"beautify": False, # Ouput indented code
    	"beautify_options": {
      		"indent_level": 4,
      		"indent_start": 0,
      		"space_colon": False
    	}
  	}

	source_path = os.path.join(os.path.dirname(__file__), 'uglify.js')
  	es5_fallback_path = os.path.join(os.path.dirname(__file__), 'es5.js')
  	
  	# Initialize new context for UgliPyJS with given options
  	#
  	# options - Hash of options to override UgliPyJS.DEFAULTS
  	def __init__(self, options = {}):
  		defaults = UglipyJS.__DEFAULTS__
  		self._options = UglipyJS.__DEFAULTS__
  		self._options.update(options)
  		self._context = execjs.compile(open(UglipyJS.es5_fallback_path, "r").read() + open(UglipyJS.source_path, "r").read())

  	# Minifies JavaScript code
 	#
  	# source should be a String or IO object containing valid JavaScript.
  	#
  	# Returns minified code as String
  	def compile(self,source):
  		source = str(source) if isinstance(source,str) else source.read()

  		js = []
  		js.append("var result = '';")
  		js.append("var source = " + json.dumps(source) + ";")
  		js.append("var ast = UglifyJS.parser.parse(source);")

  		if self._options["lift_vars"]:
  			js.append("ast = UglifyJS.uglify.ast_lift_variables(ast);")

  		if self._options["copyright"]:
  			js.append('var comments = UglifyJS.parser.tokenizer(source)().comments_before;' + 
      			'for (var i = 0; i < comments.length; i++) {' + 
        			'var c = comments[i];' +
        			'result += (c.type == "comment1") ? "//"+c.value+"\\n" : "/*"+c.value+"*/\\n";' + 
      			'}')

  		if self._options["mangle"]:
  			js.append("ast = UglifyJS.uglify.ast_mangle(ast, " + json.dumps(self.mangle_options()) + ");")

  		if self._options["squeeze"]:
  			js.append("ast = UglifyJS.uglify.ast_squeeze(ast, " + json.dumps(self.squeeze_options()) + ");")

  		if self._options["unsafe"]:
  			js.append("ast = UglifyJS.uglify.ast_squeeze_more(ast);")

  		js.append("result += UglifyJS.uglify.gen_code(ast, " + json.dumps(self.gen_code_options()) + ");")

  		if not self._options["beautify"] and self._options["max_line_length"]:
  			js.append("result = UglifyJS.uglify.split_lines(result, " + str(self._options["max_line_length"]) + ");")

  		js.append("return result;")

  		return self._context.exec_('\n'.join(js))

  	def mangle_options(self):
		options = {
			"toplevel": self._options["toplevel"],
			"defines": {},
			"except": self._options["except"],
			"no_functions": self._options["mangle"] == "vars"
			}

		return options

	def squeeze_options(self):
 		options = {
 			"make_seqs": self._options["seqs"],
 			"dead_code": self._options["dead_code"],
 			"keep_comps": not self._options["unsafe"]
 			}

 		return options

  	def gen_code_options(self):
  		options = {
  			"ascii_only": self._options["ascii_only"],
  			"inline_script": self._options["inline_script"],
  			"quote_keys": self._options["quote_keys"]
  			}

  		if self._options["beautify"]:
  			options.update({"beautify": True})
  			options.update(self._options["beautify_options"])
  		
  		return options
# Minifies JavaScript code using implicit context.
#
# source should be a String or IO object containing valid JavaScript.
# options contain optional overrides to UgliPyJS.DEFAULTS
#
# Returns minified code as String
def compile(source, options = {}):
	instance = UglipyJS(options)
	return instance.compile(source)