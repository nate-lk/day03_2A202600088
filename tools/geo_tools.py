# geo_tools.py

from typing import TypedDict
import math


class Location(TypedDict):
    lat: float
    lon: float


def geocode(city: str) -> Location:
    city_map = {
        "hanoi":            {"lat": 21.0285,  "lon": 105.8542},
        "ho chi minh city": {"lat": 10.8231,  "lon": 106.6297},
        "new york":         {"lat": 40.7128,  "lon": -74.0060},
        "london":           {"lat": 51.5074,  "lon": -0.1278},
    }
    key = city.lower()
    if key not in city_map:
        raise ValueError(f"Unknown city: '{city}'. Known cities: {list(city_map)}")
    return city_map[key]


def haversine(loc1: Location, loc2: Location) -> float:
    R = 6371
    phi1    = math.radians(loc1["lat"])
    phi2    = math.radians(loc2["lat"])
    dphi    = math.radians(loc2["lat"] - loc1["lat"])
    dlambda = math.radians(loc2["lon"] - loc1["lon"])
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def get_distance(city1: str, city2: str) -> str:
    loc1 = geocode(city1)
    loc2 = geocode(city2)
    km   = haversine(loc1, loc2)
    return f"{km} km"


# Tool definition — includes "fn" so the agent can call it directly
tool_schema = {
    "name":        "get_distance",
    "description": "Calculate the distance in km between two cities by name.",
    "fn":          get_distance,          # ← callable attached here
    "parameters": {
        "type": "object",
        "properties": {
            "city1": {"type": "string"},
            "city2": {"type": "string"},
        },
        "required": ["city1", "city2"],
    },
}


if __name__ == "__main__":
    print(get_distance("Hanoi", "Ho Chi Minh City"))
