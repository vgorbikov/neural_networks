import PySimpleGUI as sg



sg.theme('Dark Blue 3')

#задаёт разрешение сетки
horizontal_resolution = 10    
#фактические размеры рабочей области      
area_width = 500
area_height = 700
grid_step = round(area_width/horizontal_resolution)


#адаптер к холсту
class DrawGrid():
    def __init__(self, width, height, grid_step, gui_obj) -> None:
        self.width: int = width
        self.height: int = height
        self.grid_step: int = grid_step
        self.gwidth = self.width//self.grid_step
        self.gheight = self.height//self.grid_step
        self.area: sg.Graph = gui_obj
        self.objects = []
        self.binary_set: list(int) = [0 for i in range(0, self.gwidth*self.gheight)]


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
        self.objects.append(work_area.draw_rectangle((rx, ry), (rx+self.grid_step, ry+self.grid_step), fill_color='black'))
        self.binary_set[gy*self.gwidth + gx] = 1



#холст
work_area = sg.Graph(canvas_size=(area_width, area_height), 
                     graph_bottom_left=(0, area_height), 
                     graph_top_right=(area_width, 0), 
                     background_color='white',
                     key='-INPUT-',
                     enable_events=True,
                     drag_submits=True)

#создаём адаптер к холсту
grid = DrawGrid(area_width, area_height, grid_step, work_area)

#размещаем нужные элементы в окне
layout = [[sg.Text('Нарисуйте цифру'), sg.Text(size=(12,1))],
          [work_area],
          [sg.Text('Это выглядит как: ', key='-OUT-')],
          [sg.Button('Clear'), sg.Button('Exit')]]

window = sg.Window('Work Presentation', layout, finalize=True)

#Сетка для разбиения на "пиксели"
work_grid_vert = [work_area.draw_line((x, 0), (x, area_height), color='grey') for x in range(0, area_width, grid_step)]
work_grid_hor = [work_area.draw_line((0, y), (area_width, y), color='grey') for y in range(0, area_height, grid_step)]


while True:  # Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == '-INPUT-':
        # window['-OUT-'].update("Это выглядит как: ")
        grid.draw(*values['-INPUT-'])
        print(grid.binary_set)
    if event == 'Clear':
        grid.clear()
        

window.close()