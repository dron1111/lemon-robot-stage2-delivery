# Проверка комплекта Этапа 2

## Автоматическая структурная проверка

```bash
python -m pip install 'xacro==2.1.1' 'PyYAML>=6.0.1'
python scripts/validate_delivery.py --write-urdf /tmp/lemon_robot.urdf
```

Проверяются:

- наличие обязательных файлов комплекта;
- раскрытие Xacro;
- корректная связная URDF-структура;
- links и joints цепочки Z → J1 → J2 → J3 → J4 → J5;
- axes и limits подвижных joints;
- frames рабочего инструмента и D435;
- visual/collision/inertial для физических links;
- отсутствие производственных mesh/CAD-файлов в версии сдачи;
- конфигурация шестиосевого trajectory controller;
- наличие Gazebo Harmonic / `gz_ros2_control`;
- RViz fixed frame `base_footprint`.

## Независимая проверка URDF

На Ubuntu 24.04:

```bash
sudo apt-get update
sudo apt-get install -y liburdfdom-tools
check_urdf /tmp/lemon_robot.urdf
```

## ROS 2 workspace

```bash
mkdir -p ~/lemon_stage2_ws/src
cd ~/lemon_stage2_ws/src
git clone https://github.com/dron1111/lemon-robot-stage2-delivery.git
ln -s lemon-robot-stage2-delivery/ros2/lemon_robot_description .
cd ~/lemon_stage2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## RViz

```bash
ros2 launch lemon_robot_description display.launch.py
```

## Gazebo Harmonic

```bash
ros2 launch lemon_robot_description sim.launch.py
```

Для headless-режима:

```bash
ros2 launch lemon_robot_description sim.launch.py gui:=false
```

## Сценарий цифровой кинематики

В отдельном терминале после запуска Gazebo:

```bash
source ~/lemon_stage2_ws/install/setup.bash
ros2 run lemon_robot_description stage2_scenario
```

Последовательность: HOME → RAISE_Z → TURN_J1 → MOVE_J2_J3 → PITCH_J4 → ROLL_J5 → SAFE → HOME_RETURN.

Проверка относится только к цифровой модели Этапа 2 и не включает физическое управление роботом.
