from setuptools import find_packages, setup

setup(
      name='owasp-zap-historic',
      version="0.1.0",
      description='Custom report to display owasp zap historical execution records',
      long_description='OWASP ZAP Historic is custom report to display historical execution'
                       ' records using MySQL + Flask',
      classifiers=[
          'Framework :: Robot Framework',
          'Programming Language :: Python',
          'Topic :: Software Development :: Testing',
      ],
      keywords='owasp zap historical execution report',
      author='Neil Howell',
      author_email='neiljhowell@gmail.com',
      url='https://github.com/Accruent/owasp-zap-historic',
      license='',

      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'config',
          'flask',
          'bcrypt',
          'flask-mysqldb',
          'pytz'
      ],
      entry_points={
          'console_scripts': [
              'owaspzaphistoric=owasp_zap_historic.app:main',
          ]
      },
)
