import socket
from os import walk,getcwd,makedirs,name,getlogin
from os.path import normcase,splitext,join,split,isdir,isfile
from pygame import mixer_music,mixer,error
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import  askyesno, showinfo 
from json import load,dump,loads,dumps
from threading import Thread
from mutagen.mp3 import MP3
from pyttsx3 import speak
class music_player():
    # def __init__(self):
    def run(self):
        login=getlogin()
        # self.DATA=(f"C:\\Users\\{login}\\AppData\\Roaming\\Music-Player\\Data")
        self.play_list=[]
        self.file_dir=[]
        self.file_name_dir={}
        self.udplay_list={}
        self.exited=False
        self.name=None
        self.playing=False
        self.paused=False
        self.audio_format=[".mp3",".MP3",".wav",".3gp",".aa",".aax",".avi",".ogg"]
        self.gui()
    def gui(self):
        self.root=Tk()
        self.speak_=BooleanVar()
        self.root.title("Music Player")
        if name=="nt":
            self.root.iconbitmap(normcase(join(getcwd(),"img\\tkicon.ico")))
        self.root.geometry("250x300")
        self.list_window=Frame(self.root)
        self.list_window.pack(side=TOP)
        self.title_label=Label(self.root)
        self.title_label.pack()
        self.progresslabel=Label(self.root)
        self.progresslabel.pack()
        self.button_window=Frame(self.root)
        self.button_window.pack(side=BOTTOM)
        self.list=Listbox(self.list_window,width=30)
        self.list.grid(row=0,column=0)
        self.gui_menu()
        self.gui_data_init()
        self.root.bind("<Control-O>",self.open_folder)
        self.root.bind("<Alt-leftarrow>",self.previous)
        self.root.bind("<Alt-rightarrow>",self.next)
        self.root.bind("<space>",self.play)
        self.list.bind("<Button-1>",self.play2)
        self.gui_button()
        if not self.last_played ==None:
            self.play(selected=self.last_played)
        self.root.mainloop()
        self.exited=True
        self.dump_data()
        try:
            mixer_music.stop()
        except error:
            pass
        showinfo("Exit??","Closing The Player")
    def gui_button(self):
        self.load_img()
        self.previous_button=Button(self.button_window,command=self.previous,image=self.image4)
        self.previous_button.grid(row=0,column=1)
        self.button=Button(self.button_window,command=self.play,image=self.image2)
        self.button.grid(row=0,column=2)
        self.volume_scale=Scale(self.button_window,orient='vertical',variable=self.volume,from_=100,to=0)
        self.volume_scale.grid(row=0,column=5)
        self.next_button=Button(self.button_window,command=self.next,image=self.image3)
        self.next_button.grid(row=0,column=3)
        self.check_button=Checkbutton(self.button_window,text="Say name",variable=self.speak_,onvalue=True,offvalue=False)
        self.check_button.deselect()
        self.check_button.grid(row=0,column=0)
        self.volume_scale.bind('<ButtonRelease>',self.set_volume)
        self.volume_scale.set(self.volume)

    def load_img(self):
        self.image4=PhotoImage(file=join(getcwd(),"img/previous.png"))
        self.image2=PhotoImage(file=join(getcwd(),"img/play.png"))
        self.image3=PhotoImage(file=join(getcwd(),"img/next.png"))
    def gui_data_init(self):
        self.get_data()
        if self.volume == None:
            self.volume=25
        if self.udplay_list==None or type(self.udplay_list) ==list:
            self.udplay_list={}
        def main_playlist():
            self.list.delete(0,END)
            self.get_data()
        self.list_menu.add_command(label="Main",command=main_playlist)
        for pllist in self.udplay_list:
            self.list_menu.add_command(label=pllist,command=lambda :self.play_play_list(pllist))

    def gui_menu(self):
        menu=Menu(self.root)
        File=Menu(menu)
        File.add_command(label="Add Folder ctrl+shift+o",command=self.open_folder)
        File.add_command(label="Close Floder",command=self.close_floder)
        playlist_menu=Menu(menu)
        playlist_menu.add_command(label="CreatePlaylist",command=self.creat_playlist)
        self.list_menu=Menu(menu)
        playlist_menu.add_cascade(label="PLay Playlist",menu=self.list_menu)
        menu.add_cascade(label="File",menu=File)
        menu.add_cascade(label="Playlist",menu=playlist_menu)
        self.root.config(menu=menu)


    def open_folder(self,event=None,a=None,list_=None):
        file_name_list=[]
        if list_==None:
            list=self.list
        else:
            list=list_
        if a==None:
            a=askdirectory(initialdir="/")
            if self.file_dir.__contains__(a):
                showinfo("Folder Exict",f"The selected Folder {a} has been alredy added")
                return None
            self.file_dir.append(a)
        for Directory_path,_,file_name in walk(a):
            file_name_list.append([Directory_path,file_name])
        for dir_n,file_list in file_name_list:
            for name in file_list:
                _,exe=splitext(name)
                if exe in self.audio_format:

                    list.insert(END,name)
                    self.file_name_dir[name]=normcase(dir_n)
                    self.play_list.append(name)
            list.select_anchor(len(self.play_list))

    def play(self,event=None,selected=None,repeat=False):

        if selected is None:
            index=self.list.curselection()
            try:
                name=self.play_list[index[0]]
            except Exception as e:
                return None
            file=join(self.file_name_dir[name],name)
            self.list.selection_set(index)
        else:
            file=selected
            _,name=split(file)
            index=self.play_list.index(name)
            self.list.see(index)
            self.list.selection_set(index)

        mixer.init()
        if self.playing:
            self.image=PhotoImage(file=join(getcwd(),"img/play.png"))
            self.button.config(image=self.image)
            mixer_music.pause()
            mixer_music.set_volume(self.volume)
            q=mixer_music.get_pos()
            self.paused=True
            self.playing=False

        else:
            if len(file)>4:
                self.image=PhotoImage(file=join(getcwd(),"img/pause.png"))
                self.button.config(image=self.image)
                try:
                    if not self.paused or self.name != name:
                        if self.speak_.get():
                            speak(f"Playing {name}")
                        try:
                            mixer_music.load(file)
                        except Exception as e:
                            mixer.init()
                            mixer_music.load(file)
                            return None
                        mixer_music.set_volume(self.volume)
                        mixer_music.play()
                        if self.first_played !=None:
                            mixer_music.set_pos(self.pos)
                            self.first_played=None
                        self.last_played=file
                        self.thread=Thread(target=self.check_end_position)
                        self.thread.start()
                        self.name=name
                        self.title_label["text"]=name
                    else:
                        mixer_music.unpause()
                        mixer_music.set_volume(self.volume)
                    self.playing=True
                except Exception as e:
                    Label(self.root,text=e).pack()
        if repeat:
            self.play()
    def get_data(self):
        try:
            self.client=socket.socket()
            self.client.connect(('localhost',1111))
            data=self.client.recv(1024).decode()
            self.json_data=loads(data)
            self.file_dir=self.json_data["path"]
            self.last_played=self.json_data["last_played"]
            self.first_played=self.last_played
            self.pos=self.json_data["pos"]
            self.volume=self.json_data["volume"]
            self.udplay_list=self.json_data["play_list"]
            for file in self.file_dir:
                self.open_folder(a=file)
        except ConnectionRefusedError:
            showinfo("Not Connecting","We cannot connect to the server \n I think the server is not running")
            exit(2)


    def set_volume(self,event):
        self.volume=self.volume_scale.get()
        mixer_music.set_volume(self.volume)
        self.volume_scale.bell()
    def dump_data(self):
        self.json_data["path"]=self.file_dir
        self.json_data["last_played"]=self.last_played
        self.json_data["pos"]=self.pos
        self.json_data["volume"]=self.volume
        self.json_data["play_list"]=self.udplay_list
        #             dump(self.json_data,f,indent=4,sort_keys=1)
        # send_data=load
        res_bytes = dumps(self.json_data).encode('utf-8')
        self.client.send(res_bytes)
    def next(self,event=None):

        self.a=self.list.curselection()
        self.list.select_clear(self.a[0])
        if self.a[0]+1==self.list.size():
            self.list.selection_set(0)
            self.list.see(self.a[0]+1)
        else:
            self.list.selection_set(self.a[0]+1)
            self.list.see(self.a[0]+1)
        self.play(repeat=True)
    def previous(self,event=None):
        self.a=self.list.curselection()
        self.list.select_clear(self.a[0])
        if self.a[0]==0:
            self.list.selection_set(self.list.size()-1)
            self.list.see(self.list.size()-1)
        else:
            self.list.selection_set(self.a[0]-1)
            self.list.see(self.a[0]-1)
        self.play(repeat=True)

    def check_end_position(self):
        audio=MP3(self.last_played)
        end=audio.info.length
        self.end_time=round(end/60,3)
        try:
            while not self.exited:
                self.pos=mixer_music.get_pos()
                end_time=round(round(round(self.pos/1000,2)//60,2)+round(round(self.pos/1000,2)%60,2)/100,3)
                if end_time==self.end_time or mixer_music.get_busy()==0:
                    self.next()
                elif type(end_time) == float or type(end_time) == int:
                    self.progresslabel["text"] = f"{end_time}/{self.end_time}"
            return True
        except :
            return False

    def close_floder(self):
        def remove_folder(value):
            self.file_dir.pop(self.radio_value.get())
            self.list.delete(0,END)
            for file in self.file_dir:
                self.open_folder(a=file)

            if not self.file_name_dir.__contains__(self.last_played):
                try:
                    mixer_music.stop()
                except :
                    pass
                self.last_played =None
            self.close_window.destroy()
        self.close_window=Toplevel()
        self.radio_value=IntVar()
        if name=="nt":
            self.close_window.iconbitmap(normcase(join(getcwd(),"img\\tkicon.ico")))
        for vlue,file in enumerate(self.file_dir):
            self.radio_button=Radiobutton(self.close_window,variable=self.radio_value,value=vlue,text=file)
            self.radio_button.pack(anchor=W)
        Button(self.close_window,text="Remove",command=lambda:remove_folder(self.radio_value.get())).pack()
        pass

    def play2(self,event=None):
        self.play()
        self.play()
    def creat_playlist(self):
        def add():
            a=self.play_list_list.curselection()
            play_name=self.play_list_name.get()
            if self.udplay_list.__contains__(play_name):
                a=askyesno("PLaylit",f"The Play list {play_name} Already exist ")
                if a:
                    self.udplay_list[play_name]=None
                else:
                    self.play_list_window.destroy()
                    return None
            udlist=[]
            for index in a:
                name=self.play_list[index]
                file=join(self.file_name_dir[name],name)
                udlist.append(file)

            self.udplay_list[play_name]=udlist
            self.list_menu.add_command(label=play_name,command=lambda :self.play_play_list(play_name))
            showinfo("Created Playlist",f"Successfully Created Playlist {play_name}")
            self.play_list_window.destroy()

        def continuee():
            self.play_list_list=Listbox(self.play_list_window,width=30,selectmode=MULTIPLE)
            self.play_list_list.pack()
            Label(self.play_list_window,text="Select the Songs to add to the playlist").pack()

            for file in self.file_dir:
                self.open_folder(a=file,list_=self.play_list_list)
            Button(self.play_list_window,text="Add to playlist",command=add).pack()

        self.play_list_window=Toplevel()
        if name=="nt":
            self.play_list_window.iconbitmap(normcase(join(getcwd(),"img\\tkicon.ico")))

        Label(self.play_list_window,text="Enter Playlist name").pack()
        self.play_list_name=Entry(self.play_list_window)
        self.play_list_name.pack()
        Button(self.play_list_window,text="Continue",command=continuee).pack()

    def play_play_list(self,key_):
        list_=self.udplay_list[key_]
        self.list.delete(0,END)
        del self.play_list
        del self.file_name_dir
        self.play_list=[]
        self.file_name_dir={}
        for name in list_:
            dir_name,bname=split(name)
            self.list.insert(END,bname)
            self.file_name_dir[bname]=normcase(dir_name)
            self.play_list.append(bname)


if __name__ == "__main__":
    music_player().run()
