import gui

def main():
    app = gui.app

    root = gui.Interface(app)
    root.draw()

    app.mainloop()
if  __name__ == '__main__':
    main()