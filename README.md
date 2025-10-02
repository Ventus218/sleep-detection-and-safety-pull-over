# Sleep detection and safety pull over

## Developers

- Michele Ravaioli
- Alessandro Venturini

## Abstract

We propose a vehicle equipped with an adaptive cruise control system that includes highway lane-keeping functionality (which, for safety reasons, requires the driver to remain attentive at all times).

The system we aim to develop will complement the aforementioned functionality by detecting if the driver falls asleep and, in such cases, safely pulling the vehicle over to a stop.

Since the described behavior would require the vehicle to safely change lanes to reach the emergency lane—a task that is inherently complex—we have chosen to adopt the following simplifying assumption:

The vehicle’s cruise control system is designed to operate only in the slowest lane (already adjacent to the emergency lane).

## Setup

### Virtual environment

```sh
conda create -p ./.venv python=3.12
conda activate ./.venv
```

### Requirements

```sh
pip install -r requirements.txt
```

### How to update typings

[carla-python-stubs](https://github.com/aasewold/carla-python-stubs/releases/tag/0.9.15)

## Solution

We detect driver drowsiness or more generally inattention by leveraging an artificial vision algorithm based on face detection and analisys.

During pull over preparation we check the following conditions in order to compute if the vehicle can start pulling over:

- there must be an emergency lane
- there must be no vehicle coming from the emergency lane (behind the ego vehicle)
- for the entire space needed for the maneuver:

  - the emergency lane must be clear of obstacles (vehicles or static obstacles)
  - there should be no exits from the highway

During the whole maneuver and after the vehicle has stopped the driver is required to press a button in order to go back to manual driving.
The reason is that we want the driver to explicitly express the will of taking control of the vehicle (it may not be safe to assume that the driver has regained consciousness by just detecting some movements on the driving wheel or on the pedals).

## How to detect a safe pull over spot

We basically need to achieve two goals and combine their results to decide if a spot is safe for pulling over.
- Detect the emergency lane (we must distinguish if the vehicle is approaching an exit)
- Detect if the emergency lane is free of obstacles

Initially we thought about exploiting the guardrail in order to detect the road boundary. In the end we decided
not do use that since guardrails may be missing (more likely than the emergency lane).

### With camera and Radar
We exploit the camera in order to detect a continous (no exit) white line (the emergency lane).
We exploit the radar in order to detect any obstacles in the emergency lane.

1. Camera need to have a free line of sight on the emergency lane line for X meters ahead of the vehicle (X meters is the minimum distance for the vehicle to be able to stop safely)
2. If the line is not continous for X meters we assume there is a nearby exit -> NOT SAFE
3. The radar projects multiple points on the ground for X meters ahead (and slightlu on the right) of the vehicle.
4. We only consider points which distance from the line is about the width of the vehicle (a bit more).
5. Now we consider a ground plane and then measure the height of each considered point from this plane.
6. If there are multiple points which distance from the plane is relevantly high, we then assume that there is some obstacle in the emergency lane -> NOT SAFE.

As soon as the car start searching for a pull over spot it will gently approach the emergency lane line in order to extend the visibility of the radar onto the emergency lane

#### Pros
- Cheaper sensors
#### Cons
- Harder to detect a safe pull over spot with high confidence (may result in missing some safe pull over spots)
- Harder to detect a safe pull over spot in turning roads

### With a semantic lidar

First we detect a white line aside of the vehicle.
If the line is not detected we assume that there is no emergency lane -> NOT SAFE
If the line is dashed we assume there is a nearby exit -> NOT SAFE

Now that we have a solid white line we ensure there is enough space for the vehicle
to pull over (the emergency lane is wide enough).
We project multiple points on the other side of the white line and then we only
consider points which distance from the line is about the width of the vehicle (a bit more).

Now we consider a ground plane and then measure the height of each considered point from
this plane.
If there are multiple points which distance from the plane is relevantly high, we
then assume that there is some obstacle in the emergency lane -> NOT SAFE.

#### Pros
- Higher capability of detecting a safe pull over spot with confidence
#### Cons
- Expensive sensors required


## Calculations by ChatGPT (to be verified)
Let’s calculate it carefully step by step.

Given:

* Initial speed ( v_i = 14 , \text{m/s} )
* Final speed ( v_f = 0 , \text{m/s} )
* Deceleration ( a = 2 , \text{m/s}^2 )

We use the basic kinematic relation for constant acceleration:
[
v_f = v_i - a t
]

Solve for time ( t ):

[
t = \frac{v_i - v_f}{a}
]

Substitute the values:

[
t = \frac{14 - 0}{2} = \frac{14}{2} = 7
]

✅ **Answer:**
It will take **7 seconds** to come to a stop if you decelerate gently at **2 m/s²** from 14 m/s (≈ 50 km/h).

Would you also like me to calculate the **stopping distance** for that case?

Perfect 👍

We can find the **stopping distance** using the kinematic formula:

[
d = \frac{v_i^2 - v_f^2}{2a}
]

Given:

* ( v_i = 14 , \text{m/s} )
* ( v_f = 0 , \text{m/s} )
* ( a = 2 , \text{m/s}^2 )

Substitute:

[
d = \frac{14^2 - 0^2}{2 \times 2} = \frac{196}{4} = 49
]

✅ **Answer:**
It will take **7 seconds** and **49 meters** to come to a smooth stop from **14 m/s** with a **2 m/s²** deceleration.

That’s a comfortable, natural-feeling stop — similar to how a skilled driver would brake gently to a halt from ~50 km/h.
