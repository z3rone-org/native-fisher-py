class EstimatorResults:
    pass

class PrecisionEstimate:
    def __init__(self, raw_file=None, scan_number=0):
        self.raw_file = raw_file
        self.scan_number = scan_number

    def get_ion_time(self):
        return 0.0

    def get_mass_precision_estimate(self, mass):
        return 0.0

    def dispose(self):
        pass
