import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    gazebo_pkg = get_package_share_directory('basicbot_gazebo')
    desc_pkg = get_package_share_directory('basicbot_description')
    
    world_file = os.path.join(gazebo_pkg, 'worlds', 'obstacle_field.sdf')
    bridge_config = os.path.join(gazebo_pkg, 'config', 'bridge_config.yaml')
    
    # Path to Xacro file and RViz config
    xacro_file = os.path.join(desc_pkg, 'urdf', 'basicbot.urdf.xacro')
    rviz_config_file = os.path.join(desc_pkg, 'rviz', 'basicbot.rviz')
    
    # Process Xacro
    doc = xacro.process_file(xacro_file)
    robot_desc = doc.toxml()
    
    # 1. Start Gazebo Sim
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )
    
    # 2. Start robot_state_publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )
    
    # 3. Spawn the basicbot model
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'basicbot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )
    
    # 4. Start the ros_gz_bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
        output='screen'
    )

    # 5. Start RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        node_robot_state_publisher,
        spawn_robot,
        bridge,
        rviz_node
    ])
