from tkinter import*
import socket
import threading
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
import os,time

server_socket = None
running =False
accept_thread = None

def Receive():
    #main=Toplevel(root)
    main=Tk()
    main.title("Receive")
    main.geometry('450x560+500+200')
    main.configure(bg="#ab95b5")
    main.resizable(False,False)


    #Variable
    save_folder_var=StringVar(value=os.getcwd())
    ListingIP_var=StringVar(value="0.0.0.0")


    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096


    def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?",parent=main):
                main.destroy()
                exit(0)

    main.protocol("WM_DELETE_WINDOW", on_closing)

    def browse_folder():
        path = filedialog.askdirectory(parent=main)
        if path:
            save_folder_var.set(path)


    def start_server_thread():
        global running
        try:
            if running:
                return
            port = 5001
            ip = "0.0.0.0"
            running = True
            start.config(state="disabled")
            Close.config(state="normal")
            accept_thread = threading.Thread(target=run_server, args=(ip, port), daemon=True)
            accept_thread.start()
            
            status_label.config(text="Ready to receive...")
        except Exception as es:
            messagebox.showerror("Error",f"Due To:{str(es)}",parent=main)

    def stop_server():
        global running
        running = False
        if server_socket:
            try:
                server_socket.close()
            except:
                pass
        start.config(state="normal")
        Close.config(state="disabled")
        status_label.config(text="Status: Stopped")
        progress["value"] = 0



    def run_server( ip, port):
            global running
            progress["value"] =0
            percentage_label.config(text="")
            speed_label_Numeric.config(text="")
            ETA_label_Numeric.config(text="") 
            slash.config(text="")
            ReceivedSize_label.config(text="")
            totalSize_label.config(text="")
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((ip, port))
                server_socket.listen(5)
                time.sleep(2)
                status_label.config(text="Waiting for sender...")
            except Exception as e:
                status_label.config(text="Failed to start server")
                messagebox.showerror("Error", str(e),parent=main)
                running = False
                start.config(state="normal")
                Close.config(state="disabled")
                return

            while running:
                global conn
                try:
                    server_socket.settimeout(1.0)
                    conn, addr = server_socket.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                t.start()

            # cleanup on exit
            try:
                server_socket.close()
            except:
                pass

    def handle_client( conn, addr):
        sizetxt=""
        totalfilesize=0.0
        receivedsize=0.0
        try:
            #status_label.config(text=f"Connection from {addr[0]}")
            # receive header (filename and filesize)
            header_bytes = conn.recv(BUFFER_SIZE)
            if not header_bytes:
                conn.close()
                return
            header = header_bytes.decode(errors="ignore")
            if SEPARATOR not in header:
                # malformed header
                conn.close()
                return
            filename, filesize_str,sender= header.split(SEPARATOR)
            filesize = int(filesize_str)
            status_label.config(text=f"Connection from {sender}")

            safe_filename = os.path.basename(filename)
            save_path = os.path.join(save_folder_var.get(), safe_filename)

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



            # if file exists, create a new name
            base, ext = os.path.splitext(save_path)
            counter = 1
            while os.path.exists(save_path):
                save_path = f"{base}({counter}){ext}"
                counter += 1

            progress["maximum"] = filesize
            progress["value"] = 0
            received = 0
            time.sleep(5)
            slash.config(text="/")
            totalSize_label.config(text=f"{totalfilesize:.2f} {sizetxt}")
            status_label.config(text=f"Receiving {safe_filename}")

            with open(save_path, "wb") as f:
                
                start = time.time()
                last_time = start
                last_recv = 0
                percent=0
                speed=0
                eta=0
                while received < filesize:
                    chunk = conn.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    progress["value"] = received

                    #Recieved size convertion
                    if sizetxt=="KB":
                        receivedsize=received/1024

                    elif sizetxt=="MB":
                        receivedsize=received/(1024*1024)    

                    elif sizetxt=="GB":
                        receivedsize=received/(1024*1024*1024)


                    now = time.time()
                    if now - last_time >= 1:
                        percent = (received / filesize) * 100
                        diff = received - last_recv
                        speed = diff / (now - last_time) / (1024 * 1024)
                        eta = (filesize - received) / (speed * 1024 * 1024) if speed > 0 else 0

                        last_time = now
                        last_recv = received
                        percentage_label.config(text=f"{percent:.2f}%")
                        speed_label_Numeric.config(text=f"{speed:.2f} MB/s") 
                        ETA_label_Numeric.config(text=f"{eta/60:.2f} Minutes") 
                        ReceivedSize_label.config(text=f"{receivedsize:.2f} {sizetxt}")
                    main.update_idletasks()

                    

            conn.close()
            if received >= filesize:
                status_label.config(text=f"Received: {safe_filename} -> {save_path}")
                progress["value"] = filesize
                percentage_label.config(text="100%")
                speed_label_Numeric.config(text="")
                ETA_label_Numeric.config(text="")
                messagebox.showinfo("Received", f"Saved to: {save_path}",parent=main)
            else:
                status_label.config(text="Receive incomplete / connection closed")
                percentage_label.config(text=f"{percent:.2f}%")
                speed_label_Numeric.config(text="")
                ETA_label_Numeric.config(text="")
                progress["value"] = received
                messagebox.showwarning("Warning", "File transfer incomplete.",parent=main)
        except Exception as e:
            try:
                conn.close()
            except:
                pass
            status_label.config(text="Error receiving file")
            progress["value"] = received
            percentage_label.config(text=f"{percent:.2f}%")
            speed_label_Numeric.config(text="")
            ETA_label_Numeric.config(text="")  
            messagebox.showerror("Error", str(e),parent=main)    

    #Icon
    image_icon=PhotoImage(file=r"Images\receive.png")
    main.iconphoto(True,image_icon)

    ##Icon
    #image_icon=PhotoImage(file=r"Images\send.png")
    #main.iconphoto(True,image_icon)

    sendbackground=PhotoImage(file=r"Images/sender.png")
    sendback=Label(main,image=sendbackground,bg="#ab95b5")
    sendback.place(x=10,y=15)

    # Separator Line
    Frame(main,width=500,height=2,bg="#f3f5f6").place(x=0,y=225)


    #singnal and ID
    signalID=PhotoImage(file=r"Images/id.png")
    back=Label(main,image=signalID,bg="#ab95b5")
    back.place(x=100,y=325)

    # Get host name
    host = socket.gethostname()
    
    Label(main,text=f'ID: {host}',fg='black',bg="white").place(x=140,y=350)

    #browse_folder
    Label(main,text="Save File Location:",font =('arial',13),bg="#ab95b5",fg="#070b12").place(x=160,y=50)
    Label(main, textvariable=save_folder_var, width=33, anchor="w", relief="sunken").place(x=160,y=80)


    #Status Label
    status_label = Label(main, text="Status: Stopped",bg="#ab95b5")
    status_label.place(x=15,y=290)

    

    #Percentage
    percentage_label=Label(main, text="",font =('arial',12),bg="#ab95b5")
    percentage_label.place(x=390,y=178)

    #Speed
    speed_label=Label(main, text="Speed",font =('arial',14,'bold'),bg="#ab95b5")
    speed_label.place(x=20,y=225)
    speed_label_Numeric=Label(main, text="",font =('arial',12),bg="#ab95b5")
    speed_label_Numeric.place(x=10,y=250)

    #ETA
    ETA_label=Label(main, text="ETA",font =('arial',14,'bold'),bg="#ab95b5")
    ETA_label.place(x=362,y=225)
    ETA_label_Numeric=Label(main, text="",font =('arial',12),bg="#ab95b5")
    ETA_label_Numeric.place(x=336,y=250)

    ##Filesize
    #Filesize_label=Label(main, text="Filesize",font =('arial',14,'bold'),bg="#ab95b5")
    #Filesize_label.place(x=195,y=225)
    #Filesize_numeric=Label(main, text="100 MB",font =('arial',11),bg="#ab95b5")
    #Filesize_numeric.place(x=176,y=250)

    #Received slash Totalsize
    slash=Label(main,text="",font =('arial',15,'bold'),bg="#ab95b5")
    slash.place(x=185,y=198)
    totalSize_label=Label(main,text="",font =('arial',11),bg="#ab95b5")
    totalSize_label.place(x=195,y=201)

    ReceivedSize_label=Label(main,text="",font =('arial',11),bg="#ab95b5")
    ReceivedSize_label.place(x=105,y=201)

    #progress Bar
    progress = Progressbar(main, length=375, mode="determinate")
    progress.place(x=12,y=178)

    # Separator Line
    Frame(main,width=500,height=2,bg="#f3f5f6").place(x=0,y=225)

    #buttons
    start=Button(main,text="Receive",command=start_server_thread,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000")
    start.place(x=15,y=130)

    Close=Button(main,text="Close",command=stop_server,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000")
    Close.place(x=160,y=130)

    Browse=Button(main,text="Browse",command=browse_folder,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000")
    Browse.place(x=300,y=130)

    main.mainloop()

if __name__== "__main__":
    Receive()    