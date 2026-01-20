from fileinput import filename
import subprocess
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as tksc
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename
import platform
import threading

def do_command(command):

    global command_textbox, url_entry, lines_seen, current_count
    # reset count so new command is seen as new output
    lines_seen = 0
    current_count = 0

    # quick UI update on main thread, then run the blocking subprocess in a background thread
    command_textbox.delete(1.0, tk.END)
    command_textbox.insert(tk.END, command + " working....\n")
    command_textbox.update()
    try:
        notify_new_lines()
    except NameError:
        pass

    url_val = url_entry.get()
    if (len(url_val) == 0):
        url_val = "127.0.0.1"
    final_command = ""
    if platform.system() == "Linux" or platform.system() == "Darwin":
        if command == "ping":
            final_command = command + " " + url_val + " -c 4" 
            
        if command == "tracert":
            command = "traceroute"
            final_command = command + " " + url_val
            
        if command == "nmap":
            final_command = command + " " + url_val
            
    elif platform.system() == "Windows":
        if command == "ping":
            final_command = command + " " + url_val + " -n 4"
        if command == "tracert":
            final_command = command + " " + url_val
        if command == "nmap":
            final_command = command + " " + url_val

    def _reader():
        with subprocess.Popen(final_command, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                # schedule insertion on the main thread
                def _insert(l=line):
                    command_textbox.insert(tk.END, l)
                    command_textbox.update()
                    try:
                        notify_new_lines()
                    except NameError:
                        pass
                command_textbox.after(0, _insert)

    threading.Thread(target=_reader, daemon=True).start()
    


root = tk.Tk()
frame = tk.Frame(root)
frame.pack()


# set up button to run the do_command function
'''ping_btn = tk.Button(frame, text="ping", command=lambda: do_command("ping"))
ping_btn.pack()'''

# creates the frame with label for the text box
frame_URL = tk.Frame(root, pady=10,  bg="black") # change frame color
frame_URL.pack(side=tk.TOP)

# decorative label
url_label = tk.Label(frame_URL, text="Enter a URL of interest: ", 
    #command=lambda:do_command("ping"),
    compound="center",
    font=("comic sans", 14),
    bd=0, 
    relief=tk.FLAT, 
    cursor="heart",
    fg="mediumpurple3",
    bg="black")
url_label.pack(side=tk.LEFT)
url_entry= tk.Entry(frame_URL,  font=("comic sans", 14)) # change font
url_entry.pack(side=tk.LEFT)

frame = tk.Frame(root,  bg="black") # change frame color
frame.pack()

'''ping_btn = tk.Button(frame, text="Check to see if a URL is up and active", 
    command=lambda:do_command("ping"),
    compound="center",
    font=("comic sans", 12),
    bd=0, 
    relief="flat",
    cursor="dotbox",
    bg="light blue", activebackground="gray")
ping_btn.pack() 

trace_btn = tk.Button(frame, text="Tracert the URL", 
    command=lambda:do_command("tracert"),
    compound="center",
    font=("comic sans", 12),
    bd=0, 
    relief="flat",
    cursor="dotbox",
    bg="light green", activebackground="gray")
trace_btn.pack() 

nmap_btn = tk.Button(frame, text="Nmap the URL (if nmap is installed)", 
    command=lambda:do_command("nmap"),
    compound="center",
    font=("comic sans", 12),
    bd=0, 
    relief="flat",
    cursor="dotbox",
    bg="yellow", activebackground="gray")
nmap_btn.pack()'''


#listbox list and making listbox
listbox_list = ["ping", "tracert", "nmap"]
choice_var = tk.StringVar(value=listbox_list)
list_btns = tk.Listbox(frame, height=5, listvariable=choice_var)

choice_var.set(listbox_list)

def invokeAction(selection):
    if len(selection) == 0:
        return
    selected_command = listbox_list[selection[0]]
    do_command(selected_command)
    
#list_btns.bind("<Double-1>", lambda e: invokeAction(list_btns.curselection())) #Double click to do action

list_btns.pack(side=tk.TOP)

do_btn = tk.Button(frame, text="Do Selected Command", command=lambda: invokeAction(list_btns.curselection()))
do_btn.pack()

pbar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=200, mode='indeterminate')

pbar.pack()



# Adds an output box to GUI.
command_textbox = tksc.ScrolledText(frame, height=20, width=100)
command_textbox.pack(side=tk.BOTTOM)

# Progressbar control: start on new lines, stop after a timeout
isStart = True  #
if isStart:
    lines_seen = len(command_textbox.get("1.0", tk.END).splitlines())  # Fix the evil (when it starts with the GUI)
    isStart = False
else:
    lines_seen = 0
_stop_after_id = None #The timer's ID when stopping
_stop_delay = 2000 # milliseconds

def _stop_progress():
    global _stop_after_id
    current_count = 0
    pbar.stop()


def _schedule_stop():
    global _stop_after_id
    if _stop_after_id is not None:
        command_textbox.after_cancel(_stop_after_id)
    _stop_after_id = command_textbox.after(_stop_delay, _stop_progress)

def notify_new_lines():
    #Makes the prgress bar start when stuff is added and stop when the command oupttu stops
    
    global lines_seen
    current_count = len(command_textbox.get("1.0", tk.END).splitlines())
    if current_count > lines_seen:
        lines_seen = current_count
        command_textbox.see(tk.END)
        pbar.start(10)
        _schedule_stop()

# Poll occasionally for external changes
def _poll_for_lines():
    current_count = len(command_textbox.get("1.0", tk.END).splitlines())
    if current_count > lines_seen:
        notify_new_lines()
    command_textbox.after(200, _poll_for_lines) #.afters are for scheduling delays 

# start polling
command_textbox.after(200, _poll_for_lines)

def mSave():
    filename = asksaveasfilename(defaultextension='.txt',filetypes = (('Text files', '*.txt'),('Python files', '*.py *.pyw'),('All files', '*.*')))
    if filename is None:
        return
    file = open (filename, mode = 'w')
    text_to_save = command_textbox.get("1.0", tk.END)

    file.write(text_to_save)
    file.close()

save_button = tk.Button(frame, text="Save Output", command=mSave)
save_button.pack(side=tk.LEFT)

root.mainloop()
