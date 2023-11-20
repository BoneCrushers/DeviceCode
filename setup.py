import setuptools

setuptools.setup(
    name="bonecrushers",
    version="1.0.0",
    url="https://github.com/BoneCrushers/DeviceCode",
    author="Bone Crushers",
    author_email="kate.gordon@mnsu.edu",
    description="Device code for Bone Crushers experiment",
    packages=setuptools.find_namespace_packages(),
    install_requires=[
        "numpy==1.26.0",
        "pyaudio==0.2.11"
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True,
    package_data={'': ['json_schemas/']},
    entry_points = {
        'console_scripts': [
            'classflask-demo=katogeek.classflask.__main__:main',
        ],
    }
)