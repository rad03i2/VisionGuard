from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="visionguard",
    version="1.0.0",
    author="Radwan Abdulhadi Ahmed",
    description="Local computer-vision toolkit for camera ingestion, object detection, tracking, zones, alerts, and a web dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rad03i2/VisionGuard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.23.0",
        "opencv-python>=4.8.0",
        "ultralytics>=8.1.0",
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.0",
        "pyyaml>=6.0.1",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={"console_scripts": ["visionguard=visionguard.cli:main"]},
    project_urls={
        "Source": "https://github.com/rad03i2/VisionGuard",
        "Issues": "https://github.com/rad03i2/VisionGuard/issues",
    },
)
