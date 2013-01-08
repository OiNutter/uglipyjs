from distutils.core import setup

setup(name='UgliPyJS',
      version='0.2',
      description='Python wrapper for Uglify-JS library.',
      author='Will McKenzie',
      author_email='will@oinutter.co.uk',
      packages=['uglipyjs'],
      package_dir={'uglipyjs': 'uglipyjs'},
      package_data={
       	'uglipyjs': ['*.js'],
     },
     requires=['PyV8','ordereddict','PyExecJS']
     )
