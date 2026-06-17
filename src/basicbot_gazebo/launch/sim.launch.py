import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    gazebo_pkg = get_package_share_directory('basicbot_gazebo')
    desc_pkg = get_package_share_directory('basicbot_description')
    
    world_file = os.path.join(gazebo_pkg, 'worlds', 'obstacle_field.sdf')
    bridge_config = os.path.join(gazebo_pkg, 'config', 'bridge_config.yaml')
    model_file = os.path.join(desc_pkg, 'models', 'basicbot', 'model.sdf')
    
    # 1. Start Gazebo Sim
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )
    
    # 2. Spawn the basicbot model
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'basicbot',
            '-file', model_file,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )
    
    # 3. Start the ros_gz_bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        spawn_robot,
        bridge
    ])
