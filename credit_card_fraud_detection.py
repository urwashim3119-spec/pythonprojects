"""
Credit Card Fraud Detection - Beginner Tkinter GUI Project
Dataset: creditcard.csv with Time, V1...V28, Amount, Class columns.
Class: 0 = legitimate, 1 = fraud.

Educational demonstration only. Do not use for real banking decisions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

import imblearn



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

EXPECTED_FEATURES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
TARGET = "Class"


class FraudDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Credit Card Fraud Detection System")
        self.root.geometry("1050x720")
        self.root.minsize(900, 620)

        self.data = None
        self.models = {}
        self.results = {}
        self.feature_entries = {}
        self.best_model_name = None

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        header = tk.Frame(root, bg="#17365D", padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(
            header, text="CREDIT CARD FRAUD DETECTION",
            font=("Arial", 18, "bold"), fg="white", bg="#17365D"
        ).pack(anchor="w")
        tk.Label(
            header, text="Machine Learning • SMOTE • Model Comparison • ROC-AUC • Explainability",
            font=("Arial", 10), fg="white", bg="#17365D"
        ).pack(anchor="w", pady=(4, 0))

        controls = ttk.Frame(root, padding=12)
        controls.pack(fill="x")
        ttk.Button(controls, text="1. Load CSV Dataset", command=self.load_csv).pack(side="left", padx=4)
        self.train_button = ttk.Button(controls, text="2. Train & Compare Models", command=self.train_models)
        self.train_button.pack(side="left", padx=4)
        ttk.Button(controls, text="3. ROC Curve", command=self.show_roc).pack(side="left", padx=4)
        ttk.Button(controls, text="4. Explain Prediction (SHAP)", command=self.explain_prediction).pack(side="left", padx=4)

        self.status = tk.StringVar(value="Load creditcard.csv to begin.")
        ttk.Label(root, textvariable=self.status, foreground="#17365D", padding=(14, 2)).pack(fill="x")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=12, pady=8)

        self.results_tab = ttk.Frame(notebook, padding=10)
        self.predict_tab = ttk.Frame(notebook, padding=10)
        self.help_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.results_tab, text="Model Results")
        notebook.add(self.predict_tab, text="Transaction Simulation")
        notebook.add(self.help_tab, text="Instructions")

        self.build_results_tab()
        self.build_predict_tab()
        self.build_help_tab()

    def build_results_tab(self):
        ttk.Label(
            self.results_tab,
            text="Evaluation on the held-out test set (not the SMOTE-generated training data)",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 8))

        columns = ("model", "accuracy", "precision", "recall", "f1", "roc_auc")
        self.table = ttk.Treeview(self.results_tab, columns=columns, show="headings", height=7)
        headings = {
            "model": "Model", "accuracy": "Accuracy", "precision": "Precision",
            "recall": "Recall", "f1": "F1-score", "roc_auc": "ROC-AUC"
        }
        widths = {"model": 190, "accuracy": 105, "precision": 105, "recall": 105, "f1": 105, "roc_auc": 105}
        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(col, width=widths[col], anchor="center")
        self.table.pack(fill="x", pady=(0, 10))

        ttk.Label(self.results_tab, text="Detailed report:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.report_text = tk.Text(self.results_tab, height=15, wrap="word", font=("Consolas", 9))
        self.report_text.pack(fill="both", expand=True)
        self.report_text.insert("end", "Load a dataset and train models to view results.")
        self.report_text.configure(state="disabled")

    def build_predict_tab(self):
        top = ttk.Frame(self.predict_tab)
        top.pack(fill="x")
        ttk.Label(top, text="Select model:").pack(side="left")
        self.model_choice = tk.StringVar(value="Random Forest")
        self.model_combo = ttk.Combobox(
            top, textvariable=self.model_choice,
            values=["Logistic Regression", "Decision Tree", "Random Forest"],
            state="readonly", width=24
        )
        self.model_combo.pack(side="left", padx=8)
        ttk.Label(
            self.predict_tab,
            text="Enter Time, Amount and V1–V28. Defaults are zero for a quick GUI demo; use realistic dataset values for meaningful results.",
            wraplength=900
        ).pack(anchor="w", pady=8)

        # Scrollable feature input area
        outer = ttk.Frame(self.predict_tab)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, height=300, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.input_frame = ttk.Frame(canvas, padding=8)
        self.input_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.input_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for index, feature in enumerate(EXPECTED_FEATURES):
            row = index // 3
            col = (index % 3) * 2
            ttk.Label(self.input_frame, text=feature, width=8).grid(row=row, column=col, padx=5, pady=4, sticky="e")
            entry = ttk.Entry(self.input_frame, width=15)
            entry.insert(0, "0")
            entry.grid(row=row, column=col + 1, padx=5, pady=4, sticky="w")
            self.feature_entries[feature] = entry

        buttons = ttk.Frame(self.predict_tab)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Predict Transaction", command=self.predict_transaction).pack(side="left", padx=4)
        ttk.Button(buttons, text="Fill Sample from Test Data", command=self.fill_sample).pack(side="left", padx=4)
        self.prediction_result = tk.StringVar(value="Prediction will appear here.")
        ttk.Label(
            self.predict_tab, textvariable=self.prediction_result,
            font=("Arial", 12, "bold"), wraplength=900
        ).pack(anchor="w", pady=8)

    def build_help_tab(self):
        text = (
            "HOW TO USE THIS PROJECT\n\n"
            "1. Download the public credit-card fraud dataset and extract creditcard.csv.\n"
            "2. Click 'Load CSV Dataset' and select that file.\n"
            "3. Click 'Train & Compare Models'. Training can take a little time, especially with the full dataset.\n"
            "4. Check Accuracy, Precision, Recall, F1-score and ROC-AUC in Model Results.\n"
            "5. Click 'ROC Curve' to compare model curves.\n"
            "6. Open Transaction Simulation, enter feature values and click Predict Transaction.\n"
            "7. Select a trained model and click Explain Prediction (SHAP). If SHAP is not installed or unavailable for the chosen model, the app shows a feature-based fallback explanation.\n\n"
            "DATASET COLUMNS\n"
            "Time, V1 to V28, Amount, Class. Class 0 means legitimate; Class 1 means fraud.\n\n"
            "METHODS USED\n"
            "• Train/test split: keeps evaluation data separate.\n"
            "• StandardScaler: puts numeric features on comparable scales.\n"
            "• SelectKBest: selects the 15 most informative features.\n"
            "• SMOTE: creates synthetic minority-class examples ONLY in the training data.\n"
            "• Three models: Logistic Regression, Decision Tree, Random Forest.\n"
            "• ROC-AUC: measures how well scores separate the two classes.\n"
            "• SHAP: attempts to explain which selected features influenced a tree-model prediction.\n\n"
            "IMPORTANT LIMITATIONS\n"
            "This is an academic demonstration, not a live connection to a bank or payment processor. The dataset's V1–V28 columns are anonymized PCA components, so they do not describe human-readable transaction details. A zero-filled transaction is not a realistic transaction. Model output is not proof of fraud."
        )
        box = tk.Text(self.help_tab, wrap="word", font=("Arial", 10))
        box.pack(fill="both", expand=True)
        box.insert("1.0", text)
        box.configure(state="disabled")

    def load_csv(self):
        path = filedialog.askopenfilename(
            title="Select creditcard.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            df = pd.read_csv(path)
            missing = [c for c in EXPECTED_FEATURES + [TARGET] if c not in df.columns]
            if missing:
                messagebox.showerror(
                    "Wrong dataset format",
                    "The CSV is missing these required columns:\n" + ", ".join(missing)
                )
                return
            df = df[EXPECTED_FEATURES + [TARGET]].copy()
            df = df.replace([np.inf, -np.inf], np.nan).dropna()
            df[TARGET] = df[TARGET].astype(int)
            if set(df[TARGET].unique()) != {0, 1}:
                messagebox.showerror("Invalid target", "The Class column must contain both 0 and 1.")
                return
            if df[TARGET].value_counts().min() < 3:
                messagebox.showerror("Not enough examples", "The dataset needs at least 3 examples of each class.")
                return
            self.data = df
            self.models.clear()
            self.results.clear()
            for item in self.table.get_children():
                self.table.delete(item)
            self.status.set(
                f"Loaded {os.path.basename(path)} | {len(df):,} rows | "
                f"Legitimate: {(df[TARGET] == 0).sum():,} | Fraud: {(df[TARGET] == 1).sum():,}"
            )
            messagebox.showinfo("Dataset loaded", f"Loaded {len(df):,} usable rows successfully.")
        except Exception as exc:
            messagebox.showerror("Could not load file", str(exc))

    def train_models(self):
        if self.data is None:
            messagebox.showwarning("Dataset required", "Please load creditcard.csv first.")
            return
        self.train_button.configure(state="disabled")
        self.status.set("Training models. Please wait...")
        thread = threading.Thread(target=self._train_worker, daemon=True)
        thread.start()

    def _train_worker(self):
        try:
            X = self.data[EXPECTED_FEATURES]
            y = self.data[TARGET]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.25, random_state=42, stratify=y
            )
            # SelectKBest cannot choose more features than the dataset contains.
            k = min(15, X_train.shape[1])
            model_definitions = {
                "Logistic Regression": LogisticRegression(
                    max_iter=1000, class_weight=None, random_state=42
                ),
                "Decision Tree": DecisionTreeClassifier(
                    max_depth=10, random_state=42, class_weight=None
                ),
                "Random Forest": RandomForestClassifier(
                    n_estimators=100, max_depth=14, random_state=42,
                    n_jobs=-1, class_weight=None
                )
            }
            new_models = {}
            new_results = {}
            for name, estimator in model_definitions.items():
                self.root.after(0, lambda n=name: self.status.set(f"Training {n}..."))
                pipeline = ImbPipeline(steps=[
                    ("scaler", StandardScaler()),
                    ("selector", SelectKBest(score_func=f_classif, k=k)),
                    ("smote", SMOTE(random_state=42, k_neighbors=min(5, int(y_train.value_counts().min()) - 1))),
                    ("model", estimator)
                ])
                pipeline.fit(X_train, y_train)
                predictions = pipeline.predict(X_test)
                probabilities = pipeline.predict_proba(X_test)[:, 1]
                metrics = {
                    "accuracy": accuracy_score(y_test, predictions),
                    "precision": precision_score(y_test, predictions, zero_division=0),
                    "recall": recall_score(y_test, predictions, zero_division=0),
                    "f1": f1_score(y_test, predictions, zero_division=0),
                    "roc_auc": roc_auc_score(y_test, probabilities),
                    "y_test": y_test.copy(),
                    "predictions": predictions,
                    "probabilities": probabilities,
                    "confusion": confusion_matrix(y_test, predictions)
                }
                new_models[name] = pipeline
                new_results[name] = metrics

            self.models = new_models
            self.results = new_results
            self.best_model_name = max(new_results, key=lambda n: new_results[n]["roc_auc"])
            self.root.after(0, self.update_results)
        except Exception as exc:
            self.root.after(0, lambda error=str(exc): messagebox.showerror("Training error", error))
            self.root.after(0, lambda: self.status.set("Training failed. Check the dataset and installed libraries."))
        finally:
            self.root.after(0, lambda: self.train_button.configure(state="normal"))

    def update_results(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for name, m in self.results.items():
            self.table.insert("", "end", values=(
                name, f"{m['accuracy']:.4f}", f"{m['precision']:.4f}",
                f"{m['recall']:.4f}", f"{m['f1']:.4f}", f"{m['roc_auc']:.4f}"
            ))
        best = self.best_model_name
        m = self.results[best]
        report = (
            f"Best model by ROC-AUC: {best}\n\n"
            f"Selected features: {', '.join(self.models[best].named_steps['selector'].get_feature_names_out(EXPECTED_FEATURES))}\n\n"
            f"Confusion matrix (rows = actual [legitimate, fraud], columns = predicted [legitimate, fraud]):\n"
            f"{m['confusion']}\n\n"
            f"Classification report:\n"
            f"{classification_report(m['y_test'], m['predictions'], target_names=['Legitimate', 'Fraud'], zero_division=0)}\n"
            "Note: Accuracy alone can be misleading on an imbalanced dataset. Pay attention to fraud recall, precision, F1-score and ROC-AUC."
        )
        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", report)
        self.report_text.configure(state="disabled")
        self.status.set(f"Training complete. Best ROC-AUC in this run: {best}.")

    def show_roc(self):
        if not self.results:
            messagebox.showwarning("Train models first", "Train the models before viewing the ROC curve.")
            return
        try:
            
            from sklearn.metrics import RocCurveDisplay
            for name, m in self.results.items():
                RocCurveDisplay.from_predictions(m["y_test"], m["probabilities"], name=name)
            plt.title("ROC Curve Comparison")
            plt.grid(True, alpha=0.25)
            plt.tight_layout()
            plt.show()
        except ImportError:
            messagebox.showerror("Missing library", "Install matplotlib using: pip install matplotlib")

    def get_transaction(self):
        values = {}
        try:
            for feature in EXPECTED_FEATURES:
                values[feature] = float(self.feature_entries[feature].get())
            if values["Amount"] < 0 or values["Time"] < 0:
                raise ValueError("Time and Amount cannot be negative.")
            return pd.DataFrame([values], columns=EXPECTED_FEATURES)
        except ValueError as exc:
            messagebox.showerror("Invalid input", f"Please enter valid numbers in all fields.\n{exc}")
            return None

    def predict_transaction(self):
        if not self.models:
            messagebox.showwarning("Train models first", "Load the dataset and train models first.")
            return
        X_new = self.get_transaction()
        if X_new is None:
            return
        name = self.model_choice.get()
        if name not in self.models:
            messagebox.showwarning("Choose model", "Select one of the trained models.")
            return
        model = self.models[name]
        prediction = int(model.predict(X_new)[0])
        probability = float(model.predict_proba(X_new)[0, 1])
        if prediction == 1:
            message = f"⚠ POSSIBLE FRAUD FLAG | Model: {name} | Estimated fraud score: {probability:.1%}"
        else:
            message = f"✓ NOT FLAGGED AS FRAUD | Model: {name} | Estimated fraud score: {probability:.1%}"
        message += "\nThis is a model prediction, not a confirmed real-world finding."
        self.prediction_result.set(message)

    def fill_sample(self):
        if not self.models:
            messagebox.showwarning("Train models first", "Train models before filling a sample transaction.")
            return
        # Use a row from the held-out data stored in the fitted pipeline's training workflow.
        # A random row from the loaded data is only used to demonstrate the form.
        row = self.data.sample(1, random_state=None).iloc[0]
        for feature in EXPECTED_FEATURES:
            self.feature_entries[feature].delete(0, "end")
            self.feature_entries[feature].insert(0, str(float(row[feature])))
        messagebox.showinfo(
            "Sample filled",
            f"Filled values from one dataset row. Actual dataset label: "
            f"{'Fraud' if int(row[TARGET]) == 1 else 'Legitimate'}.\n"
            "Use Predict Transaction to see the selected model's prediction."
        )

    def explain_prediction(self):
        if not self.models:
            messagebox.showwarning("Train models first", "Train models before asking for an explanation.")
            return
        X_new = self.get_transaction()
        if X_new is None:
            return
        name = self.model_choice.get()
        pipeline = self.models[name]
        selected_names = list(pipeline.named_steps["selector"].get_feature_names_out(EXPECTED_FEATURES))
        scaled = pipeline.named_steps["scaler"].transform(X_new)
        selected = pipeline.named_steps["selector"].transform(scaled)
        estimator = pipeline.named_steps["model"]
        prediction = int(pipeline.predict(X_new)[0])
        lines = [f"Model: {name}", f"Prediction: {'Possible fraud' if prediction == 1 else 'Not flagged'}", "",
                 "Selected features for this model:", ", ".join(selected_names), ""]

        try:
            import shap
            if isinstance(estimator, (DecisionTreeClassifier, RandomForestClassifier)):
                explainer = shap.TreeExplainer(estimator)
                shap_values = explainer.shap_values(selected)
                # SHAP output format varies by version; choose class 1 values.
                if isinstance(shap_values, list):
                    values = np.asarray(shap_values[1])[0]
                else:
                    arr = np.asarray(shap_values)
                    if arr.ndim == 3:
                        values = arr[0, :, 1]
                    elif arr.ndim == 2:
                        values = arr[0]
                    else:
                        values = arr.reshape(-1)
                ranking = sorted(zip(selected_names, values), key=lambda item: abs(float(item[1])), reverse=True)[:8]
                lines += ["Top SHAP contributions (magnitude, not a guarantee of cause):"]
                lines += [f"  {feature}: {float(value):+.5f}" for feature, value in ranking]
                lines += ["", "Positive/negative direction can depend on the SHAP output format and class. Treat these as model explanations, not proof of fraud."]
            elif isinstance(estimator, LogisticRegression):
                contributions = estimator.coef_[0] * selected[0]
                ranking = sorted(zip(selected_names, contributions), key=lambda item: abs(float(item[1])), reverse=True)[:8]
                lines += ["SHAP is best supported here with a tree model. Logistic Regression fallback: largest coefficient × scaled-feature contributions:"]
                lines += [f"  {feature}: {float(value):+.5f}" for feature, value in ranking]
            else:
                lines += ["This model does not have a supported built-in SHAP explanation in this beginner demo."]
        except ImportError:
            # Beginner-friendly fallback if optional SHAP package is not installed.
            if hasattr(estimator, "feature_importances_"):
                ranking = sorted(zip(selected_names, estimator.feature_importances_), key=lambda item: float(item[1]), reverse=True)[:8]
                lines += ["SHAP is not installed. Showing built-in feature importance instead:"]
                lines += [f"  {feature}: {float(value):.5f}" for feature, value in ranking]
                lines += ["", "Install SHAP with: pip install shap"]
            else:
                lines += ["SHAP is not installed. This model's selected features are listed above."]
                lines += ["Install SHAP with: pip install shap"]
        except Exception as exc:
            lines += [f"Could not create SHAP explanation: {exc}", "Try a tree-based model or install/update shap."]
        messagebox.showinfo("Model Explanation", "\n".join(lines))


if __name__ == "__main__":
    root = tk.Tk()
    app = FraudDetectionApp(root)
    root.mainloop()
