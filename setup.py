from setuptools import setup, find_packages
from proxys import (__version__, __title__, __description__,
                    __url__, __author__, __author_email__,
                    __license__)

install_requires = ["html5lib>=1.1",
                    'requests',
                    'beautifulsoup4',
                    'tqdm',
                    'retrying']
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()
setup(name=__title__,
      version=__version__,
      description=__description__,
      long_description=readme,
      long_description_content_type="text/markdown",
      zip_safe=False,
      url=__url__,
      author=__author__,
      author_email=__author_email__,
      license=__license__,
      keywords="proxy",
      packages=find_packages(),
      include_package_data=True,
      platforms='any',
      python_requires=">=3",
      install_requires=install_requires,
      project_urls={
          "Documentation": "https://github.com/zuoxiaolei/proxys",
          "Source": "https://github.com/zuoxiaolei/proxys",
      },
      )
