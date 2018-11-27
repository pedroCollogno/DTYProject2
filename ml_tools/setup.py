from setuptools import setup

setup(
    name='ml_tools',
    version='1.0',
    description='A useful module to use ml',
    author='Paris Digital Lab',
    include_package_data=True,
    packages=[
        'ml_tools',
        'ml_tools.clustering',
        'ml_tools.utils',
        'ml_tools.deep_learning',
        'ml_tools.utils.gen',
        'ml_tools.utils.config',
    ],
    package_dir={
        'ml_tools': 'src',
        'ml_tools.clustering': 'src/clustering',
        'ml_tools.utils': 'src/utils',
        'ml_tools.deep_learning': 'src/deep_learning',
        'ml_tools.utils.gen': 'src/utils/gen',
        'ml_tools.utils.config': 'src/utils/config',
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
