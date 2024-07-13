from celery_app import add, subtract, multiply, divide

def main():
    # Example usage of tasks
    result_add = add.delay(4, 4)
    result_subtract = subtract.delay(10, 3)
    result_multiply = multiply.delay(6, 7)
    result_divide = divide.delay(8, 2)
    result_divide_by_zero = divide.delay(8, 0)

    print(f"Addition Task ID: {result_add.id}")
    print(f"Addition Result: {result_add.get(timeout=10)}")

    print(f"Subtraction Task ID: {result_subtract.id}")
    print(f"Subtraction Result: {result_subtract.get(timeout=10)}")

    print(f"Multiplication Task ID: {result_multiply.id}")
    print(f"Multiplication Result: {result_multiply.get(timeout=10)}")

    print(f"Division Task ID: {result_divide.id}")
    print(f"Division Result: {result_divide.get(timeout=10)}")

    print(f"Division by Zero Task ID: {result_divide_by_zero.id}")
    print(f"Division by Zero Result: {result_divide_by_zero.get(timeout=10)}")

if __name__ == "__main__":
    main()