from setuptools import setup, Extension

# Define the C extension module
signal_processing_module = Extension(
    'signal_processing_ext',
    sources=['signal_processing_module.c'],
)

# Setup configuration
setup(
    name='threat_elimination_extensions',
    version='1.0',
    description='High-performance C extensions for threat elimination',
    ext_modules=[signal_processing_module],
)