# G1 Pre-Calibration Tool

A modular ROS 2 application for estimating robust command durations before the
navigation calibration of the Unitree G1 humanoid robot.

The objective of this project is to experimentally determine repeatable command
durations for elementary robot motions before performing the complete
navigation calibration campaign.

The application executes repeated motion trials, computes statistical
repeatability, validates the estimated durations experimentally, and exports
validated parameters that are later used during the official navigation
calibration campaign.

---

# Features

- Straight-line pre-calibration (4 m)
- Straight-line pre-calibration (2 m)
- Left rotation pre-calibration (90°)
- Right rotation pre-calibration (90°)
- Statistical repeatability analysis
- Experimental duration validation
- Automatic duration correction
- Persistent YAML storage
- Complete history snapshots
- Export validated durations
- Modular software architecture
- Reusable Python library
- ROS 2 independent business logic

---

# Project Structure

```text
g1_precalibration/
│
├── README.md
├── application.py
├── g1_precalibration.py
│
├── calibration/
│   └── runner.py
│
├── core/
│   ├── config.py
│   ├── menu.py
│   ├── models.py
│   ├── statistics.py
│   └── storage.py
│
├── ros/
│   └── motion_executor.py
│
├── reports/
│   └── report.py
│
├── data/
│   ├── precalibration_config.yaml
│   └── precalibration_results.yaml
│
├── history/
│
└── docs/
    ├── 01_architecture.md
    ├── 02_lifecycle.md
    ├── 03_data_flow.md
    ├── 04_data_models.md
    ├── 05_statistics.md
    ├── 06_validation.md
    ├── 07_storage.md
    └── 08_developer_guide.md
```

---

# Software Architecture

```text
                 g1_precalibration.py
                          │
                    Application
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
 Configuration       Storage          Reports
        │                 │
        └────────────┬────┘
                     ▼
             CalibrationRunner
                     │
                     ▼
              MotionExecutor
                     │
                     ▼
                    ROS 2
```

The architecture follows a strict one-direction dependency policy.

Each module has a single responsibility.

Business logic is completely separated from ROS 2.

---

# Installation

Clone the repository using one of the following methods.

## HTTPS

Recommended for first-time users.

```bash
git clone https://github.com/uleroboticsgroup/g1_precalibration.git

cd g1_precalibration
```

---

## SSH

Recommended for developers with an SSH key configured on GitHub.

```bash
git clone git@github.com:uleroboticsgroup/g1_precalibration.git

cd g1_precalibration
```

---

## Create a Python Virtual Environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Install the Package

```bash
pip install --upgrade pip

pip install -e .
```

The editable installation allows modifications to the source code without
reinstalling the package after every change.


---

# ROS 2 Dependencies

The project requires:

- ROS 2 Humble or newer
- rclpy
- geometry_msgs
- PyYAML

---

# Development Installation

Install the additional development tools.

```bash
pip install black

pip install pylint

pip install pytest
```

Compile the complete project.

```bash
python3 -m compileall .
```

# Running the Application

```bash
python3 g1_precalibration.py
```

---

# Using as a Python Library

The project can also be imported by another ROS 2 application.

```python
from application import Application

app = Application()

app.run()
```

or

```python
from calibration.runner import CalibrationRunner
```

---

# Calibration Workflow

The calibration process is divided into two independent stages.

---

## Stage 1 — Motion Pre-Calibration

The objective of this stage is to determine robust execution durations for the
elementary robot motions.

No ROS bags are recorded during this stage.

The operator manually stops the robot when the physical target is reached.

The following sequence shall always be respected.

### Step 1

Straight trajectory

Target:

```
4 m
```

Repeated several times until stable statistics are obtained.

---

### Step 2

Straight trajectory

Target:

```
2 m
```

Repeated several times until stable statistics are obtained.

---

### Step 3

Rotation

Target:

```
90°
Left
```

Repeated several times until stable statistics are obtained.

---

### Step 4

Rotation

Target:

```
90°
Right
```

Repeated several times until stable statistics are obtained.

---

For every motion the application computes

- minimum
- maximum
- mean
- median
- standard deviation
- coefficient of variation
- approximate 95% confidence interval

The median is selected as the candidate duration.

The candidate duration is then validated experimentally.

If necessary, a proportional correction factor is applied.

Only validated durations are exported.

---

## Stage 2 — Navigation Calibration Campaign

The navigation calibration campaign starts only after every elementary motion
has been validated.

The recommended order is

### Straight Calibration

Five calibration runs

Five validation runs

---

### Square Calibration

Clockwise square trajectory

Five calibration runs

Five validation runs

---

### Reverse Square Calibration

Counter-clockwise square trajectory

Five calibration runs

Five validation runs

Every execution is recorded as a ROS 2 bag.

---

# Complete Workflow

```text
Start
 │
 ▼
Motion Pre-Calibration
 │
 ├───────────────┐
 ▼               ▼
Straight 4 m   Straight 2 m
 │               │
 └──────┬────────┘
        ▼
Left Rotation 90°
        │
        ▼
Right Rotation 90°
        │
        ▼
Statistical Analysis
        │
        ▼
Physical Validation
        │
        ▼
Validated Durations
        │
        ▼
Navigation Calibration Campaign
        │
        ▼
ROS Bag Recording
        │
        ▼
Offline Analysis
        │
        ▼
Final Navigation Parameters
```

---

# Statistical Methodology

For every motion the following quantities are computed.

- Minimum
- Maximum
- Mean
- Median
- Standard deviation
- Coefficient of variation
- Approximate 95% confidence interval

The median is used as the recommended duration because it is robust against
outliers.

---

# Validation

The robot executes the candidate duration automatically.

The operator measures the real travelled distance (or rotation angle).

The correction factor is

```
correction = target / measured
```

The corrected duration is

```
validated_duration =
candidate_duration × correction
```

Only accepted durations become official.

---

# Data Storage

The application stores

```
data/precalibration_config.yaml
```

Robot configuration.

Motion definitions.

---

```
data/precalibration_results.yaml
```

Recorded trials.

Validated durations.

Validation history.

---

History snapshots are automatically written into

```
history/
```

after every modification.

---

# Export

The application exports

```
validated_durations.yaml
```

which contains the validated durations used by the navigation calibration
framework.

---

# Documentation

Additional documentation is available in

```
docs/
```

- Software architecture
- Application life cycle
- Data flow
- Data models
- Statistical methodology
- Validation
- Persistent storage
- Developer guide

---

# Design Principles

The project follows the following engineering principles.

- Single Responsibility Principle
- One-way dependencies
- Strong typing using dataclasses
- Persistent storage
- Immediate data persistence
- Separation of business logic and ROS 2
- Modular reusable components

---

# License

Research software.

---

# Author

Developed for the calibration and evaluation of the Unitree G1 humanoid robot
navigation framework.