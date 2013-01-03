import execjs
import json
import os
import io
import re

class UglipyJS:

	Error = execjs.Error

	# Default options for compilation
	__DEFAULTS__ = {
    'encoding':'utf8',
		'mangle': True, # Mangle variable and function names, use :vars to skip function mangling
		'except': ["$super"], # Variable names to be excluded from mangling
		'max_line_length': 32 * 1024, # Maximum line length
		'squeeze': True, # Squeeze code resulting in smaller, but less-readable code
		'seqs': True, # Reduce consecutive statements in blocks into single statement
		'dead_code': True, # Remove dead code (e.g. after return)
		'lift_vars': False, # Lift all var declarations at the start of the scope
		'unsafe': False, # Optimizations known to be unsafe in some situations
		'copyright': True, # Show copyright message
		'ascii_only': False, # Encode non-ASCII characters as Unicode code points
		'inline_script': False, # Escape </script
		'quote_keys': False, # Quote keys in object literals
		'define': {}, # Define values for symbol replacement
		'beautify': False, # Ouput indented code
		'beautify_options': {
			'indent_level': 4,
			'indent_start': 0,
			'space_colon': False
		},
		'source_filename': None, # The filename of the input
		'source_root': None, # The URL of the directory which contains :source_filename
		'output_filename': None, # The filename or URL where the minified output can be found
		'input_source_map': None, # The contents of the source map describing the input
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
		self._context = execjs.compile(io.open(UglipyJS.es5_fallback_path, "r",encoding=self._options['encoding']).read() + io.open(UglipyJS.source_path, "r",encoding=self._options['encoding']).read())

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
		source = unicode(source,self._options['encoding']) if isinstance(source,unicode) or isinstance(source,str) else source.read()

		source = source.replace('\t',' ')

		js = """var options = %s;
var source = options.source;
var ast = UglifyJS.parse(source, options.parse_options);
ast.figure_out_scope();

if (options.squeeze) {
	var compressor = UglifyJS.Compressor(options.compressor_options);
	ast = ast.transform(compressor);
	ast.figure_out_scope();
}

if (options.mangle) {
	ast.compute_char_frequency();
	ast.mangle_names(options.mangle_options);
}

var gen_code_options = options.gen_code_options;

if (options.generate_map) {
	var source_map = UglifyJS.SourceMap(options.source_map_options);
	gen_code_options.source_map = source_map;
}

var stream = UglifyJS.OutputStream(gen_code_options);

if (options.copyright) {
	var comments = ast.start.comments_before;
	for (var i = 0; i < comments.length; i++) {
		var c = comments[i];
		stream.print((c.type == "comment1") ? "//"+c.value+"\\n" : "/*"+c.value+"*/\\n");
	}
}

ast.print(stream);
if (options.generate_map) {
	return [stream.toString() + ";", source_map.toString()];
} else {
	return stream.toString() + ";";
}
				"""
	
		options = {
			"source":source,
			"generate_map":not not generate_map,
			"compressor_options":self.compressor_options(),
			"gen_code_options":self.gen_code_options(),
			"mangle_options":self.mangle_options(),
			"parse_options":self.parse_options(),
			"source_map_options":self.source_map_options(),
			"squeeze":self.should_squeeze(),
			"mangle":self.should_mangle(),
			"copyright":self.preserve_copyright(),


		}

		return self._context.exec_(js % json.dumps(options))

	def should_mangle(self):
		return not not self._options['mangle']
	
	def should_squeeze(self):
		return not not self._options['squeeze']
	
	def preserve_copyright(self):
		return not not self._options['copyright']
	
	def compressor_options(self):
		return {
			"sequences": self._options['seqs'],
			"dead_code": self._options['dead_code'],
			"unsafe": not self._options['unsafe'],
			"hoist_vars": self._options['lift_vars'],
			"global_defs": self._options['define'] or {}
		}
	
	def mangle_options(self):
		return {
			"except": self._options["except"],
		}

	def squeeze_options(self):
		return {
			"make_seqs": self._options["seqs"],
			"dead_code": self._options["dead_code"],
			"keep_comps": not self._options["unsafe"]
		}

	def gen_code_options(self):
		options = {
	 		 	"ascii_only": self._options["ascii_only"],
				"inline_script": self._options["inline_script"],
				"quote_keys": self._options["quote_keys"],
				"max_line_len": self._options["max_line_length"]
		}

		if self._options["beautify"]:
			options.update({"beautify": True})
			options.update(self._options["beautify_options"])
		
		return options

	def source_map_options(self):
		return {
			'file': self._options['output_filename'],
			'root': self._options['source_root'],
			'orig': self._options['input_source_map']
		}
	

	def parse_options(self):
		return {
				'filename': self._options['source_filename']
				}

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