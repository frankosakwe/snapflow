# coding: utf-8
"""
SnapFlow Setup Configuration
Fast database snapshot and restore tool for development workflows
"""
import os
import re
from setuptools import setup, find_packages


def get_version():
    """Extract version from app.py"""
    init_file = os.path.join(
        os.path.dirname(__file__), 'snapflow', 'app.py'
    )
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
        version_match = re.search(
            r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
            content,
            re.MULTILINE
        )
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


def get_long_description():
    """Read README for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='snapflow',
    version=get_version(),
    description='Lightning-fast database snapshot and restore tool for development',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/quantumdb/snapflow',
    project_urls={
        'Bug Reports': 'https://github.com/quantumdb/snapflow/issues',
        'Source': 'https://github.com/quantumdb/snapflow',
        'Documentation': 'https://github.com/quantumdb/snapflow#readme',
    },
    author='QuantumDB Team',
    author_email='support@quantumdb.dev',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'examples']),
    entry_points={
        'console_scripts': [
            'snapflow=snapflow.cli:main',
        ],
    },
    python_requires='>=3.8',
    install_requires=[
        'PyYAML>=6.0',
        'SQLAlchemy>=1.4.0,<3.0.0',
        'humanize>=4.0.0',
        'schema>=0.7.5',
        'click>=8.0.0',
        'SQLAlchemy-Utils>=0.38.0',
        'psutil>=5.9.0',
    ],
    extras_require={
        'postgresql': ['psycopg2-binary>=2.9.0'],
        'mysql': ['PyMySQL>=1.0.0'],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-mock>=3.10.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'isort>=5.12.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Database',
        'Topic :: Software Development',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='database snapshot postgresql mysql development devops backup restore',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
)
