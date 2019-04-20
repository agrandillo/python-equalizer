import tkinter as tk
from tkinter import ttk, filedialog
from Filter import Filter


filter = Filter('Distrion.wav')
root = tk.Tk()
root.title("My Music Tuner")
#root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))

mainframe = tk.Frame(root, padx=100, pady=50, )
mainframe.grid(column=0, row=0)

bassSlider = tk.Scale(mainframe, from_=1, to=0,
                      resolution=0.01, command=filter.set_low_coefficient, label='Bass',
                      width=30, length=200)
bassSlider.grid(column=0, row=1)
bassSlider.set(0.5)


midSlider = tk.Scale(mainframe, from_=1, to=0,
                     resolution=0.01, command=filter.set_band_coefficient, label='Mid',
                     width=30, length=200)
midSlider.grid(column=1, row=1)
midSlider.set(0.5)

highSlider = tk.Scale(mainframe, from_=1, to=0,
                      resolution=0.01, command=filter.set_high_coefficient, label='Trebble',
                      width=30, length=200)
highSlider.grid(column=2, row=1)
highSlider.set(0.5)


filter.start()
root.mainloop()
filter.set_stream_activity(False)




