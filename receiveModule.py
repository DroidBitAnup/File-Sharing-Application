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
            ip = ListingIP_var.get().strip()
            running = True
            start.config(state="disabled")
            Close.config(state="normal")
            status_label.config(text=f"Starting server on {ip}:{port}...")
            accept_thread = threading.Thread(target=run_server, args=(ip, port), daemon=True)
            accept_thread.start()
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
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((ip, port))
                server_socket.listen(5)
                status_label.config(text=f"Listening on {ip}:{port}")
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
        try:
            status_label.config(text=f"Connection from {addr[0]}:{addr[1]}")
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
            filename, filesize_str = header.split(SEPARATOR)
            filesize = int(filesize_str)

            safe_filename = os.path.basename(filename)
            save_path = os.path.join(save_folder_var.get(), safe_filename)

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
            status_label.config(text=f"Receiving {safe_filename} ({filesize} bytes) ...")

            with open(save_path, "wb") as f:
                while received < filesize:
                    chunk = conn.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    progress["value"] = received
                    main.update_idletasks()

            conn.close()
            if received >= filesize:
                status_label.config(text=f"Received: {safe_filename} -> {save_path}")
                messagebox.showinfo("Received", f"Saved to: {save_path}",parent=main)
            else:
                status_label.config(text="Receive incomplete / connection closed")
                messagebox.showwarning("Warning", "File transfer incomplete.",parent=main)
            progress["value"] = 0
        except Exception as e:
            try:
                conn.close()
            except:
                pass
            status_label.config(text="Error receiving file")
            messagebox.showerror("Error", str(e),parent=main)    

    #Icon
    image_icon=PhotoImage(file=r"Images\receive.png")
    main.iconphoto(True,image_icon)

    #Icon
    image_icon=PhotoImage(file=r"Images\send.png")
    main.iconphoto(True,image_icon)

    sendbackground=PhotoImage(file=r"Images/sender.png")
    sendback=Label(main,image=sendbackground)
    sendback.place(x=10,y=15)

    # Separator Line
    Frame(main,width=500,height=2,bg="#f3f5f6").place(x=0,y=220)


    #Lower Frame
    mainbackground=PhotoImage(file=r"Images/id.png")
    back=Label(main,image=mainbackground,bg="#ab95b5")
    back.place(x=100,y=320)

    # Get host name
    ip_address=''
    try:
        host = socket.gethostname()
        ip_address = socket.gethostbyname(host)
        print(f"Your Local IP Address: {ip_address}")
    except socket.gaierror as e:
        print(e)
    
    Label(main,text=f'ID: {host}',fg='black').place(x=140,y=340)
    Label(main,text=f'IP: {ip_address}',fg='black').place(x=140,y=360)

    #browse_folder
    Label(main,text="Save Folder:",font =('arial',10),bg="#ab95b5",fg="#070b12").place(x=160,y=60)
    Label(main, textvariable=save_folder_var, width=33, anchor="w", relief="sunken").place(x=160,y=90)

    #Enter Listing IP
    Label(main,text="Enter Listing IP:",font =('arial',10),bg="#ab95b5",fg="#070b12").place(x=160,y=5)
    Entry(main, textvariable=ListingIP_var, width=33).place(x=160,y=30)

    #Status Label
    status_label = Label(main, text="Status: Stopped",bg="#ab95b5")
    status_label.place(x=15,y=240)

    #progress Bar
    progress = Progressbar(main, length=420, mode="determinate")
    progress.place(x=12,y=185)

    #buttons
    start=Button(main,text="Start",command=start_server_thread,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000")
    start.place(x=15,y=130)

    Close=Button(main,text="Close",command=stop_server,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000")
    Close.place(x=160,y=130)

    Browse=Button(main,text="Browse",command=browse_folder,width=10,height=1,font='arial 14 bold',bg="#fff",fg="#000")
    Browse.place(x=300,y=130)

    main.mainloop()

if __name__== "__main__":
    Receive()    