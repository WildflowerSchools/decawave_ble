from setuptools import setup

setup(
    name='decawave_ble',
    packages=['decawave_ble'],
    version='0.8.0',
    include_package_data=True,
    description='Python toolset for working with and configuring the Decawave DWM1000 devices',
    long_description=open('README.md').read(),
    url='https://github.com/WildflowerSchools/decawave_ble',
    author='tcquinn',
    author_email='tcquinn@wildflowerschools.org',
    install_requires=[
        'bluepy',
        'bitstruct'
    ],
    extras_require={
        's3': [
            'boto3',
        ],
    },
    keywords=['bluetooth'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
