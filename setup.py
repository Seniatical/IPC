from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: Apache License',
  'Programming Language :: Python :: 3'
]

setup(
  name='IPC',
  version='0.0.1',
  description='A small lightweight module to simulate a Client and Server setup',
  long_description=open('README.md').read(),
  long_description_content_type = "text/markdown",
  url = "https://github.com/Seniatical/IPC/", 
  project_urls={
   "Documentation": "https://github.com/Seniatical/IPC/",
   "Issues tracker": "https://github.com/Seniatical/IPC/issues",
   },
  author='Seniatical',
  author_email='smelted02@gmail.com',
  license='Apache', 
  classifiers=classifiers,
  keywords='Data-Types,Python', 
  packages=find_packages(),
  install_requires=['tqdm'] 
)
