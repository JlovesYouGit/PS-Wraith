from setuptools import setup, find_packages

_ = setup(
    name="usb-scanner",
    version="1.0.0",
    description="USB device scanner utility",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=[
        "pyusb>=1.3.0",
        "libusb1>=3.3.0",
        "pywinusb>=0.4.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "usb-scanner=src.usb_scanner:list_usb_devices",
        ],
    },
)