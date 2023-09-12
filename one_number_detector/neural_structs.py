from typing import Optional
import random
import numpy as np
import asyncio


class Neuron():
    def __init__(self, inp_count: int, inp_weights: Optional[list[int]] = None) -> None:

        if inp_count < 1:
            raise ValueError("У нейрона не может быть меньше одного входа")
        self.input_count: int = inp_count + 1
        self.input_weights: list = inp_weights
        if len(self.input_weights) != (self.input_count):
            raise ValueError("Количество весовых коэффициентов должно удовлетворять формуле <кол-во входов + 1>")
        
    
    @classmethod
    def random_init(cls, inp_count: int):
        inp_w = [random.random()-random.random() for inp in range(inp_count+1)]
        return cls(inp_count, inp_w)


    def _activation_func(self, x) -> int:
        if x <= 0:
            return 0
        else:
            return 1
    

    def activation(self, inputs: list[int]) -> int:
        s = 0
        for i in range(len(inputs)):
            s += inputs[i]*self.input_weights[i]
        return self._activation_func(s)


    def learn(self, inputs: list[int], target: int, intensity: int) -> int:
        """
        Проводит обучение нейрона на основе тестовых данных
        inputs - набор входных сигналов
        target - ожидаемый вывод нейрона

        Возвращает 1, если ответ был неправильным
        Иначе 0
        """
        out = self.activation(inputs)
        dout = target - out
        if dout != 0:
            for i in range(len(inputs)):
                self.input_weights[i] += dout*inputs[i]*intensity
            return 1
        return 0



class NeuronLayer():
    def __init__(self, neurons_count: int, inp_count: int, random: bool = True, weights_matrix: Optional[list[list[int]]] = None) -> None:
        self.input_count: int = inp_count + 1
        self.neurons_count: int = neurons_count
        if random == True:
            self.neurons = [Neuron.random_init(inp_count) for i in range(neurons_count)]
        else:
            t_wm = weights_matrix
            self.neurons = [Neuron(inp_count, t_wm[i]) for i in range(neurons_count)]
    

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            data = f.read()
        lined_data = data.split('\n')
        wm = [[np.float64(char) for char in string.split('|')] for string in lined_data]     
        inp_count = len(wm[0]) - 1
        neuron_count = len(wm)
        return cls(neuron_count, inp_count, False, wm)


    def get_weight_matrix(self):
        return [self.neurons[i].input_weights for i in range(self.neurons_count)]
    

    def set_weight_matrix(self, weights_matrix: Optional[list[list[int]]]):
        t_wm = weights_matrix
        for i in range(self.neurons_count):
            self.neurons[i].input_weights = t_wm[i]


    def activation(self, inputs: list[int]) -> list[int]:
        return [self.neurons[i].activation(inputs) for i in range(self.neurons_count)]
    

    def polarizated_activation(self, inputs: list[int]) -> list[int]:
        p_inputs = np.insert(inputs, 0, 1)
        return self.activation(p_inputs)
    

    def save_model(self, iteration_count: int, intensity: int):
        wm = self.get_weight_matrix()
        data = '\n'.join(['|'.join(string) for string in [[str(i) for i in s] for s in wm]])
        with open("inp{}_neu{} {}it_{}int.txt".format(self.input_count-1, self.neurons_count, iteration_count, int(intensity)), "w") as f:
            f.write(data)



class PerseptronTrainer():
    def __init__(self, layer: NeuronLayer, dataset: list, intensity: int) -> None:
        self.dataset = dataset
        self.net = layer
        self.intensity = intensity
        self.iteration = 0
        self.dataset_fails = [1 for i in dataset]
        self.done = False

        self._polarize_dataset_inputs()


    def _polarize_dataset_inputs(self):
        for set in self.dataset:
                set[0].insert(0, 1)


    def _calculate_errors(self, d: list[int]) -> int:
        i = 0
        for dev in d:
            if dev != 0:
                i += 1
        return i
    

    def _dataset_sero_err(self) -> bool:
        for n in self.dataset_fails:
            if n!= 0:
                return False
        return True


    def training_cycle(self) -> int:
        while self.done == False:
            for set_id in range(len(self.dataset)):
                set = self.dataset[set_id]
            
                fails = 0
                for i in range(len(self.net.neurons)):
                    fails += self.net.neurons[i].learn(set[0], set[1][i], self.intensity)

                self.dataset_fails[set_id] = fails
                
                print("Iteration: {}; Fails: {}; DS_Fails: {}, Set: {}".format(self.iteration, fails, self._calculate_errors(self.dataset_fails), set_id))
                yield self._calculate_errors(self.dataset_fails)

                if self._dataset_sero_err() or self.iteration == 300000:
                    self.net.save_model(self.iteration, self.intensity)
                    print(self.dataset_fails)
                    self.done = True
                    yield '-END-'
                    break
            
            self.iteration += 1


    async def training(self, intensity):
        while self.done == False:
            for set_id in range(len(self.dataset)):
                set = self.dataset[set_id]
            
                fails = 0
                for i in range(len(self.net.neurons)):
                    fails += self.net.neurons[i].learn(set[0], set[1][i], intensity)

                self.dataset_fails[set_id] = fails

                print("Iteration: {}; Fails: {}; DS_Fails: {}, Set: {}".format(self.iteration, fails, self._calculate_errors(self.dataset_fails), set_id))

                if self._dataset_sero_err() or self.iteration == 300000:
                    self.net.save_model(self.iteration, intensity)
                    print(self.dataset_fails)
                    self.done = True
                    break
            
            self.iteration += 1