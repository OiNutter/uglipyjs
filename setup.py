from distutils.core import setup
import os

long_description = "Python wrapper for Uglify-JS library."
if os.path.exists('README.txt'):
      long_description = open('README.txt').read()

setup(name='UgliPyJS',
      version='0.2.3',
      url='https://github.com/OiNutter/uglipyjs',
      download_url='https://github.com/OiNutter/uglipyjs/tarball/master',
      description='Python wrapper for Uglify-JS library.',
      long_description=long_description,
      author='Will McKenzie',
      author_email='will@oinutter.co.uk',
      packages=['uglipyjs'],
      package_dir={'uglipyjs': 'uglipyjs'},
      package_data={
       	'uglipyjs': ['*.js'],
     },
     requires=['PyV8','ordereddict','PyExecJS'],
     license='MIT License',
     classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: JavaScript'
    ]
  )
