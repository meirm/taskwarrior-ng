from setuptools import setup, find_packages

setup(
    name="taskwarrior-mcp",
    version="1.0.0",
    description="MCP Server for Taskwarrior integration",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "tasklib>=2.5.1",
        "mcp>=1.0.0", 
        "pydantic>=2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "taskwarrior-mcp=taskwarrior_mcp.server:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
