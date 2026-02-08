#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interfaz gráfica para la detección de neumonía en imágenes radiográficas.

Utiliza los módulos read_img, integrator (preprocess, load_model, grad_cam)
para cargar imagen, predecir y mostrar resultado y mapa de calor Grad-CAM.
"""

import csv

from PIL import Image, ImageTk
from tkinter import END, StringVar, Text, Tk, WARNING
from tkinter import font
from tkinter import filedialog, messagebox, ttk

import tkcap
import img2pdf

from read_img import read_image
from integrator import run_pipeline

# Resampling: LANCZOS reemplaza ANTIALIAS (deprecado en Pillow 10+)
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS


class App:
    """
    Aplicación Tkinter para cargar imagen, predecir neumonía y mostrar
    resultado (clase, probabilidad) y heatmap Grad-CAM.
    """

    def __init__(self):
        self.root = Tk()
        self.root.title("Herramienta para la detección rápida de neumonía")
        fonti = font.Font(weight="bold")
        self.root.geometry("815x560")
        self.root.resizable(0, 0)

        self.lab1 = ttk.Label(self.root, text="Imagen Radiográfica", font=fonti)
        self.lab2 = ttk.Label(self.root, text="Imagen con Heatmap", font=fonti)
        self.lab3 = ttk.Label(self.root, text="Resultado:", font=fonti)
        self.lab4 = ttk.Label(self.root, text="Cédula Paciente:", font=fonti)
        self.lab5 = ttk.Label(
            self.root,
            text="SOFTWARE PARA EL APOYO AL DIAGNÓSTICO MÉDICO DE NEUMONÍA",
            font=fonti,
        )
        self.lab6 = ttk.Label(self.root, text="Probabilidad:", font=fonti)

        self.ID = StringVar()
        self.result = StringVar()
        self.text1 = ttk.Entry(self.root, textvariable=self.ID, width=10)
        self.text_img1 = Text(self.root, width=31, height=15)
        self.text_img2 = Text(self.root, width=31, height=15)
        self.text2 = Text(self.root)
        self.text3 = Text(self.root)

        self.button1 = ttk.Button(
            self.root, text="Predecir", state="disabled", command=self.run_model
        )
        self.button2 = ttk.Button(
            self.root, text="Cargar Imagen", command=self.load_img_file
        )
        self.button3 = ttk.Button(self.root, text="Borrar", command=self.delete)
        self.button4 = ttk.Button(self.root, text="PDF", command=self.create_pdf)
        self.button6 = ttk.Button(
            self.root, text="Guardar", command=self.save_results_csv
        )

        self.lab1.place(x=110, y=65)
        self.lab2.place(x=545, y=65)
        self.lab3.place(x=500, y=350)
        self.lab4.place(x=65, y=350)
        self.lab5.place(x=122, y=25)
        self.lab6.place(x=500, y=400)
        self.button1.place(x=220, y=460)
        self.button2.place(x=70, y=460)
        self.button3.place(x=670, y=460)
        self.button4.place(x=520, y=460)
        self.button6.place(x=370, y=460)
        self.text1.place(x=200, y=350)
        self.text2.place(x=610, y=350, width=90, height=30)
        self.text3.place(x=610, y=400, width=90, height=30)
        self.text_img1.place(x=65, y=90)
        self.text_img2.place(x=500, y=90)

        self.text1.focus_set()
        self.array = None
        self.reportID = 0
        self.label = ""
        self.proba = 0.0
        self.img1 = None
        self.img2 = None

        self.root.mainloop()

    def load_img_file(self):
        """
        Abre el diálogo para elegir imagen (DICOM/JPG/PNG) y la muestra.
        Usa read_image para soportar ambos formatos.
        """
        filepath = filedialog.askopenfilename(
            initialdir="/",
            title="Select image",
            filetypes=(
                ("DICOM", "*.dcm"),
                ("JPEG", "*.jpeg"),
                ("jpg files", "*.jpg"),
                ("png files", "*.png"),
            ),
        )
        if not filepath:
            return
        try:
            self.array, img2show = read_image(filepath)
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            return
        self.img1 = img2show.resize((250, 250), RESAMPLE)
        self.img1 = ImageTk.PhotoImage(self.img1)
        self.text_img1.delete("1.0", "end")
        self.text_img1.image_create(END, image=self.img1)
        self.button1["state"] = "enabled"

    def run_model(self):
        """
        Ejecuta el pipeline (integrator): predicción + Grad-CAM.
        Muestra clase, probabilidad y heatmap en la interfaz.
        """
        self.label, self.proba, self.heatmap = run_pipeline(self.array)
        self.img2 = Image.fromarray(self.heatmap)
        self.img2 = self.img2.resize((250, 250), RESAMPLE)
        self.img2 = ImageTk.PhotoImage(self.img2)
        self.text_img2.delete("1.0", "end")
        self.text_img2.image_create(END, image=self.img2)
        self.text2.delete("1.0", "end")
        self.text2.insert(END, self.label)
        proba_pct = self.proba * 100.0
        self.text3.delete("1.0", "end")
        self.text3.insert(END, f"{proba_pct:.2f}%")

    def save_results_csv(self):
        """Guarda cédula, resultado y probabilidad en historial.csv."""
        with open("historial.csv", "a", newline="", encoding="utf-8") as csvfile:
            w = csv.writer(csvfile, delimiter="-")
            w.writerow([
                self.text1.get(),
                self.label,
                f"{self.proba * 100.0:.2f}%",
            ])
        messagebox.showinfo(
            title="Guardar",
            message="Los datos se guardaron con éxito."
        )

    def create_pdf(self):
        """Captura la ventana con tkcap y guarda como PDF."""
        cap = tkcap.CAP(self.root)
        id_name = "Reporte" + str(self.reportID) + ".jpg"
        cap.capture(id_name)
        img = Image.open(id_name)
        img = img.convert("RGB")
        pdf_path = "Reporte" + str(self.reportID) + ".pdf"
        img.save(pdf_path)
        self.reportID += 1
        messagebox.showinfo(
            title="PDF",
            message="El PDF fue generado con éxito."
        )

    def delete(self):
        """Pide confirmación y borra datos e imágenes mostradas."""
        answer = messagebox.askokcancel(
            title="Confirmación",
            message="Se borrarán todos los datos.",
            icon=WARNING,
        )
        if answer:
            self.text1.delete(0, "end")
            self.text2.delete("1.0", "end")
            self.text3.delete("1.0", "end")
            self.text_img1.delete("1.0", "end")
            self.text_img2.delete("1.0", "end")
            messagebox.showinfo(
                title="Borrar",
                message="Los datos se borraron con éxito"
            )


def main():
    """Punto de entrada: crea y ejecuta la aplicación."""
    app = App()
    return 0


if __name__ == "__main__":
    main()
