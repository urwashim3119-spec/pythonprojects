

import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# -----------------------------
# 1. Train the machine learning model
# -----------------------------
def train_model():
    print("Loading handwritten digit dataset...")
    digits = load_digits()
    X = digits.data
    y = digits.target

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print(f"Dataset images: {len(X)}")
    print(f"Training images: {len(X_train)}")
    print(f"Testing images: {len(X_test)}")
    print(f"Test accuracy: {accuracy * 100:.2f}%")
    print("Model training complete.\n")

    return model, accuracy


# -----------------------------
# 2. Train model before opening GUI
# -----------------------------
model, test_accuracy = train_model()


# -----------------------------
# 3. Set up GUI
# -----------------------------
WINDOW_SIZE = 280
BRUSH_WIDTH = 10

root = tk.Tk()
root.title("")
root.geometry("470x640")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="Handwritten Digit Recognizer",
    font=("Arial", 17, "bold")
)
title_label.pack(pady=(15, 4))

instructions = tk.Label(
    root,
    text="Draw one digit (0-9) in the white box, then click Predict.",
    font=("Arial", 10),
    wraplength=430
)
instructions.pack(pady=(0, 10))

canvas = tk.Canvas(
    root,
    width=WINDOW_SIZE,
    height=WINDOW_SIZE,
    bg="white",
    cursor="cross",
    highlightthickness=2,
    highlightbackground="#888888"
)
canvas.pack()

# Keep a matching grayscale image for machine-learning preprocessing.
# White background = 255; black ink = 0.
drawing_image = Image.new("L", (WINDOW_SIZE, WINDOW_SIZE), 255)
draw = ImageDraw.Draw(drawing_image)

last_x = None
last_y = None


# -----------------------------
# 4. Mouse drawing functions
# -----------------------------
def start_drawing(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

    # Add a dot if the user only clicks once.
    radius = BRUSH_WIDTH // 2
    canvas.create_oval(
        event.x - radius, event.y - radius,
        event.x + radius, event.y + radius,
        fill="black", outline="black"
    )
    draw.ellipse(
        (event.x - radius, event.y - radius,
         event.x + radius, event.y + radius),
        fill=0
    )


def draw_digit(event):
    global last_x, last_y

    if last_x is not None and last_y is not None:
        canvas.create_line(
            last_x, last_y, event.x, event.y,
            fill="black",
            width=BRUSH_WIDTH,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True
        )

        draw.line(
            (last_x, last_y, event.x, event.y),
            fill=0,
            width=BRUSH_WIDTH
        )

        # Rounded ends help keep the saved image close to the visible drawing.
        radius = BRUSH_WIDTH // 2
        draw.ellipse(
            (event.x - radius, event.y - radius,
             event.x + radius, event.y + radius),
            fill=0
        )

    last_x, last_y = event.x, event.y


def stop_drawing(event):
    global last_x, last_y
    last_x, last_y = None, None


canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw_digit)
canvas.bind("<ButtonRelease-1>", stop_drawing)


# -----------------------------
# 5. Prepare drawing for the model
# -----------------------------
def prepare_image_for_model():
    """
    The model was trained on 8x8 images with bright digits on a dark background.
    Our canvas has black ink on white, so invert it and scale pixels to 0-16.
    """
    # Crop around the actual handwriting so the digit is not too tiny.
    inverted = ImageOps.invert(drawing_image)
    bbox = inverted.getbbox()

    if bbox is None:
        return None

    cropped = inverted.crop(bbox)

    # Add a margin around the digit while preserving its proportions.
    width, height = cropped.size
    side = max(width, height) + 12
    square = Image.new("L", (side, side), 0)
    left = (side - width) // 2
    top = (side - height) // 2
    square.paste(cropped, (left, top))

    # Resize to the same 8x8 input size as the training data.
    small = square.resize((8, 8), Image.Resampling.LANCZOS)

    # Scikit-learn digits images use values from 0 to 16.
    pixels = np.asarray(small, dtype=np.float64)
    pixels = pixels * (16.0 / 255.0)

    # Shape must be (number_of_images, number_of_features) = (1, 64).
    return pixels.reshape(1, 64)


# -----------------------------
# 6. Predict the digit
# -----------------------------
def predict_digit():
    features = prepare_image_for_model()

    if features is None:
        messagebox.showwarning(
            "Empty Canvas",
            "Please draw a digit first."
        )
        return

    predicted_digit = int(model.predict(features)[0])

    # Random Forest estimates a probability for each digit class.
    probabilities = model.predict_proba(features)[0]
    class_index = list(model.classes_).index(predicted_digit)
    confidence = float(probabilities[class_index]) * 100

    result_label.config(
        text=f"Predicted Digit: {predicted_digit}",
        fg="#167a35"
    )
    confidence_label.config(
        text=f"Model confidence score: {confidence:.1f}%"
    )

    # Show all class scores so the user can see alternative predictions.
    scores = "\n".join(
        f"{digit}: {probabilities[list(model.classes_).index(digit)] * 100:.1f}%"
        for digit in range(10)
    )
    probability_label.config(
        text="Scores by digit (0-9):\n" + "   ".join(
            f"{digit}: {probabilities[list(model.classes_).index(digit)] * 100:.0f}%"
            for digit in range(10)
        )
    )


# -----------------------------
# 7. Clear canvas
# -----------------------------
def clear_canvas():
    global drawing_image, draw, last_x, last_y

    canvas.delete("all")
    drawing_image = Image.new("L", (WINDOW_SIZE, WINDOW_SIZE), 255)
    draw = ImageDraw.Draw(drawing_image)
    last_x, last_y = None, None

    result_label.config(
        text="Predicted Digit: —",
        fg="black"
    )
    confidence_label.config(text="Draw a digit and click Predict.")
    probability_label.config(text="")


# -----------------------------
# 8. Buttons and result labels
# -----------------------------
button_frame = tk.Frame(root)
button_frame.pack(pady=16)

predict_button = tk.Button(
    button_frame,
    text="Predict Digit",
    command=predict_digit,
    font=("Arial", 11, "bold"),
    width=15,
    height=2,
    bg="#8e79b8"
)
predict_button.grid(row=0, column=0, padx=8)

clear_button = tk.Button(
    button_frame,
    text="Clear Canvas",
    command=clear_canvas,
    font=("Arial", 11),
    width=15,
    height=2,
    bg="#8e79b8"
)
clear_button.grid(row=0, column=1, padx=8)

result_label = tk.Label(
    root,
    text="Predicted Digit: —",
    font=("Arial", 16, "bold")
)
result_label.pack(pady=(4, 2))

confidence_label = tk.Label(
    root,
    text="Draw a digit and click Predict.",
    font=("Arial", 10)
)
confidence_label.pack(pady=3)

probability_label = tk.Label(
    root,
    text="",
    font=("Consolas", 9),
    wraplength=440,
    justify="center"
)
probability_label.pack(pady=8)

accuracy_label = tk.Label(
    root,
    text=f"Model test accuracy on held-out dataset: {test_accuracy * 100:.2f}%",
    font=("Arial", 9),
    fg="#555555"
)
accuracy_label.pack(side="bottom", pady=10)


# -----------------------------
# 9. Start the application
# -----------------------------
root.mainloop()
