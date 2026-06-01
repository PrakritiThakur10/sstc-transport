import project1
import project2
import project3
import project4

def main():
    while True:
        print("Choose which file to run:")
        print("1. CALCULATOR")
        print("2. PASSWORD GENERATOR")
        print("3. FIBONACCI SERIES GENERATOR")
        print("4. ROCK PAPER SCISSOR")
        print("5. Exit")

        choice = input("Enter the number (1-5): ")

        if choice == "1":
            project1.run()
        elif choice == "2":
            project2.run()
        elif choice == "3":
            project3.run()
        elif choice == "4":
            project4.run()
        elif choice == "5":
            break
        else:
            print("Invalid input. Please choose a number between 1 and 5.")

if __name__ == "__main__":
    main()
