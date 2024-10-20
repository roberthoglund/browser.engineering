from setuptools import setup, find_packages

setup(
    name="browser.engineering",
    version="0.3.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "run-browser=browser.main:start",
        ],
    },
    install_requires=[
        # List your project dependencies here
    ],
)
