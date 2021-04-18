from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='IPC',
  version='0.0.1',
  description='A small lightweight networking module',
  long_description=open('README.md').read(),
  long_description_content_type = "text/markdown",
  url = "https://github.com/Seniatical/IPC/", 
  project_urls={
   "Documentation": "https://github.com/Seniatical/IPC/docs/docs.md",
   "Issues tracker": "https://github.com/Seniatical/IPC/issues",
   },
  author='Seniatical',
  license='MIT', 
  classifiers=classifiers,
  keywords='Networking,Client,Server,Sockets,Python', 
  packages=find_packages(),
  install_requires=['click', 'aiofiles'] 
)
