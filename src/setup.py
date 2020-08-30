from setuptools import setup, find_packages
import os

__version__ = '0.0.1'


def get_long_description(filename):
    root_dir = os.path.abspath(os.path.curdir)
    if root_dir.endswith('/src'):
        root_dir = root_dir.replace('/src', '')
    full_path = os.path.join(root_dir, filename)
    if not os.path.exists(full_path):
        raise ValueError(f'{filename} could not be found at {full_path}')

    with open(full_path) as f:
        description = f.read()

    return description


setup(
    name='telegramio',
    packages=find_packages(exclude=['tests']),
    version=__version__,
    description='Simple and Limited async Telegram Client',
    long_description=get_long_description('README.md'),
    author='Victor Klapholz',
    author_email='victor.klapholz@gmail.com',
    url='https://github.com/vklap/py_gram',
    keywords='Limited Telegram Client',
    license='MIT',
    install_requires=['httpx>=0.14.1'],
    tests_require=[
        'pytest>=6.0.1',
        'pytest-httpx>=0.8.0',
        'pytest-asyncio>=0.14.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.8',
    ],
)
