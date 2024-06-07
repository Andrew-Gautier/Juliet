import random




def update_locations(vulnerable_locations, num_lines_before, window_size):
    updated_locations = []
    for location in vulnerable_locations:
        adjusted_location = location - num_lines_before
        if adjusted_location < 0:
            adjusted_location = 0
        elif adjusted_location >= window_size:
            adjusted_location = window_size - 1
        updated_locations.append(adjusted_location)
    return updated_locations

def get_random_values(window_size):
    num_lines_before = random.randint(1, window_size - 1)
    num_lines_after = window_size - 1 - num_lines_before
    return num_lines_before, num_lines_after

# Hardcoded values for testing
vulnerable_lines = [10, 20, 30]
window_size = 40 

num_lines_before, num_lines_after = get_random_values(window_size)
updated_locations = update_locations(vulnerable_lines, num_lines_before, window_size)

print(f"Original locations: {vulnerable_lines}")
print(f"Updated locations: {updated_locations}")