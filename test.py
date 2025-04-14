from app import get_distance

if __name__ == "__main__":

    origin = "Cowell College UC Santa Cruz"
    destination = "Sixth College UC San Diego"

    distance_meters = get_distance(origin, destination)
    print(f"Distance from '{origin}' to '{destination}': {distance_meters / 1000:.2f} km")
