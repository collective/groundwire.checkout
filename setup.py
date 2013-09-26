from setuptools import setup, find_packages

version = '1.0'

setup(name='groundwire.checkout',
      version=version,
      description="Example Add-on",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['groundwire'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.beaker',
          'getpaid.authorizedotnet',
          'getpaid.core >= 0.9.2',
          'getpaid.nullpayment',
          'five.globalrequest',
          'pycountry',
          'setuptools',
          'z3c.form',
          'collective.z3cform.datetimewidget',
          'zope.interface',
          'zope.schema',
          # -*- Extra requirements: -*-
      ],
      extras_require = {
          'test': [
                'unittest2',
                'plone.app.testing',
                ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
