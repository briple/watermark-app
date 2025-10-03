from setuptools import setup, find_packages

setup(
    name='watermark-app',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'Pillow',   # Image processing library
    ],
    entry_points={
        'gui_scripts': [
            'watermark-app=main:main',  # Assuming main function in main.py
        ],
    },
    author='LiuLulin',
    author_email='522025320107@smail.nju.edu.cn',
    description='A simple application to add watermarks to images.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/briple/watermark-app',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)