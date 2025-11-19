from setuptools import setup, find_packages

setup(
    name="status-monitor",
    version="1.0.0",
    author="Prakhar Bhartiya",
    author_email="prakharbhartiya01@gmail.com",
    description="A modular application for tracking and logging service updates from multiple status pages.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "aiohttp",
        "asyncio"
    ],
    entry_points={
        "console_scripts": [
            "status-monitor=main:main_async",  # Change to main_sync if you want sync entry point
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)