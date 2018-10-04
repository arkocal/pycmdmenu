import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

print(setuptools.find_packages())

setuptools.setup(
    name="cmdmenu",
    version="0.1.01",
    author="Ali Rasim Kocal",
    author_email="arkocal@gmail.com",
    description="A library for creating hierarchical command line arg menus.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arkocal/pycmdmenu.git",
    py_modules=["cmdmenu"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
