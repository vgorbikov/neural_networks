from typing import Optional
import random
import numpy as np



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
        #важно помнить что весовой коэффициент с индексом 0 является пороговым значением и в сумматор не попадает
        s = sum([inputs[i]*self.input_weights[i] for i in range(0, self.input_count)])
        return self._activation_func(s)



class NeuronLayer():
    def __init__(self, neurons_count: int, inp_count: int, random: bool = True, weights_matrix: Optional[list[list[int]]] = None) -> None:
        self.input_count: int = inp_count + 1
        self.neurons_count: int = neurons_count
        if random == True:
            self.neurons = [Neuron.random_init(inp_count) for i in range(neurons_count)]
        else:
            t_wm = np.transpose(weights_matrix)
            self.neurons = [Neuron(inp_count, t_wm[i]) for i in range(neurons_count)]
    

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            data = f.read()
        lined_data = data.split('\n')
        wm = [[np.float64(char) for char in string.split('|')] for string in lined_data]     
        neuron_count = len(wm[0])
        inp_count = len(wm) - 1
        return cls(neuron_count, inp_count, False, wm)

    def get_weight_matrix(self):
        return np.transpose([self.neurons[i].input_weights for i in range(self.neurons_count)])
    

    def set_weight_matrix(self, weights_matrix: Optional[list[list[int]]]):
        t_wm = np.transpose(weights_matrix)
        for i in range(self.neurons_count):
            self.neurons[i].input_weights = t_wm[i]


    def activation(self, inputs: list[int]) -> list[int]:
        return np.array([self.neurons[i].activation(inputs) for i in range(self.neurons_count)])
    

    def save_model(self, iteration_count: int, intensity: int):
        wm = self.get_weight_matrix()
        data = '\n'.join(['|'.join(string) for string in [[str(i) for i in s] for s in wm]])
        with open("inp{}_neu{} {}it_{}int.txt".format(self.input_count-1, self.neurons_count, iteration_count, int(intensity)), "w") as f:
            f.write(data)



class PerseptronTrainer():
    def __init__(self, layer: NeuronLayer, dataset: list) -> None:
        self.dataset = dataset
        self.net = layer
        self.iteration = 0
        self.dataset_fails = [1 for i in dataset]
        self.done = False


    def _calculate_errors(self, d: list[int]) -> int:
        i = 0
        for dev in d:
            if dev != 0:
                i += 1
        return i
    

    def _dataset_sero_err(self):
        for n in self.dataset_fails:
            if n!= 0:
                return False
        return True



    def start_training(self, intensity: float):
        print("Train started")
        while self.done == False:
            for set_id in range(len(self.dataset)):
                set = self.dataset[set_id]
            
                set[0].insert(0, 1)
                inp_v = np.array(set[0])
                out_v = self.net.activation(inp_v)
                dout = np.array(set[1]) - out_v

                wm = self.net.get_weight_matrix()
                for i in range(self.net.input_count):
                    for n in range(self.net.neurons_count):
                        wm[i][n] += dout[n]*inp_v[i]*intensity

                self.net.set_weight_matrix(wm)

                fails = self._calculate_errors(dout)
                
                self.dataset_fails[set_id] = fails

                print("Iteration: {}; Set: {}; Out: {}; Fails: {}; Set_fails: {}".format(self.iteration, set_id, out_v, fails, self._calculate_errors(self.dataset_fails)))
                if self._dataset_sero_err() or self.iteration == 100000000:
                    self.net.save_model(self.iteration, intensity)
                    print(self.dataset_fails)
                    self.done = True
            
            self.iteration += 1

            




def dataset_target_decode(target: int, neurons_count: int):
    v = [0 for i in range(neurons_count)]
    v[target-1] = 1
    return v



def dataset_decoder(path: str, neurons_count: int):
    with open(path, 'r') as f:
        data = f.read()
    lined_data = data.split('\n')
    lined_data.pop()
    return [[[int(x) for x in set[0].split('|')], dataset_target_decode(int(set[1]), neurons_count)] for set in [line.split('>') for line in lined_data]]


l = NeuronLayer(10, 35, True)
t = PerseptronTrainer(l, dataset_decoder('ond_dataset_5rsl.txt', 10))
t.start_training(0.1)

