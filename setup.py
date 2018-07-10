from distutils.core import setup

setup(
    name='pyrw',
    author='csm10495',
    author_email='csm10495@gmail.com',
    url='http://github.com/csm10495/pyrw',
    version='0.2d',
    packages=['pyrw'],
    license='MIT License',
    python_requires='>=2.7',
    long_description=open('README.md').read(),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    include_package_data = True,
    install_requires=[],
    #entry_points={
    #    'console_scripts': [
    #        'pyrw = ?' # todo... interactive?
    #    ]
    #},
)