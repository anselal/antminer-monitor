class BaseMiner:
    def __init__(self, miner):
        self.id = miner.id
        self.ip = miner.ip
        self.model_id = miner.model_id
        self.remarks = miner.remarks
        self.is_inactive = False
        self.worker = ""
        self.chips = {}
        self.temperatures = []
        self.fan_speeds = []
        # this value will be used to calculate `total_hash_rate_per_model`
        self.hash_rate_ghs5s = 0
        # this value will be displayed in the table
        self.normalized_hash_rate = 0
        self.hw_error_rate = 0
        self.uptime = ""
        self.warnings = []
        self.errors = []

    def poll(self):
        pass

