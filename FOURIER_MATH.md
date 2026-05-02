# The Mathematics of Fourier Epicycles

This document explains the mathematical logic implemented in `app/model/app_model.py`. The goal of the Fourier transform in this project is to convert a sequence of 2D coordinates (a drawing) into a set of rotating circles (epicycles) that can reconstruct that drawing.

## 1. The Complex Plane ($z = x + iy$)
To perform the transform, we treat 2D spatial coordinates $(x, y)$ as numbers in the **complex plane**. A single complex number $z$ can represent a 2D position:
$$z = x + iy$$
In the code, this is handled by:
```python
z = [complex(p[0], p[1]) for p in points]
```
Using complex numbers is essential because rotations—the core of circular motion—are mathematically elegant to calculate using complex exponents.

## 2. The Discrete Fourier Transform (DFT)
The Discrete Fourier Transform takes $N$ complex points and decomposes them into $N$ frequency components. The formula for each complex coefficient $C_k$ is:

$$C_k = \frac{1}{N} \sum_{n=0}^{N-1} z_n e^{-i \frac{2\pi}{N} kn}$$

### Breakdown of the Code:
```python
c_k = sum(z[n] * cmath.exp(-2j * math.pi * k * n / N) for n in range(N)) / N
```
*   **$z_n$**: The input points from your drawing.
*   **$e^{-i \theta}$**: Euler's Formula ($\cos \theta - i \sin \theta$). This represents the "spinning" component used to test for a specific frequency $k$.
*   **$C_k$**: The resulting complex coefficient.

### A Deeper Perspective: The "Dot Product" and Projection
Mathematically, the DFT is a **Dot Product** between your drawing and a reference wave. 

Imagine your drawing $z$ is a high-dimensional vector. We want to know how much this vector "projects" onto a set of basis vectors. In this case, our basis vectors are perfect complex sinusoids (spinning circles) of different frequencies.

1.  **Similarity Measurement:** When we multiply $z_n$ by $e^{-i \dots}$, we are measuring how similar the drawing is to a perfect circle spinning at frequency $k$.
2.  **Projection:** The summation $\sum$ acts as the dot product. If the drawing "overlaps" with the reference frequency, the result is a large $C_k$. If they are unrelated (orthogonal), the result is near zero.
3.  **Change of Basis:** This is ultimately a **Change of Basis**. 
    *   **Spatial Basis:** Describing the drawing as a sequence of $(x, y)$ coordinates in time.
    *   **Frequency Basis:** Describing the drawing as a list of "ingredients"—how much of each rotating circle is required to build it. 

Both bases describe the exact same shape, but the Frequency Basis allows us to "compress" the drawing by only keeping the most important circles (the ones with the largest amplitudes).

## 3. Selecting Frequencies ($k$)
A common question is: *How do we know which frequencies to test?*

In the Discrete Fourier Transform, we always test exactly $N$ frequencies, where $N$ is the number of points in your drawing. These frequencies are always integers ($k = 0, 1, 2, \dots, N-1$) for two primary reasons:

### A. The Requirement of Periodicity
The Fourier Series assumes the signal is periodic—meaning it repeats forever. A 2D drawing is treated as one full "period" of a loop. For the reconstructed drawing to be "closed" (meaning the end of the line meets the start of the line), every individual circle in the chain must complete a **whole number of rotations** during that period.
*   If a circle rotated 1.5 times, the drawing would end at a different location than it started, creating a "jump" in the line.
*   By using integers, we ensure that at the end of the cycle, every vector has returned exactly to its starting orientation.

### B. The Nyquist Limit and Information
With $N$ sampled points, we have a finite amount of information. Mathematically, $N$ points can only uniquely define $N$ distinct frequencies. 
*   **Low Frequencies ($k$ near 0):** Capture the "big picture" shape and general curves.
*   **High Frequencies ($k$ near $N/2$):** Capture the fine details, sharp corners, and "jitter" in your drawing.
*   Frequencies higher than $N$ would be redundant (a phenomenon called aliasing), effectively "skipping" over the points we've already measured.

## 4. Extracting Circle Properties
Each coefficient $C_k$ tells us exactly how to draw one rotating circle in the "chain":

1.  **Amplitude (Radius):** The magnitude of the complex number, $|C_k|$, determines how large the circle is.
    *   `amplitude = abs(c_k)`
2.  **Phase (Starting Angle):** The argument or angle of the complex number, $\arg(C_k)$, determines where the circle starts its rotation.
    *   `phase = cmath.phase(c_k)`
3.  **Frequency (Speed):** The index $k$ determines how fast the circle spins. The code maps these to **signed frequencies** so that:
    *   $k=1$ spins once counter-clockwise.
    *   $k=-1$ (mapped from $N-1$) spins once clockwise.

## 4. Reconstruction (Inverse DFT)
To redraw the shape, we sum the contributions of all these circles over time $t$ (from $0$ to $2\pi$):

$$\text{Position}(t) = \sum C_k \cdot e^{i(\text{freq} \cdot t + \text{phase})}$$

In `get_points_from_coeffs`, this is performed as:
```python
x_sum += amplitude * math.cos(freq * t + phase)
y_sum += amplitude * math.sin(freq * t + phase)
```
As the code loops through $t$, the "tip" of the final rotating vector traces the path of the original drawing. By sorting coefficients by amplitude, we ensure that the most significant "circles" are handled first, allowing us to approximate the shape even if we limit the number of waves used.
