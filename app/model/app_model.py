import cmath
import math
from typing import List, Tuple


def compute_fourier_coefficients(
    points: List[Tuple[float, float]],
) -> List[Tuple[float, float, float]]:
    """
    Compute the Discrete Fourier Transform (DFT) for the given points.

    Will return a list of tuples of the form (frequency, amplitude, phase)
    sorted by amplitude in descending order
    """

    # TODO: do the math for the DFT
    N = len(points)
    if N == 0:
        return []

    coeffs = []
    # Convert coordinate pairs to a series of complex numbers
    z = [complex(p[0], p[1]) for p in points]

    for k in range(N):
        # Calculate the complex coefficient Ck

        # Look at [FOURIER_MATH.md] for the math
        # C_k = 1/N * sum from n=0 to N-1 of (z_n * e^(-i * 2pi * k * n / N))
        # where z_n is the n-th point in the path, i is the imaginary unit
        # and N is the number of points

        # What this is doing is taking the dot product of the path with a complex exponential
        # This is a way of projecting the path onto a complex exponential
        # The result is a complex number that tells us how much of that complex exponential
        # is in the path
        # The real component of C_k is the amplitude of the cosine wave
        # The imaginary component of C_k is the amplitude of the sine wave
        # The phase of C_k is the phase of the cosine wave
        c_k = sum(z[n] * cmath.exp(-2j * math.pi * k * n / N) for n in range(N))
        c_k /= N

        if k <= N // 2:
            freq = float(k)
        else:
            freq = float(k - N)

        amplitude = abs(c_k)
        phase = cmath.phase(c_k)

        coeffs.append((freq, amplitude, phase))

    # Sort by amplitude (descending) so the largest components are handled first
    # amplitude is the second element in the tuple
    coeffs.sort(key=lambda x: x[1], reverse=True)
    return coeffs


def get_points_from_coeffs(
    coeffs: List[Tuple[float, float, float]], num_points: int = 1000
) -> List[Tuple[float, float]]:
    """
    Constructs a path made from the sum of the sine waves over one full period
    This is the "inverse" of the DFT
    """
    path = []
    # loop over the number of points to reconstruct
    for i in range(num_points):
        # period of the whole path is 2*pi, we want a certain percentage of the way through
        t = 2 * math.pi * (i / num_points)
        x_sum = 0
        y_sum = 0
        # sum up all the sine waves at this point on the path
        for freq, amplitude, phase in coeffs:
            x_sum += amplitude * math.cos(freq * t + phase)
            y_sum += amplitude * math.sin(freq * t + phase)
        path.append((x_sum, y_sum))
    return path
