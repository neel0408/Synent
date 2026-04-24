import random

while True:
    number = random.randint(1, 100)
    attempts = 0

    print("\nNew Game Started!")

    while True:
        guess = int(input("Enter your guess (1-100): "))
        attempts += 1

        if guess > number:
            print("Too High!")
        elif guess < number:
            print("Too Low!")
        else:
            print("🎉 Correct Guess!")
            print("Attempts:", attempts)
            break

    choice = input("Play again? (yes/no): ")
    if choice.lower() != "yes":
        print("Game Over!")
        break