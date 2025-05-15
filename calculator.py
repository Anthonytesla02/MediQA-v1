#!/usr/bin/env python3
"""
A simple command-line calculator application that performs basic arithmetic operations.
"""

def add(x, y):
    """Add two numbers and return the result."""
    return x + y

def subtract(x, y):
    """Subtract y from x and return the result."""
    return x - y

def multiply(x, y):
    """Multiply two numbers and return the result."""
    return x * y

def divide(x, y):
    """Divide x by y and return the result."""
    # Check for division by zero
    if y == 0:
        raise ValueError("Cannot divide by zero!")
    return x / y

def get_number_input(prompt):
    """Get and validate numerical input from the user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def get_operation_choice():
    """Display operation menu and get user choice."""
    print("\nChoose an operation:")
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. Exit calculator")
    
    while True:
        choice = input("Enter choice (1-5): ")
        if choice in {'1', '2', '3', '4', '5'}:
            return choice
        print("Invalid choice. Please enter a number between 1 and 5.")

def calculator():
    """Main calculator function that runs the application."""
    print("===== Simple Calculator =====")
    
    result = None
    first_calculation = True
    
    while True:
        # For the first calculation, get the first number from the user
        # For subsequent calculations, use the previous result as the first number
        if first_calculation:
            num1 = get_number_input("Enter first number: ")
            first_calculation = False
        else:
            print(f"\nCurrent result: {result}")
            use_result = input("Use this result for the next calculation? (y/n): ").lower()
            
            if use_result == 'y':
                num1 = result
                print(f"First number: {num1}")
            else:
                num1 = get_number_input("Enter first number: ")
                first_calculation = True
        
        # Get the operation choice from the user
        choice = get_operation_choice()
        
        # Exit if the user chooses option 5
        if choice == '5':
            print("Thank you for using the calculator. Goodbye!")
            break
        
        # Get the second number from the user
        num2 = get_number_input("Enter second number: ")
        
        # Perform the selected operation
        try:
            if choice == '1':
                result = add(num1, num2)
                operation = "+"
            elif choice == '2':
                result = subtract(num1, num2)
                operation = "-"
            elif choice == '3':
                result = multiply(num1, num2)
                operation = "*"
            elif choice == '4':
                result = divide(num1, num2)
                operation = "/"
            
            # Display the result
            print(f"\n{num1} {operation} {num2} = {result}")
            
        except ValueError as e:
            print(f"Error: {e}")
            first_calculation = True

def main():
    """Entry point of the calculator application."""
    try:
        calculator()
    except KeyboardInterrupt:
        print("\nCalculator terminated by user. Goodbye!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
