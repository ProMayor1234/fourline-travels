def calculate_njveterans_cost(hours):
    """Calculate the capped total cost for NJ Veterans services.

    Args:
        hours (int or float): Number of service hours.

    Returns:
        int or float: Total cost capped at the maximum allowed amount.
    """
    hourly_rate = 125  # Cost per hour of service
    max_amount = 1000  # Maximum charge allowed for the engagement
    total = hours * hourly_rate  # Uncapped total based on hours worked
    if total > max_amount:
        return max_amount  # Apply the maximum cap if the total exceeds it
    return total  # Return the uncapped total when it is within the limit