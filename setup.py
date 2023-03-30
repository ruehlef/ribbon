import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

with open("VERSION", "r") as fh:
    VERSION = fh.read()

with open("requirements.txt", "r") as fh:
    REQUIREMENTS = fh.read().splitlines()

setuptools.setup(
    name="ribbon",
    version=VERSION,
    python_requires = '>=3.8',
    author="Sergei Gukov, Jim Halverson, Ciprian Manolescu, Fabian Ruehle",
    author_email="f.ruehle@northeastern.edu",
    description="A python program that detects ribbon knots",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ruehlef/ribbon",
    packages=["ribbon"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Linux, MacOS",
        "Topic :: Scientific/Engineering :: Mathematics"
        ],
    install_requires=REQUIREMENTS,
    package_data={'ribbon': ['*.so']},
)