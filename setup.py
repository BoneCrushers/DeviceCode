import setuptools

setuptools.setup(
    name="bonecrushers",
    version="1.0.0",
    url="https://github.com/BoneCrushers/DeviceCode",
    author="The Bone Crushers",
    author_email="kate.gordon@mnsu.edu",
    description="Device code for Bone Crushers experiment",
    packages=setuptools.find_namespace_packages(),
    install_requires=[
        "numpy==1.26.0",
        "pyaudio==0.2.14"
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
    include_package_data=True,
    package_data={'': ['SoundFiles']},
    entry_points = {
        'console_scripts': [
            'bcrush=bonecrushers.__main__:main',
        ],
    }
)