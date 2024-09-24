import tkinter as tk
from tkinter import simpledialog
import math

# Configurações de tela
WIDTH, HEIGHT = 800, 800


# Funções de desenho e transformação
def draw_pixel(canvas, x, y, color="red"):
    canvas.create_line(x, y, x + 1, y, fill=color)
    
    
def draw_line(canvas, x1, y1, x2, y2, color="red"):
    canvas.create_line(x1, y1, x2, y2, fill=color)
    
# Função para desenhar polígonos com base nos pontos clicados
def draw_polygon_from_points(canvas, points, color="red"):
    if len(points) > 1:
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            draw_line_dda(canvas, x1, y1, x2, y2, color)
        # Conectar o último ponto ao primeiro para fechar o polígono
        draw_line_dda(canvas, points[-1][0], points[-1][1], points[0][0], points[0][1], color)

# Algoritmo DDA para desenhar linhas
def draw_line_dda(canvas, x1, y1, x2, y2, color="red"):
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x1, y1
    for _ in range(steps):
        draw_pixel(canvas, round(x), round(y), color)
        x += x_inc
        y += y_inc
        
def draw_circle(canvas, xc, yc, r, color="red"):
    canvas.create_oval(xc - r, yc - r, xc + r, yc + r, outline=color)

def translate(shape, dx, dy):
    if shape["type"] == "line" or shape["type"] == "polygon":
        shape["points"] = [(x + dx, y - dy) for x, y in shape["points"]]
    elif shape["type"] == "circle":
        shape["center"] = (shape["center"][0] + dx, shape["center"][1] - dy)

def scale(shape, factor):
    if shape["type"] == "line":
        x1, y1 = shape["points"][0]
        x2, y2 = shape["points"][1]
        xc = (x1 + x2) / 2
        yc = (y1 + y2) / 2
        shape["points"] = [
            (int((x1 - xc) * factor + xc), int((y1 - yc) * factor + yc)),
            (int((x2 - xc) * factor + xc), int((y2 - yc) * factor + yc))
        ]
    elif shape["type"] == "circle":
        shape["radius"] = int(shape["radius"] * factor)

def rotate(shape, angle):
    if shape["type"] == "line" or shape["type"] == "polygon":
        points = shape["points"]
        xc = sum([p[0] for p in points]) / len(points)  # Centro médio dos pontos
        yc = sum([p[1] for p in points]) / len(points)
        theta = math.radians(angle)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        def rotate_point(x, y):
            x_new = cos_theta * (x - xc) - sin_theta * (y - yc) + xc
            y_new = sin_theta * (x - xc) + cos_theta * (y - yc) + yc
            return int(x_new), int(y_new)

        shape["points"] = [rotate_point(x, y) for x, y in points]

# Função de reflexão ajustada para usar as dimensões da tela
def reflect(shape, axis):
    if shape["type"] == "line" or shape["type"] == "polygon":
        def reflect_point(point, axis):
            if axis == 'x':
                return (point[0], HEIGHT - point[1])
            elif axis == 'y':
                return (WIDTH - point[0], point[1])
            elif axis == 'xy':
                return (WIDTH - point[0], HEIGHT - point[1])

        shape["points"] = [reflect_point(p, axis) for p in shape["points"]]

    elif shape["type"] == "circle":
        def reflect_point(point, axis):
            if axis == 'x':
                return (point[0], HEIGHT - point[1])
            elif axis == 'y':
                return (WIDTH - point[0], point[1])
            elif axis == 'xy':
                return (WIDTH - point[0], HEIGHT - point[1])

        shape["center"] = reflect_point(shape["center"], axis)

def redraw_shapes(canvas, shapes):
    canvas.delete("all")  # Limpa o canvas antes de redesenhar
    for shape in shapes:
        if shape["type"] == "line":
            draw_line(canvas, shape["points"][0][0], shape["points"][0][1],
                      shape["points"][1][0], shape["points"][1][1], "red")
        elif shape["type"] == "circle":
            draw_circle(canvas, shape["center"][0], shape["center"][1], shape["radius"], "red")
        elif shape["type"] == "polygon":
            draw_polygon_from_points(canvas, shape["points"], "red")
            # Desenha linhas conectando os pontos do polígono
            
def cohen_sutherland_clip(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    def _region_code(x, y):
        code = 0
        if x < x_min:  # esq
            code |= 1
        if x > x_max:  # dir
            code |= 2
        if y < y_min:  # baixo
            code |= 4
        if y > y_max:  # cima
            code |= 8
        return code

    accept = False
    done = False

    while not done:
        c1 = _region_code(x1, y1)
        c2 = _region_code(x2, y2)

        if c1 == 0 and c2 == 0:  # linha completamente dentro da área
            accept = True
            done = True
        elif c1 & c2 != 0:  # linha completamente fora
            done = True
        else:  # linha parcialmente dentro
            code_out = c1 if c1 != 0 else c2

            if code_out & 1:
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min
            elif code_out & 2:
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif code_out & 4:
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif code_out & 8:
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max

            if code_out == c1:
                x1, y1 = x, y
            else:
                x2, y2 = x, y

    if accept:
        return x1, y1, x2, y2
    else:
        return None

# Função de interface gráfica usando tkinter
def create_tkinter_interface():
    root = tk.Tk()
    root.title("Interface de Transformações Geométricas")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
    canvas.pack()

    shapes = []  # Lista para armazenar as formas desenhadas
    points = []
    drawing_line = False
    drawing_algorithm = None
    drawing_circle = False
    drawing_polygon = False
    drawing_clipping_area = False
    clipping_points = []
    clipping_area = None
    
    def apply_clipping():
        """ Aplica o recorte em todas as linhas da lista shapes com base na área de recorte """
        if clipping_area is None:
            return

        x_min, y_min, x_max, y_max = clipping_area
        clipped_shapes = []
        
        for shape in shapes:
            if shape["type"] == "line":
                x1, y1 = shape["points"][0]
                x2, y2 = shape["points"][1]
                clipped_line = cohen_sutherland_clip(x1, y1, x2, y2, x_min, y_min, x_max, y_max)
                if clipped_line:
                    x1_new, y1_new, x2_new, y2_new = clipped_line
                    points_new = [(x1_new, y1_new), (x2_new, y2_new)]
                    clipped_shapes.append({
                        "type": "line",
                        "points": points_new.copy()
                    })
        
        # Atualiza a lista de formas apenas com as formas recortadas
        shapes.clear()
        shapes.extend(clipped_shapes)
        redraw_shapes(canvas, shapes)

    
    def apply_translation():
        dx = simpledialog.askfloat("Input", "Digite o valor de dx:")
        dy = simpledialog.askfloat("Input", "Digite o valor de dy:")
        for shape in shapes:
            translate(shape, dx, dy)
        redraw_shapes(canvas, shapes)

    def apply_scaling():
        factor = simpledialog.askfloat("Input", "Digite o fator de escala:")
        for shape in shapes:
            scale(shape, factor)
        redraw_shapes(canvas, shapes)

    def apply_rotation():
        angle = simpledialog.askfloat("Input", "Digite o ângulo de rotação (em graus):")
        for shape in shapes:
            rotate(shape, angle)
        redraw_shapes(canvas, shapes)

    def apply_reflection(axis):
        for shape in shapes:
            reflect(shape, axis)
        redraw_shapes(canvas, shapes)

    def start_drawing_line(algorithm):
        nonlocal drawing_line, points, drawing_algorithm
        drawing_line = True
        points = []
        drawing_algorithm = algorithm
        
        
    def start_drawing_clipping_area():
        nonlocal drawing_clipping_area, clipping_points
        drawing_clipping_area = True
        clipping_points = []

    def finish_clipping_area():
        nonlocal drawing_clipping_area, clipping_points, clipping_area

        if len(clipping_points) == 2:
            x1, y1 = clipping_points[0]
            x2, y2 = clipping_points[1]
            clipping_area = (x1, y1, x2, y2)  # Define a área de recorte
            canvas.create_rectangle(x1, y1, x2, y2, outline="blue", dash=(5, 2))
            drawing_clipping_area = False
            clipping_points = []
            
            
    def start_drawing_circle():
        nonlocal drawing_circle, points
        drawing_circle = True
        points = []

    def start_drawing_polygon():
        nonlocal drawing_polygon, points
        drawing_polygon = True
        points = []
    
    def clear_all():
        shapes.clear()
        canvas.delete("all")  # Limpa o canvas antes de redesenhar
        
        
    def finish_polygon():
        nonlocal drawing_polygon, points

        if drawing_polygon and len(points) > 2:
            # Desenha o polígono conectando o último ponto ao primeiro
            draw_polygon_from_points(canvas, points)
            
            # Adiciona o último segmento de reta que conecta o último ponto ao primeiro
            shapes.append({"type": "polygon", "points": points.copy()})
            
            drawing_polygon = False
            points = []

                
                
    def on_canvas_click(event):
        nonlocal drawing_line, drawing_circle, drawing_polygon, points, drawing_clipping_area, clipping_points, clipping_area

        if drawing_clipping_area:
            if len(clipping_points) == 0:
                clipping_points.append((event.x, event.y))
            elif len(clipping_points) == 1:
                clipping_points.append((event.x, event.y))
                finish_clipping_area()
                
        elif drawing_line:
            if len(points) == 0:
                points.append((event.x, event.y))
            elif len(points) == 1:
                points.append((event.x, event.y))
                shapes.append({"type": "line", "points": points.copy()})
                redraw_shapes(canvas, shapes)
                points = []
                drawing_line = False

        elif drawing_circle:
            if len(points) == 0:
                points.append((event.x, event.y))
            elif len(points) == 1:
                radius = distance(points[0][0], points[0][1], event.x, event.y)
                shapes.append({"type": "circle", "center": points[0], "radius": radius})
                redraw_shapes(canvas, shapes)
                points = []
                drawing_circle = False

        elif drawing_polygon:
            points.append((event.x, event.y))
            if len(points) > 1:
                # Desenha uma linha entre o último ponto e o penúltimo ponto clicado
                draw_line(canvas, points[-2][0], points[-2][1], points[-1][0], points[-1][1])
            
          
    def distance(x1, y1, x2, y2):
        return int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    # Botões para adicionar ações
    translate_button = tk.Button(root, text="Transladar", command=apply_translation)
    translate_button.pack(side=tk.LEFT, padx=10, pady=10)

    scale_button = tk.Button(root, text="Escalar", command=apply_scaling)
    scale_button.pack(side=tk.LEFT, padx=10, pady=10)

    rotate_button = tk.Button(root, text="Rotacionar", command=apply_rotation)
    rotate_button.pack(side=tk.LEFT, padx=10, pady=10)

    reflect_x_button = tk.Button(root, text="Refletir X", command=lambda: apply_reflection('x'))
    reflect_x_button.pack(side=tk.LEFT, padx=10, pady=10)

    reflect_y_button = tk.Button(root, text="Refletir Y", command=lambda: apply_reflection('y'))
    reflect_y_button.pack(side=tk.LEFT, padx=10, pady=10)

    reflect_xy_button = tk.Button(root, text="Refletir XY", command=lambda: apply_reflection('xy'))
    reflect_xy_button.pack(side=tk.LEFT, padx=10, pady=10)

    line_dda_button = tk.Button(root, text="Reta DDA", command=lambda: start_drawing_line("dda"))
    line_dda_button.pack(side=tk.LEFT, padx=10, pady=10)

    line_bresenham_button = tk.Button(root, text="Reta Bresenham", command=lambda: start_drawing_line("bresenham"))
    line_bresenham_button.pack(side=tk.LEFT, padx=10, pady=10)

    circle_bresenham_button = tk.Button(root, text="Circunferência Bresenham", command=start_drawing_circle)
    circle_bresenham_button.pack(side=tk.LEFT, padx=10, pady=10)

    polygon_button = tk.Button(root, text="Desenhar Polígono", command=start_drawing_polygon)
    polygon_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    finish_polygon_button = tk.Button(root, text="Finalizar Polígono", command=finish_polygon)
    finish_polygon_button.pack(side=tk.LEFT, padx=10, pady=10)
    
      # Botões para adicionar ações
    clipping_button = tk.Button(root, text="Selecionar Área de Recorte", command=start_drawing_clipping_area)
    clipping_button.pack(side=tk.LEFT, padx=10, pady=10)
    # Botão para aplicar o recorte
    clipping_apply_button = tk.Button(root, text="Aplicar Recorte", command=apply_clipping)
    clipping_apply_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    clear_button = tk.Button(root, text="Limpar", command=clear_all)
    clear_button.pack(side=tk.LEFT, padx=10, pady=10)

    canvas.bind("<Button-1>", on_canvas_click)

    root.mainloop()

if __name__ == "__main__":
    create_tkinter_interface()