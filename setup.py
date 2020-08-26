"""Setup file for owaspzaphistoric."""
from setuptools import find_packages, setup
import version


with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()
    print(LONG_DESCRIPTION)

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name='owasp-zap-historic',
    version=version.VERSION,
    description='Custom report to display owasp zap historical execution records',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=[
        'Framework :: Robot Framework',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    keywords='owasp zap historical execution report',
    author='Neil Howell',
    author_email='neiljhowell@gmail.com',
    url='https://github.com/Accruent/owasp-zap-historic',
    license='GPL-3.0',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'owaspzaphistoric=owasp_zap_historic.app:main',
        ]
    },
)
