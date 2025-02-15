import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
from typing import Optional, Callable, Dict, List

class PPGVisualizer:
    def __init__(self, root: tk.Tk):
        """
        Initialisiert den PPG Visualizer.

        Args:
            root: Das Hauptfenster der Anwendung.
        """
        # Konstanten
        self.PLOT_TYPES = {
            "Histogram": self._plot_histogram,
            "2D Histogram": self._plot_2d_histogram,
            "Boxplot": self._plot_boxplot,
            "Scatter": self._plot_scatter,
            "Scatter mit Linie": self._plot_scatter_with_line
        }
        self.OPERATORS = [">", "<", ">=", "<=", "==", "!="]
        self.DEFAULT_FIGSIZE = (12, 6)
        
        # Hauptattribute
        self.root = root
        self.root.title("PPG CSV Visualizer")
        self.original_data: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None
        self.filter_conditions: List[str] = []
        self.cached_stats: Dict = {}
        self._data_hash: Optional[int] = None
        
        # GUI erstellen
        self._create_gui()
        
    def _create_gui(self):
        """Erstellt das Hauptlayout der GUI."""
        # Hauptcontainer
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Erstelle die verschiedenen Bereiche
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
        
    def _create_plot_section(self):
        """Erstellt den Plot-Konfigurationsbereich."""
        plot_frame = ttk.LabelFrame(self.main_container, text="Plot-Konfiguration")
        plot_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # X-Achsen Auswahl
        x_frame = ttk.Frame(plot_frame)
        x_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(x_frame, text="X-Achse:").pack(side=tk.LEFT)
        self.x_dropdown = ttk.Combobox(x_frame, state="readonly")
        self.x_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Y-Achsen Auswahl
        y_frame = ttk.Frame(plot_frame)
        y_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(y_frame, text="Y-Achse:").pack(side=tk.LEFT)
        self.y_dropdown = ttk.Combobox(y_frame, state="readonly")
        self.y_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Plot-Typ Auswahl
        type_frame = ttk.Frame(plot_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(type_frame, text="Plot-Typ:").pack(side=tk.LEFT)
        self.plot_type_dropdown = ttk.Combobox(
            type_frame,
            state="readonly",
            values=list(self.PLOT_TYPES.keys())
        )
        self.plot_type_dropdown.pack(side=tk.LEFT, padx=5)
        self.plot_type_dropdown.set("Histogram")
        
    def _create_filter_section(self):
        """Erstellt den Filterbereich."""
        filter_frame = ttk.LabelFrame(self.main_container, text="Filter")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filter Spaltenauswahl
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
            filter_op_frame,
            state="readonly",
            values=self.OPERATORS
        )
        self.filter_operator_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Filter Wert
        filter_val_frame = ttk.Frame(filter_frame)
        filter_val_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(filter_val_frame, text="Filterwert:").pack(side=tk.LEFT)
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
        
        # Bedingungen Liste
        self.conditions_listbox = tk.Listbox(filter_frame, height=5)
        self.conditions_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Bedingungen Buttons
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
        
    def _create_action_section(self):
        """Erstellt den Aktionsbereich."""
        action_frame = ttk.Frame(self.main_container)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            action_frame,
            text="Daten plotten",
            command=self.plot_data
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            action_frame,
            text="Grafik exportieren",
            command=self._export_plot
        ).pack(side=tk.LEFT, padx=5)
        
    def load_csv(self):
        """Lädt eine CSV-Datei und verarbeitet sie."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.original_data = pd.read_csv(file_path)
                self._process_data()
                self._update_gui_after_load(file_path)
                messagebox.showinfo("Erfolg", "Datei erfolgreich geladen!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {str(e)}")
                
    def _process_data(self):
        """Verarbeitet die geladenen Daten."""
        if self.original_data is not None:
            # Erstelle Kopie für gefilterte Daten
            self.filtered_data = self.original_data.copy()
            self.filtered_data = self.filtered_data.drop_duplicates()
            self.filtered_data = self.filtered_data.dropna()
            self._convert_datatypes()
            self._cache_data()
            
    def _convert_datatypes(self):
        """Konvertiert Spalten in passende Datentypen."""
        numeric_columns = self.filtered_data.select_dtypes(
            include=['float64', 'int64']
        ).columns
        for col in numeric_columns:
            self.filtered_data[col] = pd.to_numeric(
                self.filtered_data[col], errors='coerce'
            )
                    
    def _cache_data(self):
        """Cached häufig verwendete Berechnungen."""
        if self.filtered_data is not None:
            self.cached_stats = {
                'mean': self.filtered_data.mean(),
                'std': self.filtered_data.std(),
                'count': len(self.filtered_data)
            }
            self._data_hash = hash(str(self.filtered_data))
                
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
            # Reset entry
            self.filter_value_entry.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Fehler", 
                "Bitte Spalte, Operator und Wert auswählen."
            )
                
    def remove_condition(self):
        """Entfernt die ausgewählte Filterbedingung."""
        selected_idx = self.conditions_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            self.conditions_listbox.delete(idx)
            del self.filter_conditions[idx]
        else:
            messagebox.showerror(
                "Fehler", 
                "Keine Bedingung zum Entfernen ausgewählt."
            )
                
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
            self._cache_data()
            messagebox.showinfo(
                "Erfolg", 
                f"Filter angewendet. {len(self.filtered_data)} Zeilen übrig."
            )
        except Exception as e:
            messagebox.showerror(
                "Fehler", 
                f"Fehler beim Anwenden der Filter: {str(e)}"
            )
                
    def plot_data(self):
        """Erstellt den ausgewählten Plot."""
        plot_type = self.plot_type_dropdown.get()
        plot_func = self.PLOT_TYPES.get(plot_type)
        
        if plot_func:
            self._safe_plot(plot_func)
        else:
            messagebox.showerror("Fehler", "Ungültiger Plot-Typ ausgewählt.")
                
    def _safe_plot(self, plot_func: Callable):
        """Führt eine Plot-Funktion sicher aus."""
        try:
            if self._validate_input():
                plot_func()
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
                
    def _validate_input(self) -> bool:
        """Validiert die Eingaben für das Plotting."""
        if self.filtered_data is None or self.filtered_data.empty:
            raise ValueError("Keine Daten zum Plotten verfügbar.")
                
        x_col = self.x_dropdown.get()
        if not x_col:
            raise ValueError("X-Achse muss ausgewählt sein.")
                
        plot_type = self.plot_type_dropdown.get()
        if plot_type in ["2D Histogram", "Scatter"]:
            y_col = self.y_dropdown.get()
            if not y_col:
                raise ValueError("Y-Achse muss für diesen Plot-Typ ausgewählt sein.")
                    
        return True
            
    def _plot_histogram(self):
        """Erstellt ein Histogram."""
        x_col = self.x_dropdown.get()
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.hist(self.filtered_data[x_col], bins='auto', density=False, alpha=0.7)
        plt.xlabel(x_col)
        plt.ylabel('Häufigkeit')
        plt.title(f'Histogram von {x_col}')
        plt.grid(True)
        plt.show()
            
    def _plot_2d_histogram(self):
        """Erstellt ein 2D-Histogram."""
        x_col = self.x_dropdown.get()
        y_col = self.y_dropdown.get()
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.hist2d(
            self.filtered_data[x_col], 
            self.filtered_data[y_col], 
            bins=30, 
            cmap="Blues"
        )
        plt.colorbar(label="Häufigkeit")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f'2D Histogram von {x_col} und {y_col}')
        plt.grid(True)
        plt.show()
        
    def _plot_boxplot(self):
        """Erstellt ein Boxplot."""
        x_col = self.x_dropdown.get()
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.boxplot(self.filtered_data[x_col], vert=False, labels=[x_col])
        plt.xlabel('Wert')
        plt.title(f'Boxplot von {x_col}')
        plt.grid(True)
        plt.show()
        
    def _plot_scatter(self):
        """Erstellt einen Scatterplot."""
        x_col = self.x_dropdown.get()
        y_col = self.y_dropdown.get()
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.scatter(
            self.filtered_data[x_col], 
            self.filtered_data[y_col], 
            alpha=0.7
        )
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f'Scatterplot von {x_col} vs. {y_col}')
        plt.grid(True)
        plt.show()
       
    def _plot_scatter_with_line(self):
        """Erstellt einen Scatterplot mit Linienverbindung."""
        x_col = self.x_dropdown.get()
        y_col = self.y_dropdown.get()
        x_values = self.filtered_data[x_col]
        y_values = self.filtered_data[y_col]
        plt.figure(figsize=self.DEFAULT_FIGSIZE)
        plt.scatter(x_values, y_values, alpha=0.7, label='Datenpunkte')
        plt.plot(x_values, y_values, linestyle='-', color='blue', label='Verbindungslinie')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f'Scatterplot von {x_col} vs. {y_col} mit Verbindungslinie')
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
            
# Hauptprogramm
if __name__ == "__main__":
    root = tk.Tk()
    app = PPGVisualizer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()