import asyncio
import PySimpleGUI as sg
import neural_structs as ns
import time


sg.theme('Dark Blue 3')


#адаптер к холсту
class DrawGrid():
    def __init__(self, width, height, h_resolution) -> None:
        self.width: int = width
        self.height: int = height
        self.h_resolution = h_resolution
        self.grid_step: int = round(self.width/self.h_resolution)
        self.gwidth = self.width//self.grid_step
        self.gheight = self.height//self.grid_step
        #холст
        self.area: sg.Graph = sg.Graph(canvas_size=(self.width, self.height), 
                     graph_bottom_left=(0, self.height), 
                     graph_top_right=(self.width, 0), 
                     background_color='white',
                     key='-INPUT-',
                     enable_events=True,
                     drag_submits=True)
        
        self.work_grid_vert = []
        self.work_grid_hor = []

        self.objects = []
        self.binary_set: list[int] = [0 for i in range(0, self.gwidth*self.gheight)]


    def draw_grid(self):
        #Сетка для разбиения на "пиксели"
        self.work_grid_vert = [self.area.draw_line((x, 0), (x, self.height), color='grey') for x in range(0, self.width, self.grid_step)]
        self.work_grid_hor = [self.area.draw_line((0, y), (self.width, y), color='grey') for y in range(0, self.height, self.grid_step)]


    def _update_grid(self):
        self.clear()
        self.binary_set: list[int] = [0 for i in range(0, self.gwidth*self.gheight)]
        for vert in self.work_grid_vert:
            self.area.delete_figure(vert)
        for hor in self.work_grid_hor:
            self.area.delete_figure(hor)
        self.draw_grid()


    def update_resolution(self, resolution):
        self.h_resolution = resolution
        self.grid_step: int = round(self.width/self.h_resolution)
        self.gwidth = self.width//self.grid_step
        self.gheight = self.height//self.grid_step
        self._update_grid()


    def clear(self):
        for obj in self.objects:
            self.area.delete_figure(obj)
            self.binary_set = [0 for i in range(0, self.gwidth*self.gheight)]


    async def draw(self, x, y):
        gx = (x//self.grid_step)
        gy = (y//self.grid_step)
        if self.binary_set[gy*self.gwidth + gx] != 0:
            return
        rx = gx*self.grid_step
        ry = gy*self.grid_step
        async def dr():
            self.objects.append(self.area.draw_rectangle((rx, ry), (rx+self.grid_step, ry+self.grid_step), fill_color='black'))
        await(asyncio.create_task(dr()))
        self.binary_set[gy*self.gwidth + gx] = 1



class PresentationWindow():
    def __init__(self) -> None:
        self.grid = DrawGrid(500, 700, 5)

        #размещаем нужные элементы в окне
        self.presentation_layout = [
            [sg.Text('Нарисуйте цифру'), sg.Text(size=(12,1))],
            [self.grid.area],
            [sg.Text('Это выглядит как: ', key='-OUT-')],
            [sg.Button('Clear'), sg.Button('Exit')]]
        self.presentation_window = sg.Window('Work Presentation', self.presentation_layout, finalize=True)

        #создаём сетку для рисования
        self.grid.draw_grid()

        self.net = ns.NeuronLayer.load('inp35_neu10 16it_0int.txt')


    def update_answer(self, answer: int):
        self.presentation_window['-OUT-'].update('Это выглядит как: {}'.format(answer))

    
    def out_description(self, v: list):
        v = list(v)
        try:
            return v.index(1)
        except:
            return "Что-то"


    async def open(self):
        while True:  # Event Loop
            event, values = self.presentation_window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if event == '-INPUT-':
                await asyncio.create_task(self.grid.draw(*values['-INPUT-']))
            if event == 'Clear':
                self.grid.clear()
            if event == '-INPUT-+UP':
                out = self.net.polarizated_activation(self.grid.binary_set)
                self.update_answer(self.out_description(out))

        self.presentation_window.close()



class GenerateWindow():
    def __init__(self) -> None:
        self.grid = DrawGrid(500, 700, 5)

        #размещаем нужные элементы в окне
        self.presentation_layout = [
            [sg.Text('Нарисуйте цифру'), sg.Text(size=(12,1))],
            [self.grid.area, sg.Combo([5, 10, 15, 20, 25, 30], key="-RESOLUTION-", default_value=5, enable_events=True)],
            [sg.Button('Сохранить набор данных для цифры: ', key="-SAVE-"), 
             sg.Combo(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'], key="-DATASET_REFERENCE-", default_value=1)],
            [sg.Button('Clear'), sg.Button('Exit')]]
        self.presentation_window = sg.Window('Work Presentation', self.presentation_layout, finalize=True)

        #создаём сетку для рисования
        self.grid.draw_grid()


    def save_dataset(self, target: int, dataset: list[int]):
        zipdata = '|'.join([str(i) for i in dataset]) + '>{}\n'.format(target)
        with open("ond_dataset_{}rsl.txt".format(self.grid.h_resolution), "a") as f:
            f.writelines(zipdata)


    async def open(self):
        while True:  # Event Loop
            event, values = self.presentation_window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if event == '-INPUT-':
                await asyncio.create_task(self.grid.draw(*values['-INPUT-']))
            if event == 'Clear':
                self.grid.clear()
            if event == '-SAVE-':
                self.save_dataset(values['-DATASET_REFERENCE-'], self.grid.binary_set)
            if event == '-RESOLUTION-':
                self.grid.update_resolution(values['-RESOLUTION-'])

        self.presentation_window.close()



class TrainWindow():
    def __init__(self) -> None:
        self.width = 500
        self.height = 300
        self.stat_points = []
        self.graph_area: sg.Graph = sg.Graph(canvas_size=(self.width, self.height), 
                     graph_bottom_left=(0, 0), 
                     graph_top_right=(self.width, self.height), 
                     background_color='white',
                     key='-GRAPH-')

        #размещаем нужные элементы в окне
        self.presentation_layout = [
            [sg.Text('Обучение')],
            [sg.T('Выберите файл с данными для обучения:'), sg.FileBrowse(button_text="Выбрать", key='-FILE-')],
            [sg.Text('Отклонение от тестового набора:')],
            [self.graph_area],
            [sg.Button('Начать обучение', key='-START-'), sg.Button('Остановить обучение', key='-STOP-'), sg.Button('Exit')]]
        self.presentation_window = sg.Window('Work Presentation', self.presentation_layout, finalize=True)
        self.net = None
        self.trainer = None


    def dataset_target_decode(self, target: int, neurons_count: int):
        v = [0 for i in range(neurons_count)]
        v[target] = 1
        return v


    def dataset_decoder(self, path: str, neurons_count: int):
        with open(path, 'r') as f:
            data = f.read()
        lined_data = data.split('\n')
        return [[[int(x) for x in set[0].split('|')], self.dataset_target_decode(int(set[1]), neurons_count)] for set in [line.split('>') for line in lined_data]]


    async def _upd_stat(self, dataset_errors: int):
        y = dataset_errors
        for point in self.stat_points:
            self.graph_area.move_figure(point, -1, 0)
        self.stat_points.append(self.graph_area.draw_point((self.width, y)))


    async def start_training(self, datasetpath: str, n_count: int):
        dataset = self.dataset_decoder(datasetpath, n_count)
        self.net = ns.NeuronLayer(n_count, len(dataset[0][0]), random=True)
        self.trainer = ns.PerseptronTrainer(self.net, dataset, self._upd_stat)

        await asyncio.create_task(self.trainer.training(0.1))


    async def open(self):
        while True:  # Event Loop
            event, values = self.presentation_window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if event == '-START-':
                await asyncio.create_task(self.start_training(values["-FILE-"], 10))
            if event == '-STOP-':
                pass

        self.presentation_window.close()



pres_window = TrainWindow()
asyncio.run(pres_window.open())




