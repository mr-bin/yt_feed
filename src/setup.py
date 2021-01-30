from setuptools import setup, find_packages

tests_require = [
    'pytest',
]

setup(name="yt_feed",
      version="0.0.1",
      author="mr_bin",
      description="",
      license="Private",
      url="https://github.com/mr-bin/yt_feed",
      packages=find_packages(),
      package_data={
          '': ['*.sh', '*.ini', '*.pem', '*.txt'],
          'configs': ['*.yaml']},
      install_requires=[
          'PyYAML',
          'python-telegram-bot',
          'python-youtube'
      ],
      extras_require={
          'tests': tests_require,
      },
      entry_points={
          'console_scripts':
              [
                  'manage.py = yt_feed.manage:main'
              ]
      },

      classifiers=[
          "Development Status :: 1 - Planning",
          "Environment :: Web Environment",
          "License :: Other/Proprietary License",
          "Operating System :: Unix",
          "Programming Language :: Python :: 3.8",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
          "Topic :: Multimedia :: Video :: Display",
      ],
      )
