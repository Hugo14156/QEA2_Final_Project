import json
from typing import List, Tuple


class ConvertedPoints:

    # attributes
    point_resolution: int
    wave_count: int
    total_points: int
    stored_points: int
    points: List[Tuple[float, float]]

    def __init__(
        self,
        point_resolution: int,
        wave_count: int,
        total_points: int,
        stored_points: int,
        points: List[Tuple[float, float]],
    ):

        self.point_resolution = point_resolution
        self.wave_count = wave_count
        self.total_points = total_points
        self.stored_points = stored_points
        self.points = points

    @staticmethod
    def load_from_file(filename: str):
        with open(filename, "r") as f:
            data = json.load(f)
            point_resolution = data["point_resolution"]
            wave_count = data["wave_count"]
            total_points = data["total_points"]
            stored_points = data["stored_points"]
            points = data["points"]
            return ConvertedPoints(
                point_resolution, wave_count, total_points, stored_points, points
            )

    def save_to_file(self, filename: str):
        with open(filename, "w") as f:
            json.dump(
                {
                    "point_resolution": self.point_resolution,
                    "wave_count": self.wave_count,
                    "total_points": self.total_points,
                    "stored_points": self.stored_points,
                    "points": self.points,
                },
                f,
            )


class DrawingPoints:

    # attributes
    drawn_points: List[Tuple[int, int]]
    point_resolution: int
    wave_count: int

    def __init__(
        self,
        drawn_points: List[Tuple[int, int]],
        point_resolution: int,
        wave_count: int,
    ):
        self.drawn_points = drawn_points
        self.point_resolution = point_resolution
        self.wave_count = wave_count

    @staticmethod
    def load_from_file(filename: str):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

            drawn_points = data["drawn_points"]
            point_resolution = data["point_resolution"]
            wave_count = data["wave_count"]
            return DrawingPoints(drawn_points, point_resolution, wave_count)

    def save_to_file(self, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "drawn_points": self.drawn_points,
                    "point_resolution": self.point_resolution,
                    "wave_count": self.wave_count,
                },
                f,
                indent=2,
            )
