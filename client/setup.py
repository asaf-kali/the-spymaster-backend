from setuptools import find_packages, setup

setup(
    name="the-spymaster-api",
    version="1.1.4",
    description="Python client implementation for The Spymaster HTTP backend.",
    author="Asaf Kali",
    author_email="akali93@gmail.com",
    url="https://github.com/asaf-kali/the-spymaster-backend",
    packages=find_packages(),
    install_requires=[
        "codenames~=1.1",
        "the_spymaster_util~=1.10",
        "the_spymaster_solvers_client~=1.0",
        "pydantic~=1.9",
        "requests~=2.28",
    ],
    include_package_data=True,
)