# Obstacle Avoidance ROS Project

A ROS-based obstacle avoidance system for autonomous robots, featuring sensor integration, path planning, and dynamic obstacle detection capabilities.

## Features

- Real-time obstacle detection using LiDAR/ultrasonic sensors
- Dynamic path planning and navigation
- ROS compatibility for easy integration with robotic platforms
- Simulation support for Gazebo
- Configurable avoidance parameters

## Prerequisites

- ROS Noetic (or compatible distribution)
- Python 3.8+
- ROS packages: `rospy`, `sensor_msgs`, `nav_msgs`, `geometry_msgs`
- Gazebo (for simulation)

## Installation

1. Clone this repository into your ROS workspace's `src` folder:

   ```bash
   cd ~/catkin_ws/src
   git clone <repository-url>
   ```
2. Install dependencies:

   ```bash
   rosdep install --from-paths src --ignore-src -r -y
   ```
3. Build the workspace:

   ```bash
   cd ~/catkin_ws
   catkin_make
   source devel/setup.bash
   ```

## Usage

### Run in Simulation

1. Launch the Gazebo simulation environment:

   ```bash
   roslaunch obstacle_avoidance gazebo.launch
   ```
2. Start the obstacle avoidance node:

   ```bash
   rosrun obstacle_avoidance avoidance_node.py
   ```

### Run on Hardware

1. Connect your robot's sensors and ensure ROS can access them
2. Configure sensor topics in `config/params.yaml`
3. Launch the avoidance system:
   ```bash
   roslaunch obstacle_avoidance hardware.launch
   ```

## Configuration

Adjust parameters in `config/params.yaml` to customize:

- Minimum distance to obstacles
- Speed limits
- Sensor topic names
- Avoidance behavior thresholds

## Project Structure

```
obstacle_avoidance/
├── src/                # Source code
│   └── avoidance_node.py
├── launch/             # ROS launch files
├── config/             # Configuration files
├── models/             # Gazebo models (if used)
├── worlds/             # Gazebo world files
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request
