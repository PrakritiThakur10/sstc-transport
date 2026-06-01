from tkinter import *

def run():
    root = Tk()
    root.geometry("400x200")
    root.title("Fibonacci Series Generator")

    def generate_fibonacci(n):
        series = [0, 1]
        while len(series) < n:
            series.append(series[-1] + series[-2])
        return series[:n]

    def show_fibonacci():
        try:
            num_terms = int(entry.get())
            if num_terms <= 0:
                raise ValueError
            series = generate_fibonacci(num_terms)
            result_label.config(text=f"Fibonacci Series: {series}")
        except ValueError:
            result_label.config(text="Please enter a positive integer.")

    entry_label = Label(root, text="Enter the number of terms:")
    entry_label.pack(pady=10)
    entry = Entry(root)
    entry.pack(pady=5)

    generate_button = Button(root, text="Generate", command=show_fibonacci)
    generate_button.pack(pady=10)

    result_label = Label(root, text="")
    result_label.pack(pady=10)

    root.deiconify()  
    root.attributes('-topmost', True)  
    root.mainloop()
