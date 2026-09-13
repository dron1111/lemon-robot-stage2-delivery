# Цифровая модель робота — Этап 2

## Кинематическая цепочка

```text
base_footprint / base_link
→ Z (z_axis_joint, prismatic)
→ J1 yaw
→ J2 yaw
→ J3 yaw
→ J4 pitch
→ J5 roll
→ flange_link / tool0
→ pruner_link / blade_reference
```

Камера Intel RealSense D435 расположена по схеме Eye-in-Hand около рабочего инструмента.

## Основные ROS frames

- `base_footprint` — корневой frame;
- `base_link` — опорная база цифровой модели;
- `z_column_link`, `z_carriage_link` — вертикальная ось Z;
- `j1_link` … `j5_link` — последовательная цепь руки;
- `flange_link`, `tool0` — фланец и рабочая система координат;
- `pruner_link`, `blade_reference` — модель инструмента и опорная точка режущей части;
- `camera_link` — корпус D435;
- `camera_color_optical_frame` — optical frame камеры.

## Подтверждённые параметры

- порядок осей: Z → J1 yaw → J2 yaw → J3 yaw → J4 pitch → J5 roll;
- межосевое расстояние основных суставов: 176 мм;
- габарит печатного звена: 220 × 44 × 18 мм;
- стендовая мачта: 220 мм;
- посадочный размер QC36: 36 мм;
- полый вал J5: наружный диаметр 24 мм, проход для кабеля 14 мм;
- корпус D435 в цифровой модели: 90 × 25 × 25 мм;
- компоновка камеры: Eye-in-Hand.

## Simulation provisional

Для воспроизводимой симуляции заданы временные значения габарита опорной базы, хода Z, механических пределов J1–J5, смещений запястья, масс/инерций и положения камеры относительно `tool0`.

Эти значения находятся в `ros2/lemon_robot_description/config/stage2_geometry.yaml` и не являются окончательными производственными размерами или результатами физической калибровки.

## Геометрия модели

Версия для сдачи использует геометрические примитивы URDF для visual/collision. Производственные CAD-файлы в данный комплект не включаются. Это не мешает проверке кинематической структуры, систем координат, joint limits и симуляции Этапа 2.

## Базовая среда

- Ubuntu 24.04;
- ROS 2 Jazzy;
- Gazebo Harmonic;
- `gz_ros2_control`;
- RViz2.

## Сборка пакета

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

## Проверка Xacro / URDF

```bash
ros2 run xacro xacro \
  $(ros2 pkg prefix --share lemon_robot_description)/urdf/lemon_robot.urdf.xacro \
  > /tmp/lemon_robot.urdf
check_urdf /tmp/lemon_robot.urdf
```

## RViz

```bash
source ~/lemon_stage2_ws/install/setup.bash
ros2 launch lemon_robot_description display.launch.py
```

## Gazebo Harmonic

```bash
source ~/lemon_stage2_ws/install/setup.bash
ros2 launch lemon_robot_description sim.launch.py
```

Headless-режим:

```bash
ros2 launch lemon_robot_description sim.launch.py gui:=false
```

## Проверочный сценарий

После запуска Gazebo:

```bash
source ~/lemon_stage2_ws/install/setup.bash
ros2 run lemon_robot_description stage2_scenario
```

Последовательность:

```text
HOME → RAISE_Z → TURN_J1 → MOVE_J2_J3 → PITCH_J4 → ROLL_J5 → SAFE → HOME_RETURN
```

Сценарий предназначен только для проверки цифровой кинематики и не содержит команд физическому роботу.
