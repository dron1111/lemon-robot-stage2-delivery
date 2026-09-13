cmake_minimum_required(VERSION 3.16)
project(lemon_robot_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch rviz urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/stage2_scenario.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME stage2_scenario
)

ament_package()
