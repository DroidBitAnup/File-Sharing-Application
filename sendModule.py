from tkinter import*
import socket
import threading
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
import os,time

def Send():
    window=Tk()
    window.title("Send")
    window.geometry('450x560+500+200')
    window.configure(bg="#ab95b5")
    window.resizable(False,False)


    #variables
    file_var=StringVar(value="")
    IP_var=StringVar(value="")
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096
    
    
    #Functions

    def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?",parent=window):
                window.destroy()
                exit(0)

    window.protocol("WM_DELETE_WINDOW", on_closing)
    

    def select_file():
        global filename
        filename=filedialog.askopenfilename(parent=window)
        if filename:
            file_var.set(filename)
    
    
    def sender():
        global filename
        try:
            host=socket.gethostname()
            host= IP_var.get().strip()
            port=5001
            if not host or  not filename:
                messagebox.showerror("Error", "Please enter receiver IP, port and select a file.",parent=window)
                return
            t = threading.Thread(target=send_file, args=(host, port, filename), daemon=True)
            t.start()
            Send_Btn.config(state="disabled")
        except Exception as es:
                messagebox.showerror("Error",f"Due To:{str(es)}",parent=window)     
    
    def send_file(host, port, filepath):    
        try:
            filesize = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
    
            status_label.config(text=f"Connecting to {host}:{port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            sock.settimeout(None)
    
            header = f"{filename}{SEPARATOR}{filesize}".encode()
            sock.sendall(header)  # send header in one shot (small)
            # optional small delay could be used if receiver expects but not necessary
    
            sent = 0
            progress["maximum"] = filesize
            progress["value"] = 0
            time.sleep(5)
            status_label.config(text=f"Sending {filename} ({filesize} bytes)...")
    
            with open(filepath, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    sock.sendall(bytes_read)
                    sent += len(bytes_read)
                    # update progress bar
                    progress["value"] = sent
                    # force UI update
                    window.update_idletasks()
    
            sock.close()
            status_label.config(text=f"Sent: {filename} ({filesize} bytes)")
            messagebox.showinfo("Success", f"File sent: {filename}",parent=window)
            Send_Btn.config(state="normal")
            progress["value"] = 0
        except Exception as e:
            Send_Btn.config(state="normal")
            status_label.config(text="Error during send")
            messagebox.showerror("Error", str(e),parent=window)    
    
    
    
    #Icon
    image_icon=PhotoImage(file=r"Images\send.png")
    window.iconphoto(True,image_icon)
    
    sendbackground=PhotoImage(file=r"Images/sender.png")
    sendback=Label(window,image=sendbackground)
    sendback.place(x=10,y=15)
    
    Frame(window,width=500,height=2,bg="#f3f5f6").place(x=0,y=220)
    
    #Lower Frame
    mainbackground=PhotoImage(file=r"Images/id.png")
    back=Label(window,image=mainbackground,bg="#ab95b5")
    back.place(x=100,y=320)
    
    #Host
    host=socket.gethostname()
    Label(window,text=f'ID: {host}',bg='white',fg='black').place(x=140,y=350)
    
    #Selected File
    Label(window,text="Selected Files:",font =('arial',10),bg="#ab95b5",fg="#070b12").place(x=160,y=60)
    Label(window, textvariable=file_var, width=33, anchor="w", relief="sunken").place(x=160,y=90)
    
    #Enter IP
    Label(window,text="Enter Receiver IP:",font =('arial',10),bg="#ab95b5",fg="#070b12").place(x=160,y=5)
    Entry(window, textvariable=IP_var, width=33).place(x=160,y=30)
    
    #Status Label
    status_label = Label(window, text="Status: Idle",bg="#ab95b5")
    status_label.place(x=15,y=240)
    
    #progress Bar
    progress = Progressbar(window, length=420, mode="determinate")
    progress.place(x=12,y=185)
    
    #buttons
    Button(window,text="+ Select File",command=select_file,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000").place(x=160,y=130)
    Send_Btn=Button(window,text="Send",command=sender,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000")
    Send_Btn.place(x=300,y=130)
    
    
    window.mainloop()
if __name__== "__main__":
    Send()    