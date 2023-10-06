import glob
import hashlib
import os
import tkinter as tk
from tkinter.filedialog import askdirectory


baselines = r"c:\Users\Nicholas\Documents\Coding\Cybersecurity\File-Integrity-Monitor (FIM)" #Path for Baseline.txt
secure_path = ""

files_changed = []
files_added = []
files_removed = []
files_all = []

spaces = "                                                                        \n"

# Calculate Hash from data in file
def CalculateSha512Hash(file_name):
    #BUFF_SIZE can change depending on your requirements
    BUFF_SIZE = 65536 # Reads in 64kb chunks
    sha = hashlib.sha512()

    with open(file_name, 'rb') as file:
        while True:
            data = file.read(BUFF_SIZE)
            if not data:
                break
            sha.update(data)
        return sha.hexdigest()

#Calculate hash from name of a file
def CalculateNameHash(filename):
    md5 = hashlib.md5()
    md5.update(filename.encode())
    return md5.hexdigest()

#Update Baseline
def UpdateBaseline(dir, mode):
    if dir=="":
        label3.configure(text="Error : Folder not selected")
    elif os.path.isdir(baselines) == False:
        label3.configure(text="Message : Baseline Folder doesn't exist, so creating one")
        os.makedirs(baselines)
        label3.configure(text="Message : Updating Baseline.....")
        UpdateBaselineHelper(dir, mode)
        label3.configure(text="Message : Updated Baseline Successfully")
    else:
        label3.configure(text="Message : Updating Baseline.....")
        UpdateBaselineHelper(dir, mode)
        label3.configure(text="Message : Updated Baseline Successfully")

#Update Baseline Helper for [files in a folder] and  [files in subfolders]
def UpdateBaselineHelper(dir, mode):
    global name_hash, baseline_path
    if(mode=='w'):
        name_hash = CalculateNameHash(dir)
        baseline_path = os.path.join(baselines,(name_hash+'.txt'))

    files = [os.path.abspath(f) for f in glob.glob(os.path.join(dir,'*')) if os.path.isfile(f)]
    with open(baseline_path, mode) as baseline:
        for f in files:
            hash = CalculateSha512Hash(os.path.join(dir,f))
            baseline.write(f)
            baseline.write('*')
            baseline.write(str(hash))
            baseline.write("\n")

    directories = [d for d in glob.glob(os.path.join(dir,'*')) if os.path.isdir(d)]
    for d in directories:
        UpdateBaselineHelper(d,'a')

#Returning dictionary containing keys as file name and values as their hashes
def getKeyHashesFromBaseline():
    global name_hash,baseline_path
    dict = {}

    with open(baseline_path, 'r') as baseline:
        for line in baseline:
            key,value = line.split('=')
            dict[key] = value[:-1]

    return dict

#Clear data in lists
def ClearData():
    files_changed.clear()
    files_added.clear()
    files_removed.clear()
    files_all.clear()

    fc.configure(text="Files Changed :"+spaces)
    fa.configure(text="Files Added :"+spaces)
    fr.configure(text="Files Removed :"+spaces)

#Calculate hashes and Checks with the baseline
def CheckIntegrity(dir, number):
    ClearData()

    if dir=="":
        label3.configure(text="Error : Folder not selected")
    else:
        CheckIntegrityHelper(dir,number)

        # print("Files Changed:",files_changed)
        # print("Files Added:",files_added)
        # print("Files Removed:",files_removed)
        
        fc.configure(text=fc.text+ '\n'.join(files_changed))
        fa.configure(text=fa.text+ '\n'.join(files_added))
        fr.configure(text=fr.text+ '\n'.join(files_removed))
        label3.configure(text="Message : Integrity Checked Successfully")

#Helper for Check Integrity
def CheckIntegrityHelper(dir, number):
    global name_hash,baseline_path

    if(number):
        name_hash = CalculateNameHash(dir)
        baseline_path = os.path.join(baselines,(name_hash+'.txt'))
        try:
            with open(baseline_path, 'r') as baseline:
                random=99
        except IOError:
            label3.configure(text='Error : Baseline file for specified folder not present')
            return
    
    files = [os.path.abspath(f) for f in glob.glob(os.path.join(dir,'*')) if os.path.isfile(f)]
    for x in files:
        files_all.append(x)
    dict = getKeyHashesFromBaseline()
    
    for f in files:
        #Checking for changed files
        temp_hash = CalculateSha512Hash(os.path.join(dir,f))
        if str(os.path.join(dir,f)) in dict.keys() and temp_hash!=dict[f]:
            files_changed.append(os.path.abspath(f).replace(os.path.abspath(folder),"."))
        
        #Checking for added files
        if str(os.path.join(dir,f)) not in dict.keys():
            files_added.append(os.path.abspath(f).replace(os.path.abspath(folder),"."))
    
    
    directories = [d for d in glob.glob(os.path.join(dir,'*')) if os.path.isdir(d)]
    for d in directories:
        CheckIntegrityHelper(d,0)
    
    if number==1:
        #checking for removed files
        for x in list(dict.keys()):
            if x not in files_all:
                files_removed.append(os.path.abspath(x).replace(os.path.abspath(folder),"."))


################################# GUI #################################

font_data = ("Raleway",14)
label_text_clr = "#FFCF00"
btn_fg_clr = "#27ab55"
btn_text_clr = "#000000"
btn_hover_clr = "#148f3f"
error_label_clr = "#E94F37"

folder=""

root = tk.Tk()
root.title(" File Integrity Monitor ")
root.geometry("650x700")

label1 = tk.Label(text="Select a Folder", fg=label_text_clr, font=font_data)
label1.place(relx=0.35, y=40,anchor=tk.CENTER)#absolute placing

def open_file():
    label3.configure(text="Message : ")
    label2.configure(text="(Selected Folder path will appear here)")
    global folder
    folder = askdirectory(parent=root, title="Choose a folder")
    if folder:
        label3.configure(text="Message : Folder Selected Successfully")
        label2.config(text=folder)
        ClearData()

browse_img = tk.PhotoImage(file = r"C:\Users\Nicholas\Documents\Coding\Cybersecurity\File-Integrity-Monitor (FIM)\images\browse.png")
browse_sample = browse_img.subsample(10,10)
browse_btn = tk.Button(master=root,
                        text="Browse",
                        image=browse_sample,
                        compound=tk.RIGHT,
                        command=open_file,
                        height=60,
                        width=125)
browse_btn.place(relx=0.7,y=40,anchor=tk.CENTER)

# Selected Folder Path
label2 = tk.Label(text="(Selected folder path will appear here)",
                    wraplength=500,
                    font=font_data,
                    fg=label_text_clr)
label2.place(relx=0.5, y=110,anchor=tk.CENTER)

baseline_img = tk.PhotoImage(file = r"C:\Users\Nicholas\Documents\Coding\Cybersecurity\File-Integrity-Monitor (FIM)\images\updatebaseline.png")
baseline_sample = baseline_img.subsample(18,18)
#Update Baseline
update_baseline_btn = tk.Button(text="Update Baseline",
                                image=baseline_sample,
                                compound=tk.RIGHT,
                                command=lambda:UpdateBaseline(folder,'w'),
                                fg=btn_text_clr,
                                font=font_data,
                                height=60,
                                width=200)
update_baseline_btn.place(relx=0.5, y=190,anchor=tk.CENTER)

check_integrity_img = tk.PhotoImage(file = r"C:\Users\Nicholas\Documents\Coding\Cybersecurity\File-Integrity-Monitor (FIM)\images\checkintegrity.png")
check_integrity_sample = check_integrity_img.subsample(9,9)
#Check Integrity Button
check_integrity_btn = tk.Button(text="Check Integrity",
                                image=check_integrity_sample,
                                compound=tk.RIGHT,
                                command=lambda:CheckIntegrity(folder,1),
                                fg=btn_text_clr,
                                font=font_data,
                                height=60,
                                width=200)
check_integrity_btn.place(relx=0.5, y=260,anchor=tk.CENTER)

#label3: Message Label
label3=tk.Label(text="Message: ",
                font=font_data,
                fg=error_label_clr)
label3.pack(fill="both",expand=True)
label3.place(relx=0.5, y=310,anchor=tk.CENTER)

#label4 : Changed Files
fc = tk.Label(text="Files Changed :"+spaces,
                       font=font_data,
                       fg=label_text_clr)
fc.pack(fill="both", expand=True)
fc.place(relx=0.5,y=370,anchor=tk.CENTER)

#label4 : Added Files
fa = tk.Label(text="Files Added : "+spaces,
                       font=font_data,
                       fg=label_text_clr)
fa.pack(fill="both", expand=True)
fa.place(relx=0.5,y=470,anchor=tk.CENTER)

#label4 : Removed Files 
fr = tk.Label(text="Files Removed : "+spaces,
                       font=font_data,
                       fg=label_text_clr)
fr.pack(fill="both", expand=True)
fr.place(relx=0.5,y=570,anchor=tk.CENTER)

root.mainloop()