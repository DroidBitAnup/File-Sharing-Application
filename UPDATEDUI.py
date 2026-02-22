from tkinter import*
import tkinter as Tk
import socket

import threading
from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from zeroconf import Zeroconf, ServiceBrowser

import os,time


def Send():
    window=TkinterDnD.Tk()
    window.title("Send")
    window.geometry('470x500+500+200')
    window.configure(bg="#ab95b5")
    window.resizable(False,False)

    

     #variables
    file_var=StringVar(value="")
    IP_var=StringVar(value="")
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096
    senderName=""
    receiverName=""
    stored_file_list=[]
    port=5001
    global sendingAboart,Flag,progress_arc
    sendingAboart=False
    Flag=1
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    devices = {}   # name -> (ip, port)
    circles = {}   # canvas_id -> device_name
    device_progress_bars={}



    def sender():
        global filename
        try:
            hostname= IP_var.get().strip()
            #port=5001
            if not host or  not filename:
                messagebox.showerror("Error", "Please enter receiver ID, and select a file.",parent=window)
                return
            t = threading.Thread(target=send_file, args=(port, filename,hostname), daemon=True)
            t.start()
        except Exception as es:
                messagebox.showerror("Error",f"Due To:{str(es)}",parent=window)     
    

    class Listener:
        def add_service(window, zc, service_type, name):
            info = zc.get_service_info(service_type, name)

            print(info)

            if info:
                ip = ".".join(map(str, info.addresses[0]))
                devices[name] = (ip, info.port)
            else:
                devices.clear()
            draw_devices()  

    #Click on devive
    def on_click(event):
        global Flag,sendingAboart

        if circles:
            item = canvas.find_closest(event.x, event.y)[0]
        
        
            if item in circles:
                if Flag==1:
                    device = circles[item]
                    receiverName=device.split(".")[0]
                    print(device[0])
                    print(receiverName)
                    ip, port = devices[device]
                    t = threading.Thread(target=send_file, args=(5001,receiverName,device), daemon=True)
                    t.start()
                    Flag=0
                    #connect(ip, port)
                else:
                    sendingAboart=True
        else: messagebox.showwarning("Warning","Scan Device First.",parent=window)
                    #sock.close()




    def send_file( port,hostname,arcid):

        global Flag,sendingAboart
        sizetxt=""
        totalfilesize=0.0
        filesize=0
        sentsize=0.0    
        sent = 0
        start = time.time()
        last_time = start
        last_sent = 0
        percent=0
        
        

        for filepath in stored_file_list:
            filesize += os.path.getsize(filepath)
    

        
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

        totalSize_label.config(text=f"Total: {totalfilesize:.2f} {sizetxt}")     
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((hostname, port))
            sock.settimeout(None) 

            header = f"{filesize}{SEPARATOR}{senderName}{SEPARATOR}{len(stored_file_list)}".encode()
            sock.sendall(header) 
            header=None
            status_label.config(text=f"Connecting to {hostname}")
            time.sleep(5)

        #except Exception as e:
        #    sock.close()
        #    messagebox.showerror("Error", str(e),parent=window)


            for filepath in stored_file_list:
            #try:

                filename=None
                filesizeone = os.path.getsize(filepath)
                filename = os.path.basename(filepath)
                print(filename)
                header=None
                header = f"{filesizeone}{SEPARATOR}{filename}\n"
                sock.sendall(header.encode())
                header=None
    
        

    
                with open(filepath, "rb") as f:
                    status_label.config(text=f"Sending {filename}")
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        sock.sendall(bytes_read)
                        sent += len(bytes_read)
                        now = time.time()
                        if now - last_time >= 1:  # update every second
                            percent = (sent / filesize)
                            diff = sent - last_sent
                            speed = diff / (now - last_time) / (1024 * 1024)  # MB/s
                            eta = (filesize - sent) / (speed * 1024 * 1024) if speed > 0 else 0
                            
                            new_extent = -(percent * 359.999) # 360 can sometimes glitch to 0 in Tkinter
                            canvas.itemconfig(device_progress_bars[arcid], extent=new_extent)

                            last_time = now
                            last_sent = sent
                            # update progress bar

                            #sent size convertion
                            if sizetxt=="KB":
                                sentsize=sent/1024

                            elif sizetxt=="MB":
                                sentsize=sent/(1024*1024)    

                            elif sizetxt=="GB":
                                sentsize=sent/(1024*1024*1024)

                            if sendingAboart:
                                    
                                sock.close()    

                        
                            speed_label_Numeric.config(text=f"{speed:.2f} MB/s") 
                            ETA_label_Numeric.config(text=f"{eta/60:.2f} Minutes")   
                            sentSize_label.config(text=f"Sent: {sentsize:.2f} {sizetxt}")
                        window.update_idletasks()
    
            sock.close()
            status_label.config(text=f"Sent: {filename} ({filesize} bytes){receiverName}")
                
            speed_label_Numeric.config(text="") 
            ETA_label_Numeric.config(text="")
            sentSize_label.config(text=f"Total: {totalfilesize:.2f} {sizetxt}")
            Flag=1
            messagebox.showinfo("Success", f"File sent: {filename}",parent=window)
            
        except Exception as e:
            status_label.config(text="Error during send")
            sock.close()
            speed_label_Numeric.config(text="") 
            ETA_label_Numeric.config(text="")
            sentSize_label.config(text=f"Sent: {sentsize:.2f} {sizetxt}")
            Flag=1
    
            if sendingAboart: 
                sendingAboart=False
            else:    
                messagebox.showerror("Error", str(e),parent=window)
                print(e)
                sock.close()
        
                

                    


                




    #Functions
    def handle_drop(event):
        new_files = window.tk.splitlist(event.data)

        #for file in new_files:
        #    #if file not in self.stored_file_list: # Avoid duplicates
        #    stored_file_list.append(file)
        update_list(new_files)

    def manual_select():
        files = filedialog.askopenfilenames()
        if files:
            update_list(files)

    def update_list(files):
        selectedfileFrame.configure(state="normal")
        selectedfileFrame.delete("0.0", "end")
        if not files:
            selectedfileFrame.insert("end", "No files selected.")

        else:  
            index=1  
            for path in files:
                # Displays only the filename for a cleaner look
                filename = filename = path.split('/')[-1].split('\\')[-1].strip('{}')
                selectedfileFrame.insert("end", f"{index}.📄 {filename[:18]}...\n")
                index+=1
            for file in files:
                stored_file_list.append(file)

        selectedfileFrame.configure(state="disabled")

     

    def draw_devices():
        global progress_arc
        canvas.delete("all")
        circles.clear()
    
    
        radius = 25
        radius = 25
        start_x = 45
        y = 44
        gap = 80

        canvas.configure(scrollregion=(0, 0, start_x + gap * len(devices), 0))

        for i, name in enumerate(devices):
            cx = start_x + i * gap

            # Circle
            circle=canvas.create_oval(
                cx - radius, y - radius,
                cx + radius, y + radius,
                fill="#4CAF50", outline=""
            )
            circles[circle] = name

            # Device Name
            deviceText=canvas.create_text(
                cx+4, y+45,
                text=name.split(".")[0][:7],
                fill="white",
                font=("Segoe UI", 11, "bold")
            ) 

            # First letter INSIDE circle
            canvas.create_text(
                cx, y,
                text=name[0].upper(),
                fill="white",
                font=("Segoe UI", 14, "bold")
            )   
            #
            progress_arc = canvas.create_arc(
                            cx - radius, y - radius,
                            cx + radius, y + radius,
                            outline="#2196F3", width=4, 
                            style="arc", start=90, extent=0 )
            
            device_progress_bars[name]=progress_arc

            #canvas.tag_bind(circle, "<Button-1>",comman=onclick,lambda e, n=name: print("Clicked:", n))
            canvas.tag_bind(deviceText, "<Button-1>",lambda e,n=name: on_click)


    def scandevice():
        if stored_file_list:
            zeroconf = Zeroconf()
            ServiceBrowser(zeroconf, "_quickshare._tcp.local.", Listener())
        else:
            messagebox.showwarning("Warning","First Selct file(s)")


    #Icon
    image_icon=PhotoImage(file=r"Images\send.png")
    window.iconphoto(True,image_icon)

    #Device ID
    senderName=host=socket.gethostname()
    Label(window,text=f'{host}',bg='#ab95b5',font =('arial',25),fg='black').place(x=5,y=5)
    ctk.CTkLabel(window,text='Device ID',bg_color='#ab95b5',font =('arial',15),fg_color='#9882a1',corner_radius=25).place(x=5,y=52)

    #Selected Files
    #Label(window,text='Selected Files',bg='#9882a1',font =('arial',10),fg='black').place(x=5,y=52)
    selectedfileFrame=ctk.CTkTextbox(window,width=200,height=180,fg_color='#b3a4b9',corner_radius=15,text_color='#070707')
    selectedfileFrame.place(x=12,y=117)
    
    selectedfileFrame.insert("0.0", "List of selected files will appear here...","hhj")
    selectedfileFrame.configure(state="disabled")
    ctk.CTkLabel(window,text='Selected Files',width=200,bg_color='#ab95b5',font =('arial',14,"bold"),fg_color='#9882a1',corner_radius=25).place(x=10,y=85)

    #Status Label
    status_label = Label(window, text="Status: Idle",bg="#ab95b5")
    status_label.place(x=8,y=297)

    #Right Frame
    right_frame = ctk.CTkFrame(window,width=200,height=220, fg_color="#b3a4b9", corner_radius=15)
    right_frame.place(x=250,y=75)

    # Register Right Frame as Drop Target
    right_frame.drop_target_register(DND_FILES)
    right_frame.dnd_bind('<<Drop>>',handle_drop)

    #Select Button
    select_btn = ctk.CTkButton(right_frame,width=170,height=25,text="+ Select File",command=manual_select,corner_radius=15)
    select_btn.place(x=15,y=190)


    #Scan Button
    scanbtnframe=ctk.CTkFrame(window,width=30,height=30, fg_color="#ab95b5")
    scanbtnframe.place(x=310,y=440)
    scan_btn = ctk.CTkButton(scanbtnframe, text="🔍 Scan For Device", fg_color="#495255",corner_radius=15,command=scandevice)
    scan_btn.pack(side="left", padx=10)

    #NearbyDevices_label = ctk.CTkLabel(window, text="Nearby Devices",bg_color="transparent",text_color="black")
    #NearbyDevices_label.place(x=252,y=297)

    #Near By Device Canvas
    #nearByDeviceBG=PhotoImage(file=r"A:\Project\File Sharing\Images\ID.png")
    canvas = Tk.Canvas(window,width=430, height=100, bg="#ab95b5",xscrollcommand="True")
    canvas.place(x=15,y=322)
    canvas.bind("<Button-1>", on_click)

    

    # Interaction Elements
    inner_container = ctk.CTkFrame(right_frame, fg_color="transparent")
    inner_container.place(relx=0.5, rely=0.5, anchor="center")

    drop_icon = ctk.CTkLabel(inner_container, text="⏏", font=("Arial", 60))
    drop_icon.pack()

    drop_text = ctk.CTkLabel(inner_container, text="Drop files to send", font=("Arial", 16))
    drop_text.pack(pady=15)

    # Separator Line
    Frame(window,width=500,height=2,bg="#f3f5f6").place(x=0,y=470)

    #Sent Totalsize
    #slash=Label(window,text="/",font =('arial',15,'bold'),bg="#ab95b5")
    #slash.place(x=185,y=198)
    totalSize_label=Label(window,text="Total:55",font =('arial',11),bg="#ab95b5")
    totalSize_label.place(x=5,y=431)

    sentSize_label=Label(window,text="Sent:",font =('arial',11),bg="#ab95b5")
    sentSize_label.place(x=5,y=448)

    #Speed
    speed_label=Label(window, text="Speed: ",font =('arial',11),bg="#ab95b5")
    speed_label.place(x=2,y=475)
    speed_label_Numeric=Label(window, text="0 MB/s",font =('arial',11),bg="#ab95b5")
    speed_label_Numeric.place(x=51,y=475)

    #ETA
    ETA_label=Label(window, text="ETA: ",font =('arial',11,),bg="#ab95b5")
    ETA_label.place(x=345,y=475)
    ETA_label_Numeric=Label(window, text="--.-- Minutes",font =('arial',11),bg="#ab95b5")
    ETA_label_Numeric.place(x=380,y=475)
    

    
    
    window.mainloop()
if __name__== "__main__":
    Send()    