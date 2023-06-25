import customtkinter as ctk
import tkinter as tk
import re
import threading

def load_password_blacklist():
    with open("password_blacklist.txt", "r") as file:
        return set(file.read().splitlines())

def check_password():
    def evaluate_password():
        password = password_entry.get()

        # Perform password strength check
        score = 0
        suggestions = []
        blacklist = load_password_blacklist()

        # Check if password is in the blacklist
        if password in blacklist:
            result_text = "Weak: This password is commonly used. Please choose a more unique and secure password."
        else:
            # Check if password is a combination of blacklist words
            regex = re.compile(r"\b(?:{})\b".format("|".join(map(re.escape, blacklist))), re.IGNORECASE)
            if regex.search(password):
                result_text = "Weak: This password contains a combination of blacklist words. Please choose a more secure password."
            else:
                # Check length
                if len(password) >= 8:
                    score += 1
                elif len(password) >= 12:
                    score += 2

                # Check complexity
                complexity_checks = [
                    (re.search("[a-z]", password), "Add lowercase letters."),
                    (re.search("[A-Z]", password), "Add uppercase letters."),
                    (re.search("\d", password), "Add digits."),
                    (re.search("[!@#$%^&*()]", password), "Add special characters.")
                ]

                for check, suggestion in complexity_checks:
                    if check:
                        score += 1
                    else:
                        suggestions.append(suggestion)

                # Evaluate score and provide suggestions
                if score <= 2:
                    strength = "Weak"
                elif score <= 3:
                    strength = "Moderate"
                elif score <= 4:
                    strength = "Strong"
                else:
                    strength = "Very Strong"

                suggestions_text = ", ".join(suggestions) if suggestions else "None"
                result_text = f"{strength}: Password strength score: {score}/5\nSuggestions: {suggestions_text}"

        # Update the result label in the main thread
        window.after(0, lambda: result_label.configure(text=result_text))
        password_entry.delete(0, ctk.END)  # Reset password entry

    # Create a new thread for evaluating the password
    evaluation_thread = threading.Thread(target=evaluate_password)
    evaluation_thread.start()

def toggle_password_visibility():
    show_password = show_password_var.get()
    password_entry.configure(show="" if show_password else "*")

# Create the main window
window = ctk.CTk()
window.title("Password Strength Checker")

# Set the size of the window
window.geometry("450x350")

# Create and configure the input frame
input_frame = ctk.CTkFrame(window)
input_frame.pack(pady=10)

password_label = ctk.CTkLabel(input_frame, text="Password:")
password_label.pack(side=ctk.LEFT)

password_entry = ctk.CTkEntry(input_frame, show="*")
password_entry.pack(side=ctk.LEFT)

show_password_var = ctk.BooleanVar()  # Use CTkBooleanVar from customtkinter
show_password_checkbox = ctk.CTkCheckBox(input_frame, text="Show Password", variable=show_password_var, command=toggle_password_visibility)
show_password_checkbox.pack(side=ctk.LEFT)

check_button = ctk.CTkButton(window, text="Check Password", command=check_password)
check_button.pack(pady=10)

# Create the result label
result_label = ctk.CTkLabel(window, text="")
result_label.pack()

# Create the password strength progress bar
strength_frame = tk.Frame(window, width=400, height=20, bg="lightgray")
strength_frame.pack(pady=10)

strength_bar = tk.Canvas(strength_frame, width=0, height=20, bg="red", highlightthickness=0)
strength_bar.pack(side=tk.LEFT, fill=tk.BOTH)

def update_password_strength():
    password = password_entry.get()

    # Calculate password score
    score = 0
    complexity_checks = [
        (re.search("[a-z]", password), 1),
        (re.search("[A-Z]", password), 1),
        (re.search("\d", password), 1),
        (re.search("[!@#$%^&*()]", password), 1)
    ]

    for check, increment in complexity_checks:
        if check:
            score += increment

    # Calculate progress bar width based on score
    width = int((score / 4) * 400)  # 400 is the maximum width of the progress bar

    # Update the progress bar color based on score
    if score <= 2:
        color = "red"
    elif score <= 3:
        color = "orange"
    else:
        color = "green"

    # Clear previous progress bar
    strength_bar.delete("all")

    # Draw the updated progress bar
    strength_bar.create_rectangle(0, 0, width, 20, fill=color, width=0)

# Bind the password entry to update the strength progress bar in real-time
password_entry.bind("<KeyRelease>", lambda event: update_password_strength())


# Run the main event loop
window.mainloop()
