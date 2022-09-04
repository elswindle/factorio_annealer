

class AnnealerOptions:
    def __init__(
        self,
        initial_temperature=1000,
        moves_per_iteration=50,
        max_iterations=10000,
        function_tolerance=0.5,
    ):
        self.annealer_args = {
            "initial-temperature": initial_temperature,
            "moves-per-iteration": moves_per_iteration,
            "max-iterations": max_iterations,
            "function-tolerance": function_tolerance,
        }