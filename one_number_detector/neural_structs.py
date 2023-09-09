from typing import Optional
import random
import numpy as np



class Neuron():
    def __init__(self, inp_count: int, inp_weights: Optional[list[int]] = None) -> None:

        if inp_count < 1:
            raise ValueError("У нейрона не может быть меньше одного входа")
        self.input_count: int = inp_count + 1

        self.input_weights: list = inp_weights or [random.random() for inp in range(self.input_count)]
        if len(self.input_weights) != (self.input_count):
            raise ValueError("Количество весовых коэффициентов должно удовлетворять формуле <кол-во входов + 1>")


    def _activation_func(self, x) -> int:
        if x < self.input_weights[0]:
            return 0
        else:
            return 1
    

    def activation(self, inputs: list[int]) -> int:
        #важно помнить что весовой коэффициент с индексом 0 является пороговым значением и в сумматор не попадает
        s = sum([inputs[i]*self.input_weights[i] for i in range(1, self.input_count)])
        print(s)
        return self._activation_func(s)



class NeuronLayer():
    def __init__(self, neurons_count: int, inp_count: int, weights_matrix: Optional[list[list[int]]] = None) -> None:
        self.input_count: int = inp_count + 1
        self.neurons_count: int = neurons_count
        t_wm = np.transpose(weights_matrix)
        if weights_matrix != None:
            self.neurons = [Neuron(inp_count, t_wm[i]) for i in range(neurons_count)]
        else: 
            self.neurons = [Neuron(inp_count) for i in range(neurons_count)]


    def get_weight_matrix(self):
        return np.transpose([self.neurons[i].input_weights for i in range(self.neurons_count)])
    

    def set_weight_matrix(self, weights_matrix: Optional[list[list[int]]]):
        t_wm = np.transpose(weights_matrix)
        for i in range(self.neurons_count):
            self.neurons[i].input_weights = t_wm[i]


    def activation(self, inputs: list[int]) -> list[int]:
        return [self.neurons[i].activation(inputs) for i in range(self.neurons_count)]



def train(layer: NeuronLayer):
    pass