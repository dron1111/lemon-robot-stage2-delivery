#!/usr/bin/env python3
"""Validate the public Stage 2 delivery package."""

from __future__ import annotations

import argparse
import ast
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

REQUIRED_FILES = (
    "ros2/lemon_robot_description/package.xml",
    "ros2/lemon_robot_description/CMakeLists.txt",
    "ros2/lemon_robot_description/urdf/lemon_robot.urdf.xacro",
    "ros2/lemon_robot_description/urdf/macros/inertial_macros.xacro",
    "ros2/lemon_robot_description/launch/display.launch.py",
    "ros2/lemon_robot_description/launch/sim.launch.py",
    "ros2/lemon_robot_description/rviz/lemon_robot.rviz",
    "ros2/lemon_robot_description/config/stage2_geometry.yaml",
    "ros2/lemon_robot_description/config/stage2_controllers.yaml",
    "ros2/lemon_robot_description/worlds/stage2_neutral.sdf",
    "ros2/lemon_robot_description/scripts/stage2_scenario.py",
    "docs/01_STAGE2_COMPLETION_REPORT.md",
    "docs/02_DIGITAL_MODEL.md",
    "docs/03_SPECIFICATION.md",
    "docs/04_SUPPLIER_REQUESTS.md",
    "docs/05_VALIDATION.md",
)

REQUIRED_LINKS = {
    "base_footprint", "base_link", "z_column_link", "z_carriage_link",
    "j1_link", "j2_link", "j3_link", "j4_link", "j5_link",
    "flange_link", "tool0", "pruner_link", "blade_reference",
    "camera_mount_link", "camera_link", "camera_color_optical_frame",
}

EXPECTED_JOINTS = {
    "base_footprint_joint": ("fixed", "base_footprint", "base_link", None),
    "mast_mount_joint": ("fixed", "base_link", "z_column_link", None),
    "z_axis_joint": ("prismatic", "z_column_link", "z_carriage_link", "0 0 1"),
    "j1_joint": ("revolute", "z_carriage_link", "j1_link", "0 0 1"),
    "j2_joint": ("revolute", "j1_link", "j2_link", "0 0 1"),
    "j3_joint": ("revolute", "j2_link", "j3_link", "0 0 1"),
    "j4_joint": ("revolute", "j3_link", "j4_link", "0 1 0"),
    "j5_joint": ("revolute", "j4_link", "j5_link", "1 0 0"),
    "flange_joint": ("fixed", "j5_link", "flange_link", None),
    "tool0_joint": ("fixed", "flange_link", "tool0", None),
    "pruner_joint": ("fixed", "tool0", "pruner_link", None),
    "blade_reference_joint": ("fixed", "pruner_link", "blade_reference", None),
    "camera_mount_joint": ("fixed", "tool0", "camera_mount_link", None),
    "camera_joint": ("fixed", "camera_mount_link", "camera_link", None),
    "camera_optical_joint": ("fixed", "camera_link", "camera_color_optical_frame", None),
}

PHYSICAL_LINKS = {
    "base_link", "z_column_link", "z_carriage_link", "j1_link", "j2_link",
    "j3_link", "j4_link", "j5_link", "flange_link", "pruner_link", "camera_link",
}
MOVING_JOINTS = ("z_axis_joint", "j1_joint", "j2_joint", "j3_joint", "j4_joint", "j5_joint")


def fail(message: str) -> None:
    raise AssertionError(message)


def validate(repo_root: Path, write_urdf: Path | None) -> dict[str, object]:
    repo_root = repo_root.resolve()
    package = repo_root / "ros2" / "lemon_robot_description"
    checks: list[str] = []

    for rel in REQUIRED_FILES:
        if not (repo_root / rel).is_file():
            fail(f"missing required file: {rel}")
    checks.append("required_files")

    for xml_path in (
        package / "package.xml",
        package / "urdf" / "lemon_robot.urdf.xacro",
        package / "urdf" / "macros" / "inertial_macros.xacro",
        package / "worlds" / "stage2_neutral.sdf",
    ):
        ET.parse(xml_path)
    for py_path in (
        package / "launch" / "display.launch.py",
        package / "launch" / "sim.launch.py",
        package / "scripts" / "stage2_scenario.py",
    ):
        ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
    checks.append("source_syntax")

    try:
        import xacro
    except ImportError as exc:
        raise RuntimeError("xacro is required") from exc
    expanded = xacro.process_file(
        str(package / "urdf" / "lemon_robot.urdf.xacro"),
        mappings={"use_gz_ros2_control": "false"},
    ).toprettyxml(indent="  ")
    if write_urdf:
        write_urdf.parent.mkdir(parents=True, exist_ok=True)
        write_urdf.write_text(expanded, encoding="utf-8")
    root = ET.fromstring(expanded)
    checks.append("xacro_expansion")

    links = {x.attrib["name"]: x for x in root.findall("link")}
    if REQUIRED_LINKS - links.keys():
        fail("missing required links: " + ", ".join(sorted(REQUIRED_LINKS - links.keys())))

    joints = {x.attrib["name"]: x for x in root.findall("joint")}
    for name, (kind, parent, child, axis) in EXPECTED_JOINTS.items():
        joint = joints.get(name)
        if joint is None or joint.attrib.get("type") != kind:
            fail(f"joint contract mismatch: {name}")
        if joint.find("parent") is None or joint.find("parent").attrib.get("link") != parent:
            fail(f"parent mismatch: {name}")
        if joint.find("child") is None or joint.find("child").attrib.get("link") != child:
            fail(f"child mismatch: {name}")
        if joint.find("origin") is None:
            fail(f"origin missing: {name}")
        if axis is not None:
            axis_tag = joint.find("axis")
            limit = joint.find("limit")
            if axis_tag is None or axis_tag.attrib.get("xyz") != axis:
                fail(f"axis mismatch: {name}")
            if limit is None:
                fail(f"limit missing: {name}")
            if not (float(limit.attrib["lower"]) < float(limit.attrib["upper"])):
                fail(f"invalid limits: {name}")
    checks.append("joint_contract")

    child_owner: dict[str, str] = {}
    children = {name: [] for name in links}
    for joint in joints.values():
        parent = joint.find("parent").attrib["link"]
        child = joint.find("child").attrib["link"]
        if parent not in links or child not in links or child in child_owner:
            fail(f"invalid tree at {joint.attrib.get('name')}")
        child_owner[child] = joint.attrib["name"]
        children[parent].append(child)
    roots = set(links) - set(child_owner)
    if roots != {"base_footprint"}:
        fail(f"unexpected roots: {sorted(roots)}")
    visited: set[str] = set()
    stack = ["base_footprint"]
    while stack:
        current = stack.pop()
        if current in visited:
            fail("cycle detected")
        visited.add(current)
        stack.extend(children[current])
    if visited != set(links):
        fail("disconnected URDF tree")
    checks.append("connected_tree")

    for name in PHYSICAL_LINKS:
        for tag in ("visual", "collision", "inertial"):
            if links[name].find(tag) is None:
                fail(f"{name} lacks {tag}")
    if root.findall(".//mesh"):
        fail("delivery model must not contain CAD mesh references")
    checks.append("primitive_geometry_only")

    geometry = yaml.safe_load((package / "config" / "stage2_geometry.yaml").read_text(encoding="utf-8"))
    if "confirmed" not in geometry or "simulation_provisional" not in geometry:
        fail("geometry status sections missing")
    if geometry["confirmed"].get("joint_center_distance_m") != 0.176:
        fail("confirmed joint centre distance changed")
    checks.append("confirmed_vs_provisional")

    controllers = yaml.safe_load((package / "config" / "stage2_controllers.yaml").read_text(encoding="utf-8"))
    joints_cfg = controllers["stage2_joint_trajectory_controller"]["ros__parameters"]["joints"]
    if tuple(joints_cfg) != MOVING_JOINTS:
        fail("controller joint order mismatch")
    checks.append("controller_chain")

    sim_text = (package / "launch" / "sim.launch.py").read_text(encoding="utf-8")
    xacro_text = (package / "urdf" / "lemon_robot.urdf.xacro").read_text(encoding="utf-8")
    if "ros_gz_sim" not in sim_text or "gz_ros2_control" not in xacro_text:
        fail("Gazebo Harmonic integration missing")
    if "gazebo_ros" in sim_text or "gazebo_ros2_control/GazeboSystem" in xacro_text:
        fail("Gazebo Classic marker found")
    checks.append("gazebo_harmonic")

    rviz = (package / "rviz" / "lemon_robot.rviz").read_text(encoding="utf-8")
    if "RobotModel" not in rviz or "Fixed Frame: base_footprint" not in rviz:
        fail("RViz configuration mismatch")
    checks.append("rviz")

    return {
        "status": "PASS",
        "checks": checks,
        "moving_joints": list(MOVING_JOINTS),
        "hardware_execution_enabled": False,
        "stage3_scope_added": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--write-urdf", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.repo_root, args.write_urdf)
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
