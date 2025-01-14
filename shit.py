import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from typing import Optional, Callable, List

class PPGVisualizer:
    def __init__(self, root: tk.Tk):
        """
        Initialisiert den PPG Visualizer.

        Args:
            root: Das Hauptfenster der Anwendung.
        """
        self.PLOT_TYPES = {
            "Histogram": self._plot_histogram,
            "2D Histogram": self._plot_2d_histogram,
            "Boxplot": self._plot_boxplot,
            "Scatter": self._plot_scatter,
            "Scatter mit Linie": self._plot_scatter_with_line
        }
        self.OPERATORS = [">", "<", ">=", "<=", "==", "!="]
        self.DEFAULT_FIGSIZE = (12, 6)

        self.root = root
        self.root.title("PPG CSV Visualizer")
        self.original_data: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None
        self.filter_conditions: List[str] = []

        self._create_gui()

    def _create_gui(self):
        """Erstellt das Hauptlayout der GUI."""
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self._create_file_section()
        self._create_plot_section()
        self._create_filter_section()
        self._create_action_section()

    def _create_file_section(self):
        """Erstellt den Dateiauswahlbereich."""
        file_frame = ttk.LabelFrame(self.main_container, text="Dateiauswahl")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        self.file_label = ttk.Label(file_frame, text="Keine Datei ausgewählt")
        self.file_label.pack(pady=5)

        self.load_button = ttk.Button(file_frame, text="CSV laden", command=self.load_csv)
        self.load_button.pack(pady=5)

    def _create_filter_section(self):
        """Erstellt den Filterbereich."""
        filter_frame = ttk.LabelFrame(self.main_container, text="Filter")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        # Filter Spalte
        filter_col_frame = ttk.Frame(filter_frame)
        filter_col_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(filter_col_frame, text="Filter Spalte:").pack(side=tk.LEFT)
        self.filter_column_dropdown = ttk.Combobox(filter_col_frame, state="readonly")
        self.filter_column_dropdown.pack(side=tk.LEFT, padx=5)

        # Filter Operator
        filter_op_frame = ttk.Frame(filter_frame)
        filter_op_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(filter_op_frame, text="Operator:").pack(side=tk.LEFT)
        self.filter_operator_dropdown = ttk.Combobox(
            filter_op_frame, state="readonly", values=self.OPERATORS
        )
        self.filter_operator_dropdown.pack(side=tk.LEFT, padx=5)

        # Filter Wert
        filter_val_frame = ttk.Frame(filter_frame)
        filter_val_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(filter_val_frame, text="Filter Wert:").pack(side=tk.LEFT)
        self.filter_value_entry = ttk.Entry(filter_val_frame)
        self.filter_value_entry.pack(side=tk.LEFT, padx=5)

        # Filter Buttons
        filter_btn_frame = ttk.Frame(filter_frame)
        filter_btn_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(
            filter_btn_frame,
            text="Bedingung hinzufügen",
            command=self.add_filter_condition
        ).pack(side=tk.LEFT, padx=5)

        self.conditions_listbox = tk.Listbox(filter_frame, height=5)
        self.conditions_listbox.pack(fill=tk.X, padx=5, pady=5)

        condition_btn_frame = ttk.Frame(filter_frame)
        condition_btn_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(
            condition_btn_frame,
            text="Ausgewählte Bedingung entfernen",
            command=self.remove_condition
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            condition_btn_frame,
            text="Filter anwenden",
            command=self.apply_filters
        ).pack(side=tk.LEFT, padx=5)

    def _create_plot_section(self):
        """Erstellt den Plot-Konfigurationsbereich."""
        plot_frame = ttk.LabelFrame(self.main_container, text="Plot-Konfiguration")
        plot_frame.pack(fill=tk.X, padx=5, pady=5)

        # X-Achse
        x_frame = ttk.Frame(plot_frame)
        x_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(x_frame, text="X-Achse:").pack(side=tk.LEFT)
        self.x_dropdown = ttk.Combobox(x_frame, state="readonly")
        self.x_dropdown.pack(side=tk.LEFT, padx=5)

        # Y-Achse
        y_frame = ttk.Frame(plot_frame)
        y_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(y_frame, text="Y-Achse:").pack(side=tk.LEFT)
        self.y_dropdown = ttk.Combobox(y_frame, state="readonly")
        self.y_dropdown.pack(side=tk.LEFT, padx=5)

        # Plot-Typ
        type_frame = ttk.Frame(plot_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(type_frame, text="Plot-Typ:").pack(side=tk.LEFT)
        self.plot_type_dropdown = ttk.Combobox(
            type_frame, state="readonly", values=list(self.PLOT_TYPES.keys())
        )
        self.plot_type_dropdown.pack(side=tk.LEFT, padx=5)
        self.plot_type_dropdown.set("Histogram")

        self.map_pl_to_time_var = tk.BooleanVar()
        ttk.Checkbutton(
            plot_frame,
            text="`pl` als Zeit mappen",
            variable=self.map_pl_to_time_var
        ).pack(side=tk.LEFT, padx=5)

    def _create_action_section(self):
        """Erstellt den Aktionsbereich."""
        action_frame = ttk.Frame(self.main_container)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            action_frame, text="Daten plotten", command=self.plot_data
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            action_frame, text="Grafik exportieren", command=self._export_plot
        ).pack(side=tk.LEFT, padx=5)

    def load_csv(self):
        """Lädt eine CSV-Datei und verarbeitet sie."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.original_data = pd.read_csv(file_path)
                self.filtered_data = self.original_data.copy()
                self._update_gui_after_load(file_path)
                messagebox.showinfo("Erfolg", "Datei erfolgreich geladen!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {str(e)}")

    def _update_gui_after_load(self, file_path: str):
        """Aktualisiert die GUI nach dem Laden einer Datei."""
        self.file_label.config(text=file_path)
        columns = self.original_data.columns.tolist()
        self.x_dropdown["values"] = columns
        self.y_dropdown["values"] = columns
        self.filter_column_dropdown["values"] = columns

    def add_filter_condition(self):
        """Fügt eine neue Filterbedingung hinzu."""
        filter_col = self.filter_column_dropdown.get()
        filter_val = self.filter_value_entry.get()
        operator = self.filter_operator_dropdown.get()

        if filter_col and filter_val and operator:
            condition = f"{filter_col} {operator} {filter_val}"
            self.filter_conditions.append(condition)
            self.conditions_listbox.insert(tk.END, condition)
            self.filter_value_entry.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Fehler", "Bitte Spalte, Operator und Wert auswählen."
            )

    def remove_condition(self):
        """Entfernt die ausgewählte Filterbedingung."""
        selected_idx = self.conditions_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            self.conditions_listbox.delete(idx)
            del self.filter_conditions[idx]
        else:
            messagebox.showerror("Fehler", "Keine Bedingung zum Entfernen ausgewählt.")

    def apply_filters(self):
        """Wendet alle Filterbedingungen auf die Daten an."""
        if self.original_data is None:
            messagebox.showerror("Fehler", "Keine Daten geladen.")
            return

        if not self.filter_conditions:
            self.filtered_data = self.original_data.copy()
            messagebox.showinfo("Info", "Keine Filter definiert, zeige alle Daten.")
            return

        try:
            query_string = " & ".join(self.filter_conditions)
            self.filtered_data = self.original_data.query(query_string)
            messagebox.showinfo(
                "Erfolg", f"Filter angewendet. {len(self.filtered_data)} Zeilen übrig."
            )
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anwenden der Filter: {str(e)}")

    def plot_data(self):
        """Erstellt den ausgewählten Plot."""
        if self.filtered_data is None or self.filtered_data.empty:
            messagebox.showerror("Fehler", "Keine Daten zum Plotten verfügbar.")
            return

        x_col = self.x_dropdown.get()
        y_col = self.y_dropdown.get()
        plot_type = self.plot_type_dropdown.get()

        # Optional: `pl` in Zeit umwandeln
        if self.map_pl_to_time_var.get() and x_col == 'pl':
            self.filtered_data['pl_time'] = (
                self.filtered_data['pl'] /
                self.filtered_data.groupby('Patient_Id')['pl'].transform('max') *
                10
            )
            x_col = 'pl_time'

        plot_func = self.PLOT_TYPES.get(plot_type)
        if plot_func:
            self._safe_plot(plot_func, x_col=x_col, y_col=y_col)
        else:
            messagebox.showerror("Fehler", "Ungültiger Plot-Typ ausgewählt.")

    def _safe_plot(self, plot_func: Callable, x_col: str, y_col: Optional[str] = None):
        """Führt eine Plot-Funktion sicher aus."""
        try:
            plot_func(x_col, y_col)
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def _plot_histogram(self, x_col: str, y_col: Optional[str] = None):
        """Erstellt ein Histogram."""
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.hist(self.filtered_data[x_col], bins='auto', alpha=0.7)
        plt.xlabel(x_col)
        plt.ylabel("Häufigkeit")
        plt.title(f"Histogram von {x_col}")
        plt.grid(True)
        plt.show()

    def _plot_2d_histogram(self, x_col: str, y_col: str):
        """Erstellt ein 2D-Histogram."""
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.hist2d(self.filtered_data[x_col], self.filtered_data[y_col], bins=30, cmap="Blues")
        plt.colorbar(label="Häufigkeit")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"2D Histogram von {x_col} und {y_col}")
        plt.grid(True)
        plt.show()

    def _plot_boxplot(self, x_col: str, y_col: Optional[str] = None):
        """Erstellt ein Boxplot."""
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.boxplot(self.filtered_data[x_col], vert=False, labels=[x_col])
        plt.xlabel("Wert")
        plt.title(f"Boxplot von {x_col}")
        plt.grid(True)
        plt.show()

    def _plot_scatter(self, x_col: str, y_col: str):
        """Erstellt einen Scatterplot."""
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.scatter(self.filtered_data[x_col], self.filtered_data[y_col], alpha=0.7)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"Scatterplot von {x_col} vs. {y_col}")
        plt.grid(True)
        plt.show()

    def _plot_scatter_with_line(self, x_col: str, y_col: str):
        """Erstellt einen Scatterplot mit Linie."""
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        #plt.scatter(self.filtered_data[x_col], self.filtered_data[y_col], alpha=0.7, label="Datenpunkte")
        plt.plot(self.filtered_data[x_col], self.filtered_data[y_col], linestyle="-", color="blue", label="Linie")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"Scatterplot von {x_col} vs. {y_col} mit Linie")
        plt.legend()
        plt.grid(True)
        plt.show()

    def _export_plot(self):
        """Exportiert den aktuellen Plot."""
        messagebox.showinfo("Info", "Die Exportfunktion ist noch nicht implementiert.")

    def on_closing(self):
        """Handhabt das Schließen der Anwendung."""
        if messagebox.askokcancel("Beenden", "Möchten Sie die Anwendung schließen?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PPGVisualizer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()