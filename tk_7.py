import tkinter as tk

colours = ['red','green','orange','white','yellow','blue']

r = 0
for c in colours:
    tk.Label(text=c, relief=tk.RIDGE).grid(row=r,column=0)
    tk.Entry(bg=c, relief=tk.SUNKEN).grid(row=r,column=1)
    tk.Label(text='Last time, {}'.format(c)).grid(row=r,column=2)
    r = r + 1

tk.mainloop()


# import tkinter as tk

# root = tk.Tk()
# w = tk.Label(root, text="Blue Sky", width=10, bg="blue", fg="white")
# w.pack(side=tk.RIGHT)
# w = tk.Label(root, text="Red Sun", width=10, bg="red", fg="white")
# w.pack(side=tk.RIGHT)
# w = tk.Label(root, text="Green Grass", width=10, bg="green", fg="black")
# w.pack(side=tk.RIGHT)


# tk.mainloop()