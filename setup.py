from setuptools import setup, find_packages
from proxys import __version__

setup(name="proxys",
      version=__version__,
      description="get free proxy regularly peer 10 minutes",
      long_description="",
      url="https://github.com/zuoxiaolei/proxys",
      author="zuoxiaolei",
      author_email="1905561110@qq.com",
      license="MIT License",
      keywords="proxy",
      packages=find_packages(),
      include_package_data=True,
      platforms='any',
      python_requires=">=3",
      install_requires=[],
      )
