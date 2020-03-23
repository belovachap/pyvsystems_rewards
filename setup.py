import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyvsystems_rewards',
    version='0.0.5',
    author='Chapman Shoop',
    author_email='chapman.shoop@gmail.com',
    description='A library for calculating v.systems supernode rewards',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/belovachap/pyvsystems_rewards',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
