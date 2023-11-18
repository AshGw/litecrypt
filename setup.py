from setuptools import find_packages, setup

with open("scripts/setup/minimal_requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md") as f:
    markdown_description = f.read()

setup(
    name="litecrypt",
    version="0.2.1",
    author="Ashref Gwader",
    author_email="AshrefGw@proton.me",
    python_requires=">=3.7",
    description="Library to Simplify Encryption and Data Protection",
    long_description_content_type="text/markdown",
    long_description=markdown_description,
    url="https://github.com/AshGw/litecrypt.git",
    packages=find_packages(
        exclude=["important", "docker-build", ".github", "docs", "tests"]
    ),
    package_data={
        "litecrypt": ["**"],
    },
    exclude_package_data={
        "": [".gitignore", "LICENSE", "README.md"],
    },
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=[
        "Cryptography application",
        "File encryption",
        "Secure encryption",
        "Cryptography library",
        "AES-256",
        "Data protection",
        "Secure file storage",
        "Key management",
        "Data protection",
        "Encryption tools",
        "Secure data storage",
    ],
)
