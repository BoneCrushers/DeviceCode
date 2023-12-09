BUILD_MAJOR=0

import setuptools

def version():
    import datetime

    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds = (now - midnight).seconds / 10

    BUILD_MINOR = f"{now.month:02d}{now.day:02d}"
    BUILD_MINOR = str(now.year)[2:]+BUILD_MINOR

    build = f"{BUILD_MAJOR}.{BUILD_MINOR}.{seconds:04.0f}"
    return build

setuptools.setup(
    name="bonecrushers",
    version=version(),
    url="https://github.com/BoneCrushers/DeviceCode",
    author="The Bone Crushers",
    author_email="kate.gordon@mnsu.edu",
    description="Device code for Bone Crushers experiment",
    packages=setuptools.find_namespace_packages(),
    install_requires=[
        "numpy==1.26.0",
        "pyaudio==0.2.14",
        "smbus2==0.4.3"
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
    include_package_data=True,
    package_data={
        "bonecrushers.data": ["*.wav"]},
    entry_points = {
        'console_scripts': [
            'bcrush-test=bonecrushers.cli.test:main',
        ],
    }
)
