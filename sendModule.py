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
    senderName=""
    
    
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
            hostname= IP_var.get().strip()
            port=5001
            if not host or  not filename:
                messagebox.showerror("Error", "Please enter receiver ID, and select a file.",parent=window)
                return
            t = threading.Thread(target=send_file, args=(port, filename,hostname), daemon=True)
            t.start()
            Send_Btn.config(state="disabled")
        except Exception as es:
                messagebox.showerror("Error",f"Due To:{str(es)}",parent=window)     
    
    def send_file( port, filepath,hostname):
        sizetxt=""
        totalfilesize=0.0
        sentsize=0.0    
        sent = 0
        start = time.time()
        last_time = start
        last_sent = 0
        percent=0
        try:
            filesize = os.path.getsize(filepath)
            filename = os.path.basename(filepath)

            #Fillesize convertion
            if filesize>=(1024*1024) and filesize<(1024*1024*1024):
                totalfilesize=filesize/(1024*1024)
                sizetxt="MB"
            elif filesize>=(1024*1024*1024): 
                totalfilesize=filesize/(1024*1024*1024)
                sizetxt="GB"
            else:
                totalfilesize=filesize/(1024)
                sizetxt="KB"
    
            status_label.config(text=f"Connecting to {hostname}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((hostname, port))
            sock.settimeout(None)
    
            header = f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{senderName}".encode()
            sock.sendall(header)  # send header in one shot (small)
            # optional small delay could be used if receiver expects but not necessary
    
            sent = 0
            progress["maximum"] = filesize
            progress["value"] = 0
            

            time.sleep(5)
            slash.config(text="/")
            totalSize_label.config(text=f"{totalfilesize:.2f} {sizetxt}")
            status_label.config(text=f"Sending {filename}")

    
            with open(filepath, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    sock.sendall(bytes_read)
                    sent += len(bytes_read)
                    now = time.time()
                    if now - last_time >= 1:  # update every second
                        percent = (sent / filesize) * 100
                        diff = sent - last_sent
                        speed = diff / (now - last_time) / (1024 * 1024)  # MB/s
                        eta = (filesize - sent) / (speed * 1024 * 1024) if speed > 0 else 0

                        last_time = now
                        last_sent = sent
                        # update progress bar

                        #Recieved size convertion
                        if sizetxt=="KB":
                            sentsize=sent/1024

                        elif sizetxt=="MB":
                            sentsize=sent/(1024*1024)    

                        elif sizetxt=="GB":
                            sentsize=sent/(1024*1024*1024)

                        progress["value"] = sent
                        percentage_label.config(text=f"{percent:.2f}%")
                        speed_label_Numeric.config(text=f"{speed:.2f} MB/s") 
                        ETA_label_Numeric.config(text=f"{eta/60:.2f} Minutes")   
                        sentSize_label.config(text=f"{sentsize:.2f} {sizetxt}")
                    window.update_idletasks()
    
            sock.close()
            status_label.config(text=f"Sent: {filename} ({filesize} bytes){host}")
            progress["value"] = filesize
            percentage_label.config(text="100%")
            speed_label_Numeric.config(text="") 
            ETA_label_Numeric.config(text="")
            sentSize_label.config(text=f"{totalfilesize:.2f} {sizetxt}")
            messagebox.showinfo("Success", f"File sent: {filename}",parent=window)
            Send_Btn.config(state="normal")
        except Exception as e:
            Send_Btn.config(state="normal")
            status_label.config(text="Error during send")
            progress["value"] = sent
            percentage_label.config(text=f"{percent:.2f}%")
            speed_label_Numeric.config(text="") 
            ETA_label_Numeric.config(text="")
            sentSize_label.config(text=f"{sentsize:.2f} {sizetxt}")
            messagebox.showerror("Error", str(e),parent=window)    
    
    
    
    #Icon
    image_icon=PhotoImage(file=r"Images\send.png")
    window.iconphoto(True,image_icon)
    
    sendbackground=PhotoImage(file=r"Images/sender.png")
    sendback=Label(window,image=sendbackground,bg="#ab95b5")
    sendback.place(x=10,y=15)
    
    
    #Lower Frame
    mainbackground=PhotoImage(file=r"Images/id.png")
    back=Label(window,image=mainbackground,bg="#ab95b5")
    back.place(x=100,y=320)
    
    #Host
    senderName=host=socket.gethostname()
    Label(window,text=f'ID: {host}',bg='white',fg='black').place(x=140,y=350)
    
    #Selected File
    Label(window,text="Selected Files:",font =('arial',10),bg="#ab95b5",fg="#070b12").place(x=160,y=60)
    Label(window, textvariable=file_var, width=33, anchor="w", relief="sunken").place(x=160,y=90)
    
    #Enter Host ID
    Label(window,text="Enter Receiver ID:",font =('arial',10),bg="#ab95b5",fg="#070b12").place(x=160,y=5)
    Entry(window, textvariable=IP_var, width=33).place(x=160,y=30)

    #Percentage
    percentage_label=Label(window, text=" ",font =('arial',12),bg="#ab95b5")
    percentage_label.place(x=390,y=178)

    #Speed
    speed_label=Label(window, text="Speed",font =('arial',14,'bold'),bg="#ab95b5")
    speed_label.place(x=20,y=225)
    speed_label_Numeric=Label(window, text="",font =('arial',12),bg="#ab95b5")
    speed_label_Numeric.place(x=10,y=250)

    #ETA
    ETA_label=Label(window, text="ETA",font =('arial',14,'bold'),bg="#ab95b5")
    ETA_label.place(x=362,y=225)
    ETA_label_Numeric=Label(window, text="",font =('arial',12),bg="#ab95b5")
    ETA_label_Numeric.place(x=336,y=250)

    ##Filesize
    #Sent_label=Label(window, text="Sent",font =('arial',14,'bold'),bg="#ab95b5")
    #Sent_label.place(x=195,y=225)
    #Sent_numeric=Label(window, text="100 MB",font =('arial',11),bg="#ab95b5")
    #Sent_numeric.place(x=176,y=250)

    #Sent slash Totalsize
    slash=Label(window,text="",font =('arial',15,'bold'),bg="#ab95b5")
    slash.place(x=185,y=198)
    totalSize_label=Label(window,text="",font =('arial',11),bg="#ab95b5")
    totalSize_label.place(x=195,y=201)

    sentSize_label=Label(window,text="",font =('arial',11),bg="#ab95b5")
    sentSize_label.place(x=105,y=201)

    #progress Bar
    progress = Progressbar(window, length=375, mode="determinate")
    progress.place(x=12,y=178)

    # Separator Line
    Frame(window,width=500,height=2,bg="#f3f5f6").place(x=0,y=225)

    
    #Status Label
    status_label = Label(window, text="Status: Idle",bg="#ab95b5")
    status_label.place(x=15,y=290)
    
    
    #buttons
    Button(window,text="+ Select File",command=select_file,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000").place(x=160,y=130)
    Send_Btn=Button(window,text="Send",command=sender,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000")
    Send_Btn.place(x=300,y=130)
    
    
    window.mainloop()
if __name__== "__main__":
    Send()    