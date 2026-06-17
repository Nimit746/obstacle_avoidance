# Idea of the node creation

## Step 1

### The idea of the node creation is that first import all the necessary modules and then apply a check on the ultralytics module as it requires to be installed in the environment. If it is installed then there is a variable named `HAS_YOLO` whose value is true or false according to the import of the module which will affect the later code

```python
from ultralytics import YOLO
```

<p>
The above statement can be crashed if the module is not imported which can crash the robot, therefore it is kept inside a check.
</p>

```python
try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False
```

> This check insures that if the module is not imported then the node doesn't crash.

## Step 2

### A new node is created which is named as ObstacleAvoidanceNode

<p>

> This node created is inherited from the Node class inside the package node It can be called using the

```python
from rclpy.node import Node
```

and is implemented by

```python
class ObstacleAvoidanceNode(Node):
```

>Inside the class in a constructor we name the node using the parent class constructor

```python
super().__init__('obstacle_avoidance')
```

</p>

<p>
Now after the constructor the next step is to write the complete node.
This is achieved in many steps:

1. Create a publisher which publishes the content to the `/cmd_vel` topic as this contains the messages to be given to the robot for the movement.

2. Create 2 subscribers which subscribes to topics such as `/scan` and `/camera/image_raw` which helps to recieve the data what LiDAR and Camera are collecting together on basis of that data decision is made.

3. Subscriber 1 which is from LiDAR takes the data in the form of `LaserScan` which is a predefined message in the `sensor_msgs.msg` interface

4. Subscriber 2 which is from Camera takes the data in the form of `Image` which is again a predefined in the `sensor_msgs.msg` interface.

5. Then the bridge has to be build between the Camera recieved data and OpenCV as they both process images but the format is different. This is done using a module named `CvBridge` and can be called in the following way.

```python
    self.bridge = CvBridge()
```

6. Then if there was YOLO installed then the models have to be loaded in the `self.yolo_coco` by ```self.yolo_coco = YOLO('yolo8vn.pt')```. If not present then the message will pop up that Ultralytics was not found so the robot will work using the LiDAR.

7. The last step is to create a timer function of ROS which calls a callback function for the processing and publishing the messages to the robot using the publisher build above.
`create_timer` is a built_in method in Node class which takes 2 parameter one is time (in seconds) and other is a callback funtion. Here the callback funtion is named as `self.control_loop`

> NOTE: The callback funtion in the subscribers and timer funtion are just the references of the methods build in the class. ROS calls and executes them all under the hood.

</p>

<p>
The callback funtions of the subscribers and timer are as follows:

1. Subscriber 1: `Scan Callback()` -> It takes two parameters first is msg and other is self. Msg is passed by the ROS under the hood as it is called by ROS. This function is used to collect the minimum distance and save it in the class attribute called `self.min_distance`. It will be used in the control_loop function later.

2. Subscriber 2: `Camera Callback()` -> It also takes the same parameters as the Scan Callback funtion and is used called similarly. If there is some value of the `self.yolo_coco` then the function will process further otherwise it will return as it is. In processing the the msg image is converted to the main format of the CV so that yolo can predict on that image. It uses bridge to convert the data from msg to the CV. The command is `cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")` which converts the image to the original format of the CV.

3. Timer callback function named `control_loop()` -> It is a basic method which takes only a self object as the instance of the class. This function has all the values of the data collected in the variables using the camera and LiDAR. it checks that which has the minimum range of the data and then it processes and publish the result to the topic `/cmd_vel` which gives the robot the command that where it should move and in which direction.

</p>

## Step 3

### The last step is the most basic where a main function is created and then the function creates complete pipeline of the ROS Node working

<p>

The code snippet is as follows:

```python
def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if not node:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
```

</p>

## Last Step

### This step finally sets the command to start the node

```python
if __name__ == '__main__':
    main()
```
