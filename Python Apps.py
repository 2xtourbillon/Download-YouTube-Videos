from pytube import YouTube
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
import re
import threading

class Application:
    """Builds the main frame in tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.grid_rowconfigure(0, weight=2)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.config(bg='#ffdddd')
        
        top_label = Label(self.root, text='YouTube Download Manager', fg='orange', font=('Type Xero', 70))
        top_label.grid(pady=(0, 10))

        link_label = Label(self.root, text='Please Paste Any YouTube Video Link Below:', font=('Calibri', 30))
        link_label.grid(pady=(0, 20))

        self.youtubeEntryVar = StringVar()

        self.youtubeEntry = Entry(self.root, width=70, textvariable=self.youtubeEntryVar, font=('Agency Fb', 25), fg='red')
        self.youtubeEntry.grid(pady=(0, 15), ipady=2, padx=100)

        self.youtubeEntryError = Label(self.root, text='', font=('Concert One', 20))
        self.youtubeEntryError.grid(pady=(0, 8))

        self.youtubeFileSaveLabel = Label(self.root, text='Choose Directory', font=('Concert One', 15))
        self.youtubeFileSaveLabel.grid()

        self.youtubeFileDirectoryButton = Button(self.root, text='Directory', font=('Bell MT', 15), command=self.openDirectory)
        self.youtubeFileDirectoryButton.grid(pady=(10,3))

        self.fileLocationLabel = Label(self.root, text='', font=('Freestyle Script', 25))
        self.fileLocationLabel.grid()

        self.youtubeChooselabel = Label(self.root, text='Choose the Download Type', font=('Variety', 30))
        self.youtubeChooselabel.grid()

        #create list
        self.downloadChoices = [("Audio MP3", 1), ("Video MP4", 2)]

        self.ChoicesVar = StringVar()
        self.ChoicesVar.set(1) #default to MP3

        # create radio buttons
        for text, mode in self.downloadChoices:
            self.youtubeChoices = Radiobutton(self.root, text=text, font=("Nothwest old", 15), variable=self.ChoicesVar, value=mode)
            self.youtubeChoices.grid()

        self.downloadButton = Button(self.root, text='Download', width=10, font=('Bell MT', 15), command=self.checkyoutubelink)
        self.downloadButton.grid(pady=(30, 5))

    def checkyoutubelink(self):
        """Checks the YouTube link provided by user
        
        Returns:
            downloadWindow() if checks are successfull, otherwise Labels directing the user for input
        """
        # self.matchyoutubelink = re.match("^https://www.youtube.com/.", self.youtubeEntryVar)
        self.matchyoutubelink = str(self.youtubeEntryVar)
        if (not self.matchyoutubelink):
            self.youtubeEntryError.config(text='Invalid YouTube Link', fg='Red')
        elif (not self.openDirectory):
            self.fileLocationLabel.config(text='Please Choose a Directory', fg='red')
        elif (self.matchyoutubelink and self.openDirectory):
            self.downloadWindow()

    def downloadWindow(self):
        """Launches the download Window: SecondApp()"""
        
        self.newWindow = Toplevel(self.root) #create new window on top of root
        self.root.withdraw() #root dissappears
        self.newWindow.state('zoomed')
        self.newWindow.grid_rowconfigure(0, weight=0)
        self.newWindow.grid_columnconfigure(0, weight=1)

        self.app = SecondApp(self.newWindow, self.youtubeEntryVar.get(), self.FolderName, self.ChoicesVar.get())

    def openDirectory(self):
        """Allows users to open a directory dialog
        
        Returns:
            True if folder name is chosen, else Label with directions
        """
        self.FolderName = filedialog.askdirectory()

        if (len(self.FolderName) > 0):
            self.fileLocationLabel.config(text=self.FolderName, fg='green')
            return True
        else:
            self.fileLocationLabel.config(text='Please Choose a Directory', fg='red')

class SecondApp:
    """Launches the Progress window and download thread
    
    Args:
        downloadWindow (obj): new window that was launched
        youtubelink (str): user's youtube link
        FolderName (str): folder where app will download content
        Choices (str): chooses to download audio(MP3) or audio+video (MP4)
    
    Attributes:
        downloadWindow (obj): new window that was launched
        youtubelink (str): user's youtube link
        FolderName (str): folder where app will download content
        Choices (str): chooses to download audio(MP3) or audio+video (MP4)
    
    Todo:
        * Fix the self.video_type.filesize line; it is not returning anything but pytube docs 
            state it should be returning file size. Currently unable to download audio (MP4)

    """
    
    def __init__(self, downloadWindow, youtubelink, FolderName, Choices):
        self.downloadWindow = downloadWindow
        self.youtubelink = youtubelink
        self.FolderName = FolderName
        self.Choices = Choices

        self.yt = YouTube(self.youtubelink)

        # choose download option based on chosen mode
        if (self.Choices == '1'):
            #storing audio in self.video_type
            self.video_type = self.yt.streams.filter(only_audio=True)
            self.MaxFileSize = self.video_type.filesize
        if (self.Choices == '2'):
            self.video_type = self.yt.streams.first() #return the first video format available
            self.MaxFileSize = self.video_type.filesize

        self.loadingLabel = Label(self.downloadWindow, text='Downloading in Progress!...', font=('Small Fonts', 40))
        self.loadingLabel.grid(pady=(100, 0))

        self.loadingPercent = Label(self.downloadWindow, text='0', fg='green', font=('Agency Fb', 40))
        self.loadingPercent.grid(pady=(50, 0))

        self.progressbar = ttk.Progressbar(self.downloadWindow, length=500, orient='horizontal', mode='indeterminate')
        self.progressbar.grid(pady=(50, 0))
        self.progressbar.start()

        threading.Thread(target=self.yt.register_on_progress_callback(self.show_progress)).start()
        threading.Thread(target=self.downloadFile).start()

    def downloadFile(self):
        """Downloading the file"""

        if (self.Choices == '1'):
            self.yt.streams.filter(only_audio=True).first().download(self.FolderName)

        if (self.Choices == '2'):
            self.yt.streams.first().download(self.FolderName)

    def show_progress(self, streams=None, Chunks=None, filehandle=None, bytes_remaining=None):
        """Showing the progress bar and evaluating status and MB size"""
        
        self.percentCount = float('%0.2f' (100-(100*(bytes_remaining/self.MaxFileSize))))

        if (self.percentCount < 100):
            self.loadingPercent.config(text=self.percentCount)
        else:
            self.progressbar.stop()
            self.loadingLabel.grid_forget()
            self.progressbar.grid_forget()

            self.downloadFinished = Label(self.downloadWindow, text='Download Finished', font=('Arial', 30))
            self.downloadFinished.grid(pady=(150, 0))

            self.downloadedFileName = Label(self.downloadWindow, text=self.yt.title, font=('Terminal', 30))
            self.downloadedFileName.grid(pady=(50, 0))

            MB = float('%0.2f'% (self.MaxFileSize/1000000))

            self.downloadFileSize = Label(self.downloadWindow, text=str(MB), font=('Agency FP', 15))
            self.downloadFileSize.grid(pady=(50,0))

if __name__ == '__main__':

    window = Tk()
    window.title('YouTube Download Manager')
    window.state('zoomed') #window to appear full screen

    app = Application(window)

    mainloop()