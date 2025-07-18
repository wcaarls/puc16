from setuptools import setup, find_packages

try:
    with open('README.md', 'r') as fh:
        long_description = fh.read()
except:
    long_description = ''

setup(name='puc16',
      version='0.2.0',
      description='Assembler and C compiler for the PUC16 processor',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/wcaarls/puc16',
      author='Wouter Caarls',
      author_email='wouter@puc-rio.br',
      license='GNU GPLv3+',
      classifiers=['Development Status :: 4 - Beta',
      'Environment :: Console',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      'Programming Language :: Python :: 3',
      'Topic :: Education',
      'Topic :: Software Development :: Assemblers',
      'Topic :: Software Development :: Compilers',
      ],
      keywords='assembler compiler educational risc processor',
      packages=find_packages(),
      package_data={'': ['*.grammar']},
      entry_points = {
        'console_scripts': ['as-puc16=puc16.asm:main',
                            'cc-puc16=puc16.cc:main']
      },
      extras_require={
        'vga': ['pygame', 'numpy']
      })
