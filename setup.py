from setuptools import setup

setup(
    name="the-spymaster-api",
    version="0.1.6",
    description="Python client implementation for The Spymaster HTTP backend.",
    author="Asaf Kali",
    author_email="akali93@gmail.com",
    url="https://github.com/asaf-kali/the-spymaster-backend",
    packages=["the_spymaster_api", "the_spymaster_api.structs"],
    install_requires=["codenames~=1.1", "pydantic~=1.9", "requests"],
    include_package_data=True,
)
