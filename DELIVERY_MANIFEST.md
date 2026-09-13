# Реестр комплекта сдачи Этапа 2

Договор №1-СЗ/2026 от 23.07.2026.

Комплект содержит только материалы договорного Этапа 2.

## Документация

- `docs/01_STAGE2_COMPLETION_REPORT.md`
- `docs/02_DIGITAL_MODEL.md`
- `docs/03_SPECIFICATION.md`
- `docs/04_SUPPLIER_REQUESTS.md`
- `docs/05_VALIDATION.md`

## Цифровая модель и симуляция

- `ros2/lemon_robot_description/package.xml`
- `ros2/lemon_robot_description/CMakeLists.txt`
- `ros2/lemon_robot_description/config/stage2_geometry.yaml`
- `ros2/lemon_robot_description/config/stage2_controllers.yaml`
- `ros2/lemon_robot_description/urdf/lemon_robot.urdf.xacro`
- `ros2/lemon_robot_description/urdf/macros/inertial_macros.xacro`
- `ros2/lemon_robot_description/launch/display.launch.py`
- `ros2/lemon_robot_description/launch/sim.launch.py`
- `ros2/lemon_robot_description/rviz/lemon_robot.rviz`
- `ros2/lemon_robot_description/worlds/stage2_neutral.sdf`
- `ros2/lemon_robot_description/scripts/stage2_scenario.py`

## Проверка

- `scripts/validate_delivery.py`
- `.github/workflows/validate.yml`

Редакция переданного результата идентифицируется конкретным Git commit SHA, указанным в Акте сдачи-приёмки.
