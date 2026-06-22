def save_log(text):
    with open("logs.txt", "a") as file:
        file.write(text + "\n")