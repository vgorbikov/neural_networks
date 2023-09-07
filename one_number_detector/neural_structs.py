from typing import Optional
import random

class Neuron():
    def __init__(self, inp_count: int, inp_weights: Optional[list[int]] = None) -> None:
        if inp_count < 1:
            raise ValueError("У нейрона не может быть меньше одного входа")
        self.input_count: int = inp_count

        self.input_weights: list = inp_weights or [random.random() if inp!=0 else 1 for inp in range(inp_count + 1)]
        if len(self.input_weights) != (inp_count + 1):
            raise ValueError("Количество весовых коэффициентов должно удовлетворять формуле <кол-во входов + 1>")

        self.activation_func = lambda x: (0 if x < self.input_weights[0] else x)

