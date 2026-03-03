print("Simple Calculator")
print("history - View calculation history")
print("clear - Clear calculation history")
print("exit - Exit the calculator")
        
history_file = "history.txt"

def add_to_history(user_input, result):
    with open(history_file, "a") as file:
        file.write(f"{user_input} = {result}\n")

def view_history():
    try:
        with open(history_file, "r") as file:
            history = file.read()
            print("Calculation History:")
            print(history)
    except FileNotFoundError:
        print("No history found.")

def clear_history():
    with open(history_file, "w") as file:
        file.write("")
    print("History cleared.")

def calculate(user_input):
    try:
        result = eval(user_input)
        add_to_history(user_input, result)
        return result
    except Exception as e:
        return f"Error: {e}"

def main():
    while True:
        

        user_input = input("Enter your expression : ")
        if user_input == "history":
            view_history()

        elif user_input == "clear":
            clear_history()

        elif user_input == "exit":
            print("Exiting the calculator. Goodbye!")
            break

        else:
            # perform calculation once, store result to avoid double history entry
            result = calculate(user_input)
            print(f"Result: {result}")

main()