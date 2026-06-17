import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='basicbot_control',
            executable='obstacle_avoidance',
            name='obstacle_avoidance',
            output='screen'
        )
    ])
