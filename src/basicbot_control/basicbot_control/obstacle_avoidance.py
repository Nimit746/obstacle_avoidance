import rclpy       # Rclpy is a library for ROS 2. It is ros2 client for python
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image     # These are the sensor message interfaces for the ROS 2
from geometry_msgs.msg import Twist              # These are the geometry message imnterfaces for the ROS 2
from cv_bridge import CvBridge                   # This is the library for connecting the OpenCV and the ROS 2.

from rclpy.executors import ExternalShutdownException
import cv2
import numpy as np
import os
from ament_index_python.packages import get_package_share_directory



# Check whether the ultralytics is installed or not as if not installed then the server will crash. Also there is a flag for marking that module is installed or not.
try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False


# Creating a node class for the ROS
class ObstacleAvoidanceNode(Node):
    def __init__(self):
        """Constructor"""
        super().__init__('obstacle_avoidance')
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)   # Publishing to the /cmd_vel topic using the twist messages which contains the angular and linear velocity of the robot.

        self.scan_subscription = self.create_subscription(      # Creating a subscription for the data coming from the LiDAR
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.camera_subscription = self.create_subscription(   # Creating a subscription for the data coming from the camera.
            Image,
            '/camera/image_raw',
            self.camera_callback,
            10)
            
        self.bridge = CvBridge()    # Connecting openCV to the ROS using the CVBridge module
        
        
        
        
        # Check for the YOLO model loaded or not. If loaded then the models of the package will be laoded else the models will not be used, instead the LiDAR will be used only
        if HAS_YOLO:     
            try:
                self.get_logger().info('Loading YOLO models...')
                
                # YOLOv8n will auto-download if not found in the current directory
                self.yolo_coco = YOLO('yolov8n.pt')
                
                # Look for best.pt in the package's share/models directory
                pkg_dir = get_package_share_directory('basicbot_control')
                best_pt_path = os.path.join(pkg_dir, 'models', 'best.pt')
                
                if os.path.exists(best_pt_path):
                    self.yolo_stairs = YOLO(best_pt_path)
                    self.get_logger().info(f'Loaded custom stairs model from {best_pt_path}')
                else:
                    self.get_logger().warn(f'best.pt not found at {best_pt_path}, using yolov8n.pt as fallback')
                    self.yolo_stairs = YOLO('yolov8n.pt')
            except Exception as e:
                self.get_logger().error(f'Error loading YOLO models: {e}')
                self.yolo_coco = None
                self.yolo_stairs = None
        else:
            self.get_logger().error('ultralytics package not found. YOLO object detection disabled.')
            self.yolo_coco = None
            self.yolo_stairs = None
            
        self.min_distance = float('inf')
        self.object_detected = False
        self.stairs_detected = False
        
        # Simple control loop timer
        self.timer = self.create_timer(0.5, self.control_loop)
        
    # This is a callback function called by a Subscriber for LiDAR
    def scan_callback(self, msg):
        # Filter out inf and nan values
        valid_ranges = [r for r in msg.ranges if r > msg.range_min and r < msg.range_max]
        if valid_ranges:
            self.min_distance = min(valid_ranges)
        else:
            self.min_distance = float('inf')
            
            
    # This is a callback function called by the Camera Subscriber.
    def camera_callback(self, msg):
        if not self.yolo_coco:
            return
            
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Run inference (Process of predicting the data using the pretrained model. [In this case Yolov8n.pt or best.pt])
            results_coco = self.yolo_coco(cv_image, verbose=False)
            results_stairs = self.yolo_stairs(cv_image, verbose=False) if self.yolo_stairs else None
            
            # Update detection flags based on bounding boxes
            self.object_detected = len(results_coco[0].boxes) > 0
            if results_stairs:
                self.stairs_detected = len(results_stairs[0].boxes) > 0
            else:
                self.stairs_detected = False
        except Exception as e:
            self.get_logger().warn(f'Camera processing error: {e}')
    
    
    # This is a callback function for the timer after every 0.1 seconds.
    def control_loop(self):
        msg = Twist()
        
        # Reactive obstacle avoidance fusing LiDAR and Vision
        obstacle_too_close = self.min_distance < 0.25
        vision_detected = self.object_detected or self.stairs_detected
        
        if obstacle_too_close or vision_detected:
            # Stop and turn
            msg.linear.x = 0.0
            msg.angular.z = 0.5
            reason = "LiDAR" if obstacle_too_close else "Vision"
            self.get_logger().info(f'{reason} obstacle detected! Turning.')
        else:
            # Move forward
            msg.linear.x = 0.2
            msg.angular.z = 0.0
            
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
