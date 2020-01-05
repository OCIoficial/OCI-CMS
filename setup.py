from setuptools import setup, find_packages

setup(
    name="oci-cms",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "cms.grading.scoretypes": [
            "ThresholdPercentage=scoretypes.ThresholdPercentage:ThresholdPercentage"
        ]
    }
)
