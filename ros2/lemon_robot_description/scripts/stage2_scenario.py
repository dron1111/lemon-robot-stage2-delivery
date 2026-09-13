#!/usr/bin/env python3
"""Reproducible Stage 2 simulation-only kinematic demonstration."""

from __future__ import annotations

from dataclasses import dataclass

import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

JOINTS = ["z_axis_joint", "j1_joint", "j2_joint", "j3_joint", "j4_joint", "j5_joint"]


@dataclass(frozen=True)
class PoseStep:
    name: str
    positions: tuple[float, float, float, float, float, float]
    seconds: int = 2


STAGE2_SEQUENCE = (
    PoseStep("HOME", (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
    PoseStep("RAISE_Z", (0.12, 0.0, 0.0, 0.0, 0.0, 0.0)),
    PoseStep("TURN_J1", (0.12, 0.55, 0.0, 0.0, 0.0, 0.0)),
    PoseStep("MOVE_J2_J3", (0.12, 0.55, -0.45, 0.35, 0.0, 0.0)),
    PoseStep("PITCH_J4", (0.12, 0.55, -0.45, 0.35, 0.40, 0.0)),
    PoseStep("ROLL_J5", (0.12, 0.55, -0.45, 0.35, 0.40, -0.60)),
    PoseStep("SAFE", (0.05, 0.15, -0.10, 0.10, 0.0, 0.0)),
    PoseStep("HOME_RETURN", (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
)


class Stage2Scenario(Node):
    def __init__(self) -> None:
        super().__init__("stage2_scenario")
        self._client = ActionClient(
            self,
            FollowJointTrajectory,
            "/stage2_joint_trajectory_controller/follow_joint_trajectory",
        )

    def run(self) -> bool:
        self.get_logger().info("Waiting for Stage 2 Gazebo trajectory controller...")
        if not self._client.wait_for_server(timeout_sec=20.0):
            self.get_logger().error("Trajectory controller action server is unavailable")
            return False

        for step in STAGE2_SEQUENCE:
            self.get_logger().info(f"Stage 2 step: {step.name}")
            goal = FollowJointTrajectory.Goal()
            goal.trajectory = JointTrajectory()
            goal.trajectory.joint_names = JOINTS
            point = JointTrajectoryPoint()
            point.positions = list(step.positions)
            point.time_from_start = Duration(sec=step.seconds)
            goal.trajectory.points = [point]
            send_future = self._client.send_goal_async(goal)
            rclpy.spin_until_future_complete(self, send_future)
            handle = send_future.result()
            if handle is None or not handle.accepted:
                self.get_logger().error(f"Controller rejected step {step.name}")
                return False
            result_future = handle.get_result_async()
            rclpy.spin_until_future_complete(self, result_future)
            result = result_future.result()
            if result is None or result.result.error_code != FollowJointTrajectory.Result.SUCCESSFUL:
                self.get_logger().error(f"Step failed: {step.name}")
                return False

        self.get_logger().info("Stage 2 kinematic scenario completed")
        return True


def main() -> None:
    rclpy.init()
    node = Stage2Scenario()
    try:
        success = node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()
    raise SystemExit(0 if success else 2)


if __name__ == "__main__":
    main()
