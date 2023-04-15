from setuptools import find_packages, setup

setup(
    name="the-spymaster-api",
    version="1.8.1",
    description="Python client implementation for The Spymaster HTTP backend.",
    author="Asaf Kali",
    author_email="asaf.kali@mail.huji.ac.il",
    url="https://github.com/asaf-kali/the-spymaster-backend",
    packages=find_packages(),
    install_requires=[
        "codenames~=2.0",
        "the_spymaster_util~=3.0",
        "the_spymaster_solvers_client~=1.7",
        "pydantic~=1.9",
        "requests~=2.28",
    ],
    include_package_data=True,
)
