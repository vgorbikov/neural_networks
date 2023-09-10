import PySimpleGUI as sg
# import neural_structs as ns

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
        self.objects = []
        self.binary_set: list(int) = [0 for i in range(0, self.gwidth*self.gheight)]


    def draw_grid(self):
        #Сетка для разбиения на "пиксели"
        work_grid_vert = [self.area.draw_line((x, 0), (x, self.height), color='grey') for x in range(0, self.width, self.grid_step)]
        work_grid_hor = [self.area.draw_line((0, y), (self.width, y), color='grey') for y in range(0, self.height, self.grid_step)]


    def clear(self):
        for obj in self.objects:
            self.area.delete_figure(obj)
            self.binary_set = [0 for i in range(0, self.gwidth*self.gheight)]


    def draw(self, x, y):
        gx = (x//self.grid_step)
        gy = (y//self.grid_step)
        if self.binary_set[gy*self.gwidth + gx] != 0:
            return
        rx = gx*self.grid_step
        ry = gy*self.grid_step
        self.objects.append(self.area.draw_rectangle((rx, ry), (rx+self.grid_step, ry+self.grid_step), fill_color='black'))
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


    def update_answer(self, answer: int):
        self.presentation_window['-OUT-'].update('Это выглядит как: {}'.format(answer))


    def open(self):
        while True:  # Event Loop
            event, values = self.presentation_window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if event == '-INPUT-':
                # window['-OUT-'].update("Это выглядит как: ")
                self.grid.draw(*values['-INPUT-'])
            if event == 'Clear':
                self.grid.clear()
            if event == '-INPUT-+UP':
                self.update_answer(values['-INPUT-'][0])

        self.presentation_window.close()



class GenerateWindow():
    def __init__(self) -> None:
        self.grid = DrawGrid(500, 700, 5)

        #размещаем нужные элементы в окне
        self.presentation_layout = [
            [sg.Text('Нарисуйте цифру'), sg.Text(size=(12,1))],
            [self.grid.area],
            [sg.Button('Сохранить набор данных для цифры: ', key="-SAVE-"), 
             sg.Combo(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'], key="-DATASET_REFERENCE-")],
            [sg.Button('Clear'), sg.Button('Exit')]]
        self.presentation_window = sg.Window('Work Presentation', self.presentation_layout, finalize=True)

        #создаём сетку для рисования
        self.grid.draw_grid()


    def save_dataset(self, target: int, dataset: list[int]):
        zipdata = '|'.join([str(i) for i in dataset]) + '>{}\n'.format(target)
        with open("ond_dataset_{}rsl.txt".format(self.grid.h_resolution), "a") as f:
            f.writelines(zipdata)


    def open(self):
        while True:  # Event Loop
            event, values = self.presentation_window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if event == '-INPUT-':
                # window['-OUT-'].update("Это выглядит как: ")
                self.grid.draw(*values['-INPUT-'])
            if event == 'Clear':
                self.grid.clear()
            if event == '-SAVE-':
                self.save_dataset(values['-DATASET_REFERENCE-'], self.grid.binary_set)

        self.presentation_window.close()



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



# class TrainWindow():
#     def __init__(self) -> None:
#         self.width = 500
#         self.height = 300
#         self.stat = []
#         self.last_point = 0
#         self.graph_area: sg.Graph = sg.Graph(canvas_size=(self.width, self.height), 
#                      graph_bottom_left=(0, 0), 
#                      graph_top_right=(self.width, self.height), 
#                      background_color='white',
#                      key='-GRAPH-')

#         #размещаем нужные элементы в окне
#         self.presentation_layout = [
#             [sg.Text('Обучение')],
#             [sg.T('Выберите файл с данными для обучения:'), sg.FileBrowse(button_text="Выбрать", key='-FILE-')],
#             [sg.Text('Отклонение от тестового набора:')],
#             [self.graph_area],
#             [sg.Button('Начать обучение', key='-START-'), sg.Button('Остановить обучение', key='-STOP-'), sg.Button('Exit')]]
#         self.presentation_window = sg.Window('Work Presentation', self.presentation_layout, finalize=True)


#     def _upd_stat(self, d: int):
#         point = d
#         print(point)
#         step = 5
#         [self.graph_area.move_figure(s, -step, 0) for s in self.stat]
#         self.graph_area.draw_line((self.width-step, self.last_point), (self.width, point))
#         self.last_point = point


#     def open(self):
#         while True:  # Event Loop
#             event, values = self.presentation_window.read()
#             print(event, values)
#             if event == sg.WIN_CLOSED or event == 'Exit':
#                 break
#             if event == '-START-':
#                 dset = dataset_decoder(values['-FILE-'], 3)
#                 layer = nst.NeuronLayer(3, 35)
#                 t = nst.Trainer(layer, dataset_decoder('ond_dataset_5rsl.txt', 3))
#                 t.start_training(0.0001, self._upd_stat)
#             if event == '-STOP-':
#                 t.done = True

#         self.presentation_window.close()








pres_window = GenerateWindow()
pres_window.open()



