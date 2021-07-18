import setuptools

requirements = []
with open('requirements.txt') as rtxt:
    requirements = rtxt.read().splitlines()

setuptools.setup(
    name="Discord-Bot",
    version="1.0.0",
    author="GigaClub",
    author_email="business@GigaClub.net",
    url="https://github.com/gigaclub/Discord-Bot",
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
    install_requires=requirements,
)