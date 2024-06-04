class Node:
    def __init__(self, DC: int, rank: int = 1) -> None:
        self.id = None  # Will be set by the Graph class
        self.rank = rank
        self.temp_rank = 0  # Temporary rank for calculation
        self.DC = DC