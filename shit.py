import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, messagebox

class PPGVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("PPG CSV Visualizer")
        
        self.original_data = None
        self.filtered_data = None

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
        self.plot_type_dropdown = ttk.Combobox(self.column_frame, state="readonly", values=["Histogram", "2D Histogram", "Boxplot", "Scatter"])
        self.plot_type_dropdown.grid(row=2, column=1, padx=5)
        self.plot_type_dropdown.set("Histogram")

        self.filter_frame = tk.Frame(root)
        self.filter_frame.pack(pady=5)

        self.filter_label = tk.Label(self.filter_frame, text="Filter Column:")
        self.filter_label.grid(row=0, column=0, padx=5)
        self.filter_column_dropdown = ttk.Combobox(self.filter_frame, state="readonly")
        self.filter_column_dropdown.grid(row=0, column=1, padx=5)

        self.filter_value_label = tk.Label(self.filter_frame, text="Filter Value:")
        self.filter_value_label.grid(row=1, column=0, padx=5)
        self.filter_value_entry = tk.Entry(self.filter_frame)
        self.filter_value_entry.grid(row=1, column=1, padx=5)

        self.filter_operator_label = tk.Label(self.filter_frame, text="Operator:")
        self.filter_operator_label.grid(row=2, column=0, padx=5)
        self.filter_operator_dropdown = ttk.Combobox(self.filter_frame, state="readonly", values=[">", "<", ">=", "<=", "==", "!="])
        self.filter_operator_dropdown.grid(row=2, column=1, padx=5)

        self.add_filter_button = tk.Button(self.filter_frame, text="Add Condition", command=self.add_filter_condition)
        self.add_filter_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.conditions_label = tk.Label(self.filter_frame, text="Conditions:")
        self.conditions_label.grid(row=4, column=0, columnspan=2, pady=5)

        self.conditions_listbox = tk.Listbox(self.filter_frame, width=50, height=5)
        self.conditions_listbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.remove_condition_button = tk.Button(self.filter_frame, text="Remove Selected Condition", command=self.remove_condition)
        self.remove_condition_button.grid(row=6, column=0, columnspan=2, pady=5)

        self.apply_filter_button = tk.Button(self.filter_frame, text="Apply Filters", command=self.apply_filters)
        self.apply_filter_button.grid(row=7, column=0, columnspan=2, pady=5)

        self.plot_button = tk.Button(root, text="Plot Data", command=self.plot_data)
        self.plot_button.pack(pady=5)

        self.filter_conditions = []

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_label.config(text=file_path)
            self.original_data = pd.read_csv(file_path)
            self.filtered_data = self.original_data.copy()
            columns = self.original_data.columns.tolist()
            self.x_dropdown["values"] = columns
            self.y_dropdown["values"] = columns
            self.filter_column_dropdown["values"] = columns

    def add_filter_condition(self):
        filter_col = self.filter_column_dropdown.get()
        filter_val = self.filter_value_entry.get()
        operator = self.filter_operator_dropdown.get()
        if filter_col and filter_val and operator:
            condition = f"{filter_col} {operator} {filter_val}"
            self.filter_conditions.append(condition)
            self.conditions_listbox.insert(tk.END, condition)
        else:
            messagebox.showerror("Error", "Please select a column, operator, and value.")

    def remove_condition(self):
        selected_idx = self.conditions_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            self.conditions_listbox.delete(idx)
            del self.filter_conditions[idx]
        else:
            messagebox.showerror("Error", "No condition selected to remove.")

    def apply_filters(self):
        if self.original_data is not None and self.filter_conditions:
            try:
                query_string = " & ".join(self.filter_conditions)
                self.filtered_data = self.original_data.query(query_string)
                messagebox.showinfo("Success", "Filters applied successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply filters: {e}")
        else:
            messagebox.showerror("Error", "No filters to apply or no data loaded.")

    def plot_data(self):
        if self.filtered_data is not None:
            x_col = self.x_dropdown.get()
            y_col = self.y_dropdown.get()
            plot_type = self.plot_type_dropdown.get()
            if x_col:
                plt.figure(figsize=(12, 6))
                if plot_type == "Histogram":
                    plt.hist(self.filtered_data[x_col], bins=30, label=f"Histogram of {x_col}")
                elif plot_type == "2D Histogram" and y_col:
                    plt.hist2d(self.filtered_data[x_col], self.filtered_data[y_col], bins=30, cmap="Blues")
                    plt.colorbar(label="Frequency")
                elif plot_type == "Boxplot":
                    plt.boxplot(self.filtered_data[x_col], vert=False, labels=[x_col])
                elif plot_type == "Scatter" and y_col:
                    plt.scatter(self.filtered_data[x_col], self.filtered_data[y_col], alpha=0.7)
                else:
                    messagebox.showerror("Error", "Please select valid columns for the selected plot type")
                    return
                plt.title(f"{plot_type} Plot")
                if plot_type not in ["Boxplot"]:
                    plt.xlabel(x_col)
                    if y_col and plot_type in ["2D Histogram", "Scatter"]:
                        plt.ylabel(y_col)
                plt.legend() if plot_type == "Histogram" else None
                plt.grid(True)
                plt.show()
            else:
                messagebox.showerror("Error", "Please select X column")
        else:
            messagebox.showerror("Error", "No data loaded")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PPGVisualizer(root)
    root.mainloop()