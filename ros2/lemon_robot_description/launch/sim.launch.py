from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    share = Path(get_package_share_directory("lemon_robot_description"))
    ros_gz_share = Path(get_package_share_directory("ros_gz_sim"))
    xacro_file = str(share / "urdf" / "lemon_robot.urdf.xacro")
    world_file = str(share / "worlds" / "stage2_neutral.sdf")
    controller_file = str(share / "config" / "stage2_controllers.yaml")
    gui = LaunchConfiguration("gui")

    robot_description = Command(
        [
            FindExecutable(name="xacro"),
            " ", xacro_file,
            " use_gz_ros2_control:=true controllers_file:=", controller_file,
        ]
    )

    gazebo_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(ros_gz_share / "launch" / "gz_sim.launch.py")),
        launch_arguments={"gz_args": f"-r -v 3 {world_file}", "on_exit_shutdown": "true"}.items(),
        condition=IfCondition(gui),
    )
    gazebo_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(ros_gz_share / "launch" / "gz_sim.launch.py")),
        launch_arguments={"gz_args": f"-r -s -v 3 {world_file}", "on_exit_shutdown": "true"}.items(),
        condition=UnlessCondition(gui),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("gui", default_value="true"),
            gazebo_gui,
            gazebo_headless,
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                output="screen",
                parameters=[{"use_sim_time": True, "robot_description": robot_description}],
            ),
            TimerAction(
                period=2.0,
                actions=[Node(package="ros_gz_sim", executable="create", arguments=["-name", "lemon_robot", "-topic", "/robot_description"], output="screen")],
            ),
            TimerAction(
                period=5.0,
                actions=[Node(package="controller_manager", executable="spawner", arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"], output="screen")],
            ),
            TimerAction(
                period=7.0,
                actions=[Node(package="controller_manager", executable="spawner", arguments=["stage2_joint_trajectory_controller", "--controller-manager", "/controller_manager"], output="screen")],
            ),
        ]
    )
