import cmath
import math
from typing import List, Tuple


def compute_fourier_coefficients(
    points: List[Tuple[float, float]],
) -> List[Tuple[float, float, float]]:
    """
    Compute the Discrete Fourier Transform (DFT) for the given points.
    Maps indices to signed frequencies (low frequencies near 0).
    """
    N = len(points)
    if N == 0:
        return []

    coeffs = []
    # Convert coordinate pairs to a series of complex numbers
    z = [complex(p[0], p[1]) for p in points]

    for k in range(N):
        # Calculate the complex coefficient Ck
        # C_k = (1/N) * sum(z_n * exp(-i * 2pi * k * n / N))
        c_k = sum(z[n] * cmath.exp(-2j * math.pi * k * n / N) for n in range(N))
        c_k /= N

        if k <= N // 2:
            freq = float(k)
        else:
            freq = float(k - N)

        magnitude = abs(c_k)
        phase = cmath.phase(c_k)

        coeffs.append((freq, magnitude, phase))

    # Sort by magnitude (descending) so the largest components are handled first
    coeffs.sort(key=lambda x: x[1], reverse=True)
    return coeffs


def get_points_from_coeffs(
    coeffs: List[Tuple[float, float, float]], num_points: int = 1000
) -> List[Tuple[float, float]]:
    """
    Reconstruct the path from the Fourier coefficients.
    """
    path = []
    for i in range(num_points):
        # t must go from 0 to 2*pi over the course of num_points
        t = 2 * math.pi * (i / num_points)
        x_sum = 0
        y_sum = 0
        for freq, mag, phase in coeffs:
            x_sum += mag * math.cos(freq * t + phase)
            y_sum += mag * math.sin(freq * t + phase)
        path.append((x_sum, y_sum))
    return path
