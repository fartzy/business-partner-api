import os
import setuptools


from brazilian_business_partner_api.config import config


class CleanBuildArtifacts(setuptools.Command):
    """Custom clean command to tidy up the project root."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        os.system("rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info")


with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIRED_PACKAGES = [
    "fastapi",
    "pandas",
    "psycopg2-binary",
]

setuptools.setup(
    name=config.APP_NAME,
    version=config.APP_VERSION,
    description="GraphQL API with Brazilian Companies Data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mike Artz",
    author_email="michaeleartz@gmail.com",
    include_package_data=True,
    packages=setuptools.find_packages(exclude=["test*"]),
    entry_points={
        "console_scripts": [
            "braz-bpa-cli=brazilian_business_partner_api.cmds.cli:cli",
        ],
    },
    cmdclass={"clean": CleanBuildArtifacts},
    install_requires=REQUIRED_PACKAGES,
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3",
    ],
    keywords="graphql brazil logistics",
)
