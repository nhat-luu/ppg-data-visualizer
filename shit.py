import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

class PPGVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("PPG CSV Visualizer")
        
        self.data = None

        # GUI Elements
        self.file_label = tk.Label(root, text="No file selected")
        self.file_label.pack(pady=5)

        self.load_button = tk.Button(root, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=5)

        self.column_frame = tk.Frame(root)
        self.column_frame.pack(pady=5)

        self.x_label = tk.Label(self.column_frame, text="X-axis:")
        self.x_label.grid(row=0, column=0, padx=5)
        self.x_dropdown = ttk.Combobox(self.column_frame, state="readonly")
        self.x_dropdown.grid(row=0, column=1, padx=5)

        self.y_label = tk.Label(self.column_frame, text="Y-axis:")
        self.y_label.grid(row=1, column=0, padx=5)
        self.y_dropdown = ttk.Combobox(self.column_frame, state="readonly")
        self.y_dropdown.grid(row=1, column=1, padx=5)

        self.plot_type_label = tk.Label(self.column_frame, text="Plot Type:")
        self.plot_type_label.grid(row=2, column=0, padx=5)
        self.plot_type_dropdown = ttk.Combobox(self.column_frame, state="readonly", values=["Histogram", "2D Histogram", "Boxplot"])
        self.plot_type_dropdown.grid(row=2, column=1, padx=5)
        self.plot_type_dropdown.set("Histogram")

        self.plot_button = tk.Button(root, text="Plot Data", command=self.plot_data)
        self.plot_button.pack(pady=5)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_label.config(text=file_path)
            self.data = pd.read_csv(file_path)
            columns = self.data.columns.tolist()
            self.x_dropdown["values"] = columns
            self.y_dropdown["values"] = columns

    def plot_data(self):
        if self.data is not None:
            x_col = self.x_dropdown.get()
            y_col = self.y_dropdown.get()
            plot_type = self.plot_type_dropdown.get()
            if x_col:
                plt.figure(figsize=(12, 6))
                if plot_type == "Histogram":
                    plt.hist(self.data[x_col], bins=30, label=f"Histogram of {x_col}")
                elif plot_type == "2D Histogram" and y_col:
                    plt.hist2d(self.data[x_col], self.data[y_col], bins=30, cmap="Blues")
                    plt.colorbar(label="Frequency")
                elif plot_type == "Boxplot":
                    plt.boxplot(self.data[x_col], vert=False, labels=[x_col])
                else:
                    tk.messagebox.showerror("Error", "Please select valid columns for the selected plot type")
                    return
                plt.title(f"{plot_type} Plot")
                if plot_type != "Boxplot":
                    plt.xlabel(x_col)
                    if y_col and plot_type == "2D Histogram":
                        plt.ylabel(y_col)
                plt.legend() if plot_type == "Histogram" else None
                plt.grid(True)
                plt.show()
            else:
                tk.messagebox.showerror("Error", "Please select X column")
        else:
            tk.messagebox.showerror("Error", "No data loaded")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PPGVisualizer(root)
    root.mainloop()