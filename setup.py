from setuptools import setup, find_packages
import os

version = '1.1.dev0'

setup(name='ilo.contentrules',
      version=version,
      description="Content rules for ILO",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ilo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.contentrules.mailtolocalrole'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
