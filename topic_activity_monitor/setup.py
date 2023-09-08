from setuptools import setup

package_name = 'topic_activity_monitor'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dan brooks',
    maintainer_email='ros2@danbrooks.net',
    description='ROS2 Topic Activity and Connection Monitoring',
    license='Apache 2',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
