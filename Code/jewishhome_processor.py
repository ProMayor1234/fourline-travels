def calculate_jewishhome_cost(miles):
    """Calculate the total cost for a Jewish Home trip.

    Args:
        miles (int or float): One-way distance in miles.

    Returns:
        int or float: Total trip cost including base rate and round-trip mileage.
    """
    base_rate = 70  # Fixed starting fee for the service
    mileage_rate = 3  # Charge per mile
    legs = 2  # Round-trip multiplier (outbound + return)
    total = base_rate + (miles * mileage_rate * legs)
    return total