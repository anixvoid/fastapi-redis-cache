from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastapi-redis-cache",
    version="0.1.0",
    author="anixvoid",
    description="Custom implementation cache decorator for fastapi endpoints",
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anixvoid/fastapi-redis-cache",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.13",
    install_requires=[],
    requires=[
        "uvicorn",
        "fastapi",
        "redis",
        "pickle",
        "hashlib",
        "datetime"
    ],
    keywords="fastapi redis cache",
    project_urls={
        "Bug Tracker": "https://github.com/anixvoid/fastapi-redis-cache/issues",
        "Documentation": "https://github.com/anixvoid/fastapi-redis-cache/wiki",
        "Source Code": "https://github.com/anixvoid/fastapi-redis-cache",
    },
)