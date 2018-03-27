# Update from one unit to the next if the value is greater than 1024.
# e.g. update_unit_and_value(1024, "GH/s") => (1, "TH/s")


def update_unit_and_value(value, unit):
    while value > 1024:
        value = value / 1024.0
        if unit == 'MH/s':
            unit = 'GH/s'
        elif unit == 'GH/s':
            unit = 'TH/s'
        elif unit == 'TH/s':
            unit = 'PH/s'
        elif unit == 'PH/s':
            unit = 'EH/s'
        else:
            assert False, "Unsupported unit: {}".format(unit)
    return (value, unit)
