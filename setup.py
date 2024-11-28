from setuptools import setup, find_packages

setup(
    name="key-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'flask',
        'cryptography',
        'python-gnupg',
        'pycryptodome',
    ],
    python_requires='>=3.8',
    description="A secure key generation service",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/musicsms/key-generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
