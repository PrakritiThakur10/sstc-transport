from tkinter import *
import random

def run():
    root = Tk()
    root.geometry("400x400")
    root.title("Rock Paper Scissor Game")

    computer_value = {
        "0": "Rock",
        "1": "Paper",
        "2": "Scissor"
    }

    def reset_after_result():
        root.after(5000, reset_game)

    def reset_game():
        b1["state"] = "active"
        b2["state"] = "active"
        b3["state"] = "active"
        l1.config(text="Player")
        l3.config(text="Computer")
        l4.config(text="")
        l4.config(bg="white")

    def button_disable():
        b1["state"] = "disable"
        b2["state"] = "disable"
        b3["state"] = "disable"

    def isrock():
        c_v = computer_value[str(random.randint(0, 2))]
        if c_v == "Rock":
            match_result = "Draw"
        elif c_v == "Scissor":
            match_result = "Player Wins"
        else:
            match_result = "Computer Wins"
        l4.config(text=match_result, bg="#C1FFC1" if match_result == "Player Wins" else "#FFA07A")
        l1.config(text="Rock")
        l3.config(text=c_v)
        button_disable()
        reset_after_result()

    def ispaper():
        c_v = computer_value[str(random.randint(0, 2))]
        if c_v == "Paper":
            match_result = "Draw"
        elif c_v == "Scissor":
            match_result = "Computer Wins"
        else:
            match_result = "Player Wins"
        l4.config(text=match_result, bg="#C1FFC1" if match_result == "Player Wins" else "#FFA07A")
        l1.config(text="Paper")
        l3.config(text=c_v)
        button_disable()
        reset_after_result()

    def isscissor():
        c_v = computer_value[str(random.randint(0, 2))]
        if c_v == "Rock":
            match_result = "Computer Wins"
        elif c_v == "Scissor":
            match_result = "Draw"
        else:
            match_result = "Player Wins"
        l4.config(text=match_result, bg="#C1FFC1" if match_result == "Player Wins" else "#FFA07A")
        l1.config(text="Scissor")
        l3.config(text=c_v)
        button_disable()
        reset_after_result()

    Label(root, text="Rock Paper Scissor", font="Helvetica 20 bold", fg="dark blue").pack(pady=30)

    frame = Frame(root)
    frame.pack(pady=10)

    l1 = Label(frame, text="Player", font="Helvetica 15", padx=10)
    l2 = Label(frame, text="VS", font="Helvetica 12 bold", padx=10)
    l3 = Label(frame, text="Computer", font="Helvetica 15", padx=10)

    l1.pack(side=LEFT)
    l2.pack(side=LEFT)
    l3.pack(side=LEFT)

    l4 = Label(root, text="", font="Helvetica 18 bold", bg="white", width=20, borderwidth=3, relief="solid")
    l4.pack(pady=30)

    frame1 = Frame(root)
    frame1.pack(pady=10)

    b1 = Button(frame1, text="Rock", font="Helvetica 12", width=10, bg="#FFD700", fg="black", command=isrock)
    b2 = Button(frame1, text="Paper", font="Helvetica 12", width=10, bg="#4682B4", fg="white", command=ispaper)
    b3 = Button(frame1, text="Scissor", font="Helvetica 12", width=10, bg="#DC143C", fg="white", command=isscissor)

    b1.pack(side=LEFT, padx=10)
    b2.pack(side=LEFT, padx=10)
    b3.pack(side=LEFT, padx=10)

    root.mainloop()
