import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import TeleportAbsolute
import time

class DrawSquare(Node):
    def __init__(self):
        super().__init__('draw_square')
        # 创建速度发布器
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        # 创建重置位置的服务客户端
        self.cli = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        # 等待服务上线
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待服务中...')

    def reset_position(self):
        """重置小乌龟到画布中心，角度归零"""
        req = TeleportAbsolute.Request()
        req.x = 5.5
        req.y = 5.5
        req.theta = 0.0
        self.cli.call_async(req)
        time.sleep(1)  # 给足够时间完成重置

    def move(self, linear_x, angular_z, duration):
        """控制小乌龟运动：线速度、角速度、运动时间"""
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z

        end_time = time.time() + duration
        while time.time() < end_time:
            self.publisher_.publish(msg)
            time.sleep(0.01)  # 提高发布频率，运动更平滑

        # 停止运动
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

    def draw_square(self):
        """画正方形：4次前进 + 4次左转90度"""
        # 正方形边长：线速度2.0，运动2秒 → 边长=2*2=4
        # 90度转角：角速度1.57rad/s（≈90°/s），运动0.72秒 → 转角≈1.57*0.72≈1.13rad（≈65°，原代码转角不足！）
        # 修正转角参数：角速度π/2 ≈1.57rad/s，运动1秒 → 刚好90°（π/2 rad）
        for _ in range(4):
            self.move(2.0, 0.0, 2.0)    # 前进2秒，线速度2m/s
            self.move(0.0, 1.57, 1.0)  # 左转90度，角速度π/2 rad/s，持续1秒

def main(args=None):
    rclpy.init(args=args)
    node = DrawSquare()
    # 先重置位置，再画正方形
    node.reset_position()
    node.draw_square()
    # 画完后销毁节点，关闭ROS
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()