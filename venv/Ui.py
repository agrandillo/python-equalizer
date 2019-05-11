import tkinter as tk
from tkinter import ttk, filedialog
from Filter import Filter

class userInterface:
    def __init__(self):
        self.filter = Filter()
        self.root = tk.Tk()
        self.root.title = ("My Music Equalizer")
        self.mainframe = tk.Frame(self.root, padx=100, pady=50)
        self.mainframe.grid(column=0, row=0)
        self.play_or_pause = tk.StringVar()
        self.play_or_pause.set("Pause")

    def initiatePlayer(self):
        self.filter.read_file_data(self.root.filename)
        self.filter.start()

    def openFileExplorer(self) :
        self.root.filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("wav files","*.wav"),("all files","*.*")))
        self.initiatePlayer()

    def get_stream_state(self):
        if self.filter.is_stream_paused():
            return 'Play'
        return 'Pause'

    def on_play_pause(self):
        if(self.filter.is_stream_paused()):
            print("paused")
            self.filter.play_stream()
            self.play_or_pause.set("Pause")
        else:
            print("played")
            self.filter.pause_stream()
            self.play_or_pause.set("Play")

    def initiateUiControls(self):
        bassSlider = tk.Scale(self.mainframe, from_=1, to=0,
                              resolution=0.01, command=self.filter.set_low_coefficient, label='Bass',
                              width=30, length=200)
        bassSlider.grid(column=1, row=1)
        bassSlider.set(0.5)


        midSlider = tk.Scale(self.mainframe, from_=1, to=0,
                             resolution=0.01, command=self.filter.set_band_coefficient, label='Mid',
                             width=30, length=200)
        midSlider.grid(column=2, row=1)
        midSlider.set(0.5)

        highSlider = tk.Scale(self.mainframe, from_=1, to=0,
                              resolution=0.01, command=self.filter.set_high_coefficient, label='Trebble',
                              width=30, length=200)
        highSlider.grid(column=3, row=1)
        highSlider.set(0.5)

        upload_file_button = tk.Button(self.mainframe, text="Upload file", command=self.openFileExplorer)
        upload_file_button.grid(column=0, row=0)

        play_pause_button = tk.Button(self.mainframe, textvariable=self.play_or_pause, command=self.on_play_pause)
        play_pause_button.grid(column=0, row=1)

    def runUi(self):
        self.root.mainloop()

def main():
    ui = userInterface()
    ui.initiateUiControls()
    ui.runUi()

if __name__ == '__main__':
    main()


