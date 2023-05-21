# Polynomial Interpolation Example

The objective of this project is to show how polynomial interpolation works and its application in video games. This program includes two files: `Hermite.py` and `make_curve.py`.

## Requirements

This program requires the following Python modules:

- `numpy`
- `math`
- `pygame`

If you don't have them installed, you can install them by running the following command:

- `pip install numpy`
- `pip install pygame`

## Usage

To use the programs, run the following files:

### hermite.py

The `hermite.py` file is an example of how to use polynomial interpolation for smooth jumping in a video game.

#### Control Tips:

- To jump without interpolation, press the E key.
- To jump with interpolation, press the Q key.

### make_curve.py

This program generates a curve from a given set of user-defined points.

#### Algorithms:

- Lagrange Interpolation
- Bezier Interpolation
- Cubic Hermite Interpolation
- Cubic Spline Interpolation

#### Control Tips:

- Double click on the point to move point or time point (if you show curve using lagrange polynomial interpolation)
- Single click on the point to highlight point and show delete button
