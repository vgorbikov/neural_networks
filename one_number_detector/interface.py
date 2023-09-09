import PySimpleGUI as sg



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

        self.presentation_window.close()



class GenerateWindow():
    def __init__(self) -> None:
        self.grid = DrawGrid(500, 700, 5)

        #размещаем нужные элементы в окне
        self.presentation_layout = [
            [sg.Text('Нарисуйте цифру'), sg.Text(size=(12,1))],
            [self.grid.area],
            [sg.Button('Сохранить набор данных для цифры: ', key="-SAVE-"), 
             sg.Combo(['1', '2', '3', '4', '4', '6', '7', '8', '9', '0'], key="-DATASET_REFERENCE-")],
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

pres_window = GenerateWindow()
pres_window.open()




