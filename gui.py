from customtkinter import *
from utils import Solver

import threading

app = CTk()
app.title("Sudoku Puzzle Solver")

WIDTH = 1000
HEIGHT = 600

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

x = int((screen_width / 2) - (WIDTH / 2)) + 50
y = int((screen_height / 2) - (HEIGHT / 2)) -50

app.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

app.resizable(False,False)
app._set_appearance_mode("dark")

class Interface():
    def __init__(self, App):
        self.App = App

        self.canvas = CTkFrame(
            self.App, width=1000, height=600,
            fg_color='#EEF2F7', bg_color='#EEF2F7', corner_radius=0
        )

        self.Grid = CTkFrame(
            self.canvas, width=500, height=500,
            fg_color="#f2f2f2", corner_radius=0
        )
        self.controls = CTkFrame(
            self.canvas, width=500, height=100,
            fg_color="#676767", corner_radius=0
        )
        self.solveButton = CTkButton(
            self.controls, width=120, height=60,
            text='Solve', font=('Aerial', 18),
            hover_color='#f2f2f2', text_color='#000000',
            fg_color='#f2f2f2', corner_radius=0,
            command=self.solve
        )
        self.resetButton = CTkButton(
            self.controls, width=120, height=60,
            text='Clear', font=('Aerial', 18),
            hover_color='#f2f2f2', text_color='#000000',
            fg_color='#f2f2f2', corner_radius=0,
            command=self.resetGrid,
        )

        self.OutputFrame = CTkFrame(
            self.canvas, width=500, height=600,
            fg_color='#ffffff', corner_radius=0
        )

        self.gridValues = []
        self.outputValues = []

        self.cells = []
        self.outputCells = []
        
        self.gridFrame = CTkFrame(
            self.Grid,  width=500, height=500
        )
        self.gridOutputFrame = CTkFrame(
            self.OutputFrame,  width=500, height=500
        )

    def getGridValues(self):
        values = []
        for i in range(9):
            row = []
            for j in range(9):
                value = self.cells[i][j].get()

                if value == "":
                    value = " "

                row.append(value)
            values.append(row)
        self.gridValues = values 

    def solve(self):
        self.getGridValues()
        self.solveButton.configure(state="disabled")

        def worker():
            processedOutput = Solver.Solver(self.gridValues).controler()

            self.App.after(0, lambda: self.updateOutputgrid(processedOutput))
            self.App.after(0, lambda: self.solveButton.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def updateOutputgrid(self, outputValues):
        for i in range(9):
            for j in range(9):
                self.outputCells[i][j].configure(text=outputValues[i][j])

    def resetGrid(self):
        for row in self.cells:
            for cell in row:
                cell.delete(0, "end")

        for row in self.outputCells:
            for cell in row:
                cell.configure(text="")
        

    def max_one_char(self, new_text):
        return len(new_text) <= 1 and (new_text == "" or new_text.isdigit())
    
    def makeGrid(self):
        for i in range(9):
            self.gridFrame.grid_rowconfigure(i, weight=1)
            self.gridFrame.grid_columnconfigure(i, weight=1)

        validator = (self.App.register(self.max_one_char), '%P')
        
        for i in range(9):
            row = []
            for j in range(9):
                entry = CTkEntry(
                    self.gridFrame,
                    width=52,
                    height=52,
                    justify="center",
                    font=("Arial", 18),
                    text_color='#0000ff',
                    border_width=1,
                    border_color="#000000",
                    fg_color='#f2f2f2',
                    corner_radius=0,

                    validate="key",
                    validatecommand=validator
                )

                padx = (2, 0) if j in (3, 6) else (0, 0)
                pady = (2, 0) if i in (3, 6) else (0, 0)

                entry.grid(
                    row=i,
                    column=j,
                    sticky="nsew",
                    padx=padx,
                    pady=pady
                )

                row.append(entry)
            self.cells.append(row)

    def makeOutputGrid(self):
        for i in range(9):
            self.gridOutputFrame.grid_rowconfigure(i, weight=1)
            self.gridOutputFrame.grid_columnconfigure(i, weight=1)
            
        for i in range(9):
            row = []
            for j in range(9):
                entry = CTkLabel(
                    self.gridOutputFrame,
                    width=52,
                    height=52,
                    text= '',
                    font=("Arial", 18),
                    text_color="#009100",
                    border_width=1,
                    border_color="#000000",
                    fg_color='#f2f2f2',
                    corner_radius=0,
                )

                padx = (2, 0) if j in (3, 6) else (0, 0)
                pady = (2, 0) if i in (3, 6) else (0, 0)

                entry.grid(
                    row=i,
                    column=j,
                    sticky="nsew",
                    padx=padx,
                    pady=pady
                )

                row.append(entry)
            self.outputCells.append(row)

    def draw(self):
        self.canvas.place(x=0, y=0)

        self.Grid.place(x=0, y=0)

        self.gridFrame.place(x=12, y=12)
        self.makeGrid()

        self.controls.place(x=0, y=500)
        self.solveButton.place(x=75, y=25)
        self.resetButton.place(x=300, y=25)

        self.OutputFrame.place(x=500, y=0)

        self.gridOutputFrame.place(x=12, y=12)
        self.makeOutputGrid()





