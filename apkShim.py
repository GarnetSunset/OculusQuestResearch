def getInstalled():
	import subprocess
	stringOfPackages = subprocess.check_output(['adb', 'shell', 'pm', 'list', 'packages'])
	listOfPackages = stringOfPackages.decode().replace('package:', '').split('\r\n')
	listOfPackages = list(filter(None, listOfPackages))
	return listOfPackages
def chooseAPK(list):
	import tkinter
	root = tkinter.Tk()
	lbl = tkinter.Label(root,text = "Choose the Package")
	listbox = tkinter.Listbox(root, selectmode=tkinter.SINGLE)
	listbox.insert(tkinter.END, *list)
	listbox.pack(fill="both", expand=True)
	scrollbar = tkinter.Scrollbar(listbox, orient="vertical")
	scrollbar.config(command=listbox.yview)
	scrollbar.pack(side="right", fill="y")
	root.mainloop()
print(chooseAPK(getInstalled()))