#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interfaz gráfica para la detección de neumonía en imágenes radiográficas.
"""

from tkinter import *
from tkinter import ttk, font, filedialog, Entry
import tensorflow as tf
import keras.backend as K
import pydicom as dicom
import csv

from PIL import Image, ImageTk
from tkinter import END, StringVar, Text, Tk
from tkinter import font
from tkinter import filedialog, messagebox, ttk

import tkcap
import img2pdf

from src.data.read_img import read_image
from src.models.integrator import run_pipeline

# Resampling compatible con Pillow 10+
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
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)
        self.root.resizable(True, True)

        font_title = ("Arial", 18, "bold")
        font_sub = ("Arial", 12, "bold")

        # ================= CONFIG GRID =================
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=0)

        # ================= TITULO =================
        titulo = Label(
            self.root,
            text="SOFTWARE PARA EL APOYO AL DIAGNÓSTICO MÉDICO DE NEUMONÍA",
            font=font_title
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=20)

        # ================= FRAME IMÁGENES =================
        frame_imgs = Frame(self.root)
        frame_imgs.grid(row=1, column=0, columnspan=2, sticky="nsew")

        frame_imgs.grid_columnconfigure(0, weight=1)
        frame_imgs.grid_columnconfigure(1, weight=1)

        Label(frame_imgs, text="Imagen Radiográfica", font=font_sub)\
            .grid(row=0, column=0, pady=10)

        Label(frame_imgs, text="Imagen con Heatmap", font=font_sub)\
            .grid(row=0, column=1, pady=10)

        self.text_img1 = Text(frame_imgs, width=45, height=22)
        self.text_img1.grid(row=1, column=0, padx=40, pady=10)

        self.text_img2 = Text(frame_imgs, width=45, height=22)
        self.text_img2.grid(row=1, column=1, padx=40, pady=10)

        # ================= FRAME RESULTADOS =================
        frame_result = Frame(self.root)
        frame_result.grid(row=2, column=0, columnspan=2, pady=20)

        Label(frame_result, text="Cédula Paciente:", font=font_sub)\
            .grid(row=0, column=0, padx=10)

        self.ID = StringVar()
        self.text1 = ttk.Entry(frame_result, textvariable=self.ID, width=20)
        self.text1.grid(row=0, column=1, padx=10)

        Label(frame_result, text="Resultado:", font=font_sub)\
            .grid(row=0, column=2, padx=10)

        self.text2 = Text(frame_result, width=15, height=1)
        self.text2.grid(row=0, column=3, padx=10)

        Label(frame_result, text="Probabilidad:", font=font_sub)\
            .grid(row=0, column=4, padx=10)

        self.text3 = Text(frame_result, width=15, height=1)
        self.text3.grid(row=0, column=5, padx=10)

        # ================= FRAME BOTONES =================
        frame_buttons = Frame(self.root)
        frame_buttons.grid(row=3, column=0, columnspan=2, pady=20)

        self.button2 = ttk.Button(
            frame_buttons, text="Cargar Imagen",
            command=self.load_img_file
        )
        self.button2.grid(row=0, column=0, padx=15)

        self.button1 = ttk.Button(
            frame_buttons, text="Predecir",
            state="disabled",
            command=self.run_model
        )
        self.button1.grid(row=0, column=1, padx=15)

        self.button6 = ttk.Button(
            frame_buttons, text="Guardar",
            command=self.save_results_csv
        )
        self.button6.grid(row=0, column=2, padx=15)

        self.button4 = ttk.Button(
            frame_buttons, text="PDF",
            command=self.create_pdf
        )
        self.button4.grid(row=0, column=3, padx=15)

        self.button3 = ttk.Button(
            frame_buttons, text="Borrar",
            command=self.delete
        )
        self.button3.grid(row=0, column=4, padx=15)

        # ================= VARIABLES =================
        self.array = None
        self.reportID = 0
        self.label = ""
        self.proba = 0.0
        self.img1 = None
        self.img2 = None

        self.root.mainloop()

    # ================= FUNCIONES =================

    def load_img_file(self):
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

        self.img1 = img2show.resize((450, 450), RESAMPLE)
        self.img1 = ImageTk.PhotoImage(self.img1)

        self.text_img1.delete("1.0", "end")
        self.text_img1.image_create(END, image=self.img1)

        self.button1["state"] = "enabled"

    def run_model(self):
        self.label, self.proba, self.heatmap = run_pipeline(self.array)

        self.img2 = Image.fromarray(self.heatmap)
        self.img2 = self.img2.resize((450, 450), RESAMPLE)
        self.img2 = ImageTk.PhotoImage(self.img2)

        self.text_img2.delete("1.0", "end")
        self.text_img2.image_create(END, image=self.img2)
    

        self.text2.delete("1.0", "end")
        self.text2.insert(END, self.label)

        self.text3.delete("1.0", "end")
        self.text3.insert(END, f"{self.proba * 100:.2f}%")

    def save_results_csv(self):
        with open("historial.csv", "a", newline="", encoding="utf-8") as csvfile:
            w = csv.writer(csvfile, delimiter="-")
            w.writerow([
                self.text1.get(),
                self.label,
                f"{self.proba * 100:.2f}%"
            ])

        messagebox.showinfo(
            title="Guardar",
            message="Los datos se guardaron con éxito."
        )

    def create_pdf(self):
        """Captura la ventana con tkcap y guarda como PDF con nombre personalizado."""

        cedula = self.text1.get().strip()

        if not cedula:
            messagebox.showerror(
            title="Error",
            message="Debe ingresar la cédula del paciente antes de generar el PDF."
        )
            return

        nombre_base = f"Resultado paciente CC. {cedula}"

        # Captura imagen
        cap = tkcap.CAP(self.root)
        jpg_name = f"{nombre_base}.jpg"
        cap.capture(jpg_name)

        # Convertir a PDF
        img = Image.open(jpg_name)
        img = img.convert("RGB")

        pdf_name = f"{nombre_base}.pdf"
        img.save(pdf_name)

        messagebox.showinfo(
        title="PDF",
        message=f"El PDF fue generado con éxito:\n{pdf_name}"
        )
        
        def save_results_csv(self):
         """Guarda cédula, resultado y probabilidad en historial.csv."""

        cedula = self.text1.get().strip()

        if not cedula:
            messagebox.showerror(
            title="Error",
            message="Debe ingresar la cédula del paciente antes de guardar."
        )
            return

        with open("historial.csv", "a", newline="", encoding="utf-8") as csvfile:
            w = csv.writer(csvfile, delimiter="-")
            w.writerow([
            cedula,
            self.label,
            f"{self.proba * 100.0:.2f}%"
        ])

        messagebox.showinfo(
        title="Guardar",
        message="Los datos se guardaron con éxito."
    )

    def delete(self):
        answer = messagebox.askokcancel(
            title="Confirmación",
            message="Se borrarán todos los datos.",
            icon=messagebox.WARNING,
        )

        if answer:
            self.text1.delete(0, "end")
            self.text2.delete("1.0", "end")
            self.text3.delete("1.0", "end")
            self.text_img1.delete("1.0", "end")
            self.text_img2.delete("1.0", "end")

            messagebox.showinfo(
                title="Borrar",
                message="Los datos se borraron con éxito."
            )


def main():
    app = App()
    return 0


if __name__ == "__main__":
    main()
