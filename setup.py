from setuptools import setup, find_packages

# Read dependencies from requirements.txt
with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="SearchGPT_Searx",
    version="0.1",
    description="A modified version of SearchGPT using the Searx API",
    author="ProfSchurrie",
    url="https://github.com/ProfSchurrie/SearchGPT-Searx",
    license="MIT",
    packages=find_packages(where="src"),  # Specify src as the root for packages
    package_dir={"": "src"},  # Tell setuptools to look for packages in src
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
