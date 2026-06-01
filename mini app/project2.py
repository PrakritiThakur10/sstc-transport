from tkinter import *
import random, string

def run():
    root = Tk()
    root.geometry("400x280")
    root.title("Password Generator")

    title = StringVar()
    Label(root, textvariable=title).pack()
    title.set("Select the strength of the password")

    choice = IntVar()

    def selection():
        selected_value = choice.get()
        labelchoice.config(text=f"Selected: {selected_value}")

    Radiobutton(root, text="Poor", variable=choice, value=1, command=selection).pack(anchor=CENTER)
    Radiobutton(root, text="Average", variable=choice, value=2, command=selection).pack(anchor=CENTER)
    Radiobutton(root, text="Advanced", variable=choice, value=3, command=selection).pack(anchor=CENTER)

    labelchoice = Label(root)
    labelchoice.pack()

    lenlabel = StringVar()
    lenlabel.set("Password Length:")
    Label(root, textvariable=lenlabel).pack()

    val = IntVar()
    Spinbox(root, from_=8, to_=24, textvariable=val, width=13).pack()

    def passgen():
        poor = string.ascii_uppercase + string.ascii_lowercase
        average = poor + string.digits
        symbols = "`~!@#$%^&()_-+={}[]?|:;?"
        advanced = poor + average + symbols

        if choice.get() == 1:
            return "".join(random.sample(poor, val.get()))
        elif choice.get() == 2:
            return "".join(random.sample(average, val.get()))
        elif choice.get() == 3:
            return "".join(random.sample(advanced, val.get()))
        else:
            return "Select an option"

    def callback():
        password = passgen()
        isum.config(text=f"Your password is: {password}")

    Button(root, text="Generate Password", bd=5, height=2, command=callback, pady=3).pack()

    isum = Label(root, text="")
    isum.pack(side=BOTTOM)

    root.mainloop()

if __name__ == "__main__":
    run()
