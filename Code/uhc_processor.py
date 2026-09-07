def calculate_uhc_cost(miles):
    """Calculate the total cost for a UHC trip.

    Args:
        miles (int or float): Distance in miles.

    Returns:
        int or float: Total trip cost including the base rate and mileage fee.
    """
    base_rate = 85  # Fixed starting fee for the trip
    milage_rate = 3  # Cost per mile traveled
    total_cost = base_rate + (miles * milage_rate)  # Add mileage charge to base rate
    return total_cost