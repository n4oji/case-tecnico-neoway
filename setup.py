from setuptools import setup, find_packages

setup(
    name="case-tecnico-neoway",
    version="1.0.0",
    description="Web scraper para dados do Discogs - Teste de Engenharia de Dados",
    author="n4oji",
    author_email="naoji.okamoto@gmail.com",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.12.2",
        "selenium>=4.15.2",
        "lxml>=4.9.3",
        "pytest>=7.4.3",
        "pytest-cov>=4.1.0",
        "webdriver-manager>=4.0.1",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8", 
            "mypy",
            "pre-commit",
        ]
    },
    entry_points={
        "console_scripts": [
            "discogs-scraper=main:main",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)