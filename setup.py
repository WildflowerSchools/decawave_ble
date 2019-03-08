from setuptools import setup, find_packages

setup(
    name='decawave_ble',
    packages=find_packages(),
    version='0.9.6',
    include_package_data=True,
    description='Python toolset for working with and configuring the Decawave DWM1000 devices',
    long_description=open('README.md').read(),
    url='https://github.com/WildflowerSchools/decawave_ble',
    author='tcquinn',
    author_email='tcquinn@wildflowerschools.org',
    install_requires=[
        'bluepy',
        'tenacity',
        'bitstruct',
        'pandas'
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
