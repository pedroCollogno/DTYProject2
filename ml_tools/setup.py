from setuptools import setup

setup(
    name='ml_tools',
    version='1.0',
    description='A useful module to use ml',
    author='Paris Digital Lab',
    packages=[
        'ml_tools',
        'ml_tools.clustering',
        'ml_tools.utils',
        'ml_tools.utils.gen',
    ],
    package_dir={
        'ml_tools': 'src',
        'ml_tools.clustering': 'src/clustering',
        'ml_tools.utils': 'src/utils',
        'ml_tools.utils.gen': 'src/utils/gen',
    },
    install_requires=[
        'np',
        'matplotlib',
        'scikit-learn',
        'progressbar',
        'PyGeodesy',
        'protobuf'
    ],  # external packages as dependencies
)
