#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interfaz gráfica para detección de neumonía en radiografías de tórax.

Este módulo implementa la ventana principal de la aplicación usando PySide6,
permitiendo cargar imágenes DICOM/JPG/PNG, ejecutar predicciones con el modelo
y mostrar resultados junto con heatmaps de Grad-CAM. También permite guardar
resultados en CSV y exportar reportes en PDF.

"""
import csv
import os
import img2pdf
import cv2
from src.data.read_img import read_image
from src.models.display_labels import get_display_label
from src.models.integrator import run_pipeline
from PIL import Image, ImageDraw, ImageFont

# OpenCV puede inyectar rutas de plugins Qt incompatibles con PySide6.
# Se limpian para forzar el uso de plugins Qt propios de PySide6.
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
os.environ.pop("QT_PLUGIN_PATH", None)
os.environ.setdefault("QT_XCB_NO_XI2", "1")
os.environ.setdefault("QT_X11_NO_MITSHM", "1")
os.environ.setdefault("QT_OPENGL", "software")
os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
os.environ.setdefault("LIBGL_ALWAYS_INDIRECT", "1")
os.environ.setdefault("NO_AT_BRIDGE", "1")

from PySide6.QtCore import Qt, QRegularExpression, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

# Tamaño de vista de imágenes
IMAGE_DISPLAY_SIZE = 480

# Tamaño mínimo del recuadro cuando no hay imagen (placeholder).
IMAGE_PLACEHOLDER_MIN_SIZE = 200


def pil_to_qpixmap(
    pil_image: Image.Image,
    size: int = IMAGE_DISPLAY_SIZE,
) -> QPixmap:
    """
    Convierte una imagen PIL a QPixmap escalado manteniendo relación de aspecto.

    Args:
        pil_image: Imagen en formato PIL.
        size: Longitud máxima del lado para el escalado (por defecto 480).

    Returns:
        QPixmap escalado para mostrar en la interfaz.
    """
    w, h = pil_image.width, pil_image.height
    if pil_image.mode == "RGBA":
        fmt = QImage.Format_RGBA8888
        fmt = QImage.Format_RGBA8888
        bpl = w * 4
        mode = "RGBA"
    else:
        pil_image = pil_image.convert("RGB")
        fmt = QImage.Format_RGB888
        bpl = w * 3
        mode = "RGB"
    data = pil_image.tobytes("raw", mode)
    qimg = QImage(data, w, h, bpl, fmt)
    pix = QPixmap.fromImage(qimg)
    return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def numpy_rgb_to_qpixmap(arr, size: int = IMAGE_DISPLAY_SIZE) -> QPixmap:
    """Convierte array numpy RGB (H, W, 3) uint8 a QPixmap escalado."""
    h, w = arr.shape[:2]
    if arr.ndim == 2:
        arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
    bytes_per_line = w * 3
    qimg = QImage(arr.data, w, h, bytes_per_line, QImage.Format_RGB888)
    pix = QPixmap.fromImage(qimg)
    return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def _apply_pixmap_to_label(label_widget: QLabel, pix: QPixmap) -> None:
    """
    Muestra un QPixmap en un QLabel y ajusta el tamaño mínimo al de la imagen.

    Args:
        label_widget: QLabel donde se mostrará la imagen.
        pix: QPixmap a mostrar.
    """
    label_widget.setPixmap(pix)
    label_widget.setText("")
    label_widget.setMinimumSize(pix.width(), pix.height())


def _clear_image_label(
    label_widget: QLabel,
    placeholder_text: str,
) -> None:
    """
    Limpia la imagen del QLabel y muestra un texto placeholder.

    Args:
        label_widget: QLabel a limpiar.
        placeholder_text: Texto a mostrar en lugar de la imagen.
    """
    label_widget.setPixmap(QPixmap())
    label_widget.setText(placeholder_text)
    label_widget.setMinimumSize(IMAGE_PLACEHOLDER_MIN_SIZE, IMAGE_PLACEHOLDER_MIN_SIZE)


# Estilo moderno y limpio (tema claro profesional)
STYLESHEET = """
QMainWindow {
    background-color: #f5f6f8;
}
QWidget#central {
    background-color: #f5f6f8;
}
QLabel#titleLabel {
    color: #1a237e;
    font-size: 22px;
    font-weight: bold;
    padding: 12px 0;
}
QLabel#sectionLabel {
    color: #37474f;
    font-size: 15px;
    font-weight: bold;
    padding: 6px 0;
}
QFrame#card {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    padding: 16px;
}
QLineEdit {
    padding: 10px 12px;
    border: 1px solid #cfd8dc;
    border-radius: 6px;
    background-color: #fff;
    font-size: 14px;
    min-width: 220px;
}
QLineEdit#cedulaEdit {
    color: #1565c0;
    font-weight: bold;
}
QLabel#resultLabel {
    font-size: 15px;
    font-weight: bold;
    color: #1b5e20;
    padding: 8px 12px;
    background-color: #e8f5e9;
    border-radius: 6px;
    min-width: 120px;
}
QLabel#probLabel {
    font-size: 14px;
    font-weight: bold;
    color: #0d47a1;
    padding: 8px 12px;
    background-color: #e3f2fd;
    border-radius: 6px;
    min-width: 110px;
}
QPushButton {
    padding: 12px 22px;
    border-radius: 8px;
    font-size: 15px;
    font-weight: bold;
    border: none;
    min-width: 100px;
}
QPushButton#primary {
    background-color: #3949ab;
    color: white;
}
QPushButton#primary:hover {
    background-color: #303f9f;
}
QPushButton#primary:disabled {
    background-color: #c5cae9;
    color: #757575;
}
QPushButton#secondary {
    background-color: #eceff1;
    color: #37474f;
}
QPushButton#secondary:hover {
    background-color: #cfd8dc;
}
QPushButton#success {
    background-color: #43a047;
    color: white;
}
QPushButton#success:hover {
    background-color: #388e3c;
}
QPushButton#danger {
    background-color: #e53935;
    color: white;
}
QPushButton#danger:hover {
    background-color: #c62828;
}
QLabel#imagePlaceholder {
    background-color: #eceff1;
    border: 2px dashed #b0bec5;
    border-radius: 8px;
    color: #78909c;
    font-size: 14px;
}
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #e0e0e0;
    text-align: center;
    height: 8px;
}
QProgressBar::chunk {
    background-color: #3949ab;
    border-radius: 4px;
}
"""


class PredictionWorker(QThread):
    """
    Worker en segundo plano para ejecutar el pipeline de predicción.

    Evita bloquear la interfaz mientras se ejecuta el modelo.
    """

    finished = Signal(str, float, object)  # label, proba, heatmap_array
    error = Signal(str)

    def __init__(self, array):
        """
        Inicializa el worker con el array de imagen a procesar.

        Args:
            array: Array numpy de la imagen (salida de read_image).
        """
        super().__init__()
        self.array = array

    def run(self):
        """Ejecuta run_pipeline en el hilo secundario."""
        try:
            label, proba, heatmap = run_pipeline(self.array)
            self.finished.emit(label, proba, heatmap)
        except Exception as e:
            self.error.emit(str(e))


class DetectorWindow(QMainWindow):
    """Ventana principal de la aplicación de detección de neumonía."""

    PLACEHOLDER_ORIGINAL = 'Clic en "Cargar radiografía" para iniciar'
    PLACEHOLDER_HEATMAP = "Aquí verás el heatmap después de predecir"

    def __init__(self):
        """Inicializa la ventana, componentes y estado inicial."""
        super().__init__()
        self.array = None
        self.label = ""
        self.proba = 0.0
        self.heatmap_array = None
        self.report_id = 0
        self._worker = None
        self.setWindowTitle("Apoyo al diagnóstico médico de neumonía")
        self.setMinimumSize(1200, 800)
        self.resize(1280, 860)
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 20, 24, 24)

        # Título
        title = QLabel("Software para el apoyo al diagnóstico médico de neumonía")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Panel de imágenes (dos columnas)
        images_frame = QFrame()
        images_frame.setObjectName("card")
        images_layout = QGridLayout(images_frame)

        lbl_orig = QLabel("Radiografía")
        lbl_orig.setObjectName("sectionLabel")
        lbl_heat = QLabel("Imagen con heatmap Grad-CAM")
        lbl_heat.setObjectName("sectionLabel")

        self.img_original = QLabel()
        self.img_original.setObjectName("imagePlaceholder")
        self.img_original.setAlignment(Qt.AlignCenter)
        self.img_original.setMinimumSize(
            IMAGE_PLACEHOLDER_MIN_SIZE, IMAGE_PLACEHOLDER_MIN_SIZE
        )
        self.img_original.setText(self.PLACEHOLDER_ORIGINAL)
        self.img_original.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.img_heatmap = QLabel()
        self.img_heatmap.setObjectName("imagePlaceholder")
        self.img_heatmap.setAlignment(Qt.AlignCenter)
        self.img_heatmap.setMinimumSize(
            IMAGE_PLACEHOLDER_MIN_SIZE,
            IMAGE_PLACEHOLDER_MIN_SIZE,
        )
        self.img_heatmap.setText(self.PLACEHOLDER_HEATMAP)
        self.img_heatmap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        images_layout.addWidget(lbl_orig, 0, 0)
        images_layout.addWidget(lbl_heat, 0, 1)
        images_layout.addWidget(self.img_original, 1, 0)
        images_layout.addWidget(self.img_heatmap, 1, 1)

        layout.addWidget(images_frame)

        # Barra de progreso (oculta por defecto)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)  # modo indeterminado
        layout.addWidget(self.progress)

        # Panel de resultados
        result_frame = QFrame()
        result_frame.setObjectName("card")
        result_layout = QHBoxLayout(result_frame)
        result_layout.setSpacing(24)

        result_layout.addWidget(QLabel("Cédula paciente:"))
        self.cedula_edit = QLineEdit()
        self.cedula_edit.setObjectName("cedulaEdit")
        self.cedula_edit.setPlaceholderText("Solo números (ej: 12345678)")
        self.cedula_edit.setMaxLength(15)
        only_digits = QRegularExpression(r"^\d{0,15}$")
        self.cedula_edit.setValidator(QRegularExpressionValidator(only_digits, self))
        result_layout.addWidget(self.cedula_edit)

        result_layout.addWidget(QLabel("Resultado:"))
        self.result_label = QLabel("—")
        self.result_label.setObjectName("resultLabel")
        result_layout.addWidget(self.result_label)

        result_layout.addWidget(QLabel("Probabilidad:"))
        self.prob_label = QLabel("—")
        self.prob_label.setObjectName("probLabel")
        result_layout.addWidget(self.prob_label)

        result_layout.addStretch()
        layout.addWidget(result_frame)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_load = QPushButton("Cargar radiografía")
        self.btn_load.setObjectName("secondary")
        self.btn_load.clicked.connect(self.load_image)
        btn_layout.addWidget(self.btn_load)

        self.btn_predict = QPushButton("Predecir")
        self.btn_predict.setObjectName("primary")
        self.btn_predict.setEnabled(False)
        self.btn_predict.clicked.connect(self.run_prediction)
        btn_layout.addWidget(self.btn_predict)

        self.btn_save = QPushButton("Guardar resultado")
        self.btn_save.setObjectName("success")
        self.btn_save.clicked.connect(self.save_results_csv)
        btn_layout.addWidget(self.btn_save)

        self.btn_pdf = QPushButton("Exportar PDF")
        self.btn_pdf.setObjectName("secondary")
        self.btn_pdf.clicked.connect(self.export_pdf)
        btn_layout.addWidget(self.btn_pdf)

        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.setObjectName("danger")
        self.btn_clear.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.btn_clear)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setStyleSheet(STYLESHEET)

    def load_image(self):
        """Abre un diálogo para seleccionar y cargar una imagen de radiografía."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen",
            "",
            "Imágenes (*.dcm *.jpg *.jpeg *.png);;DICOM (*.dcm);;"
            "JPEG (*.jpg *.jpeg);;PNG (*.png)",
        )
        if not path:
            return
        try:
            self.array, img2show = read_image(path)
        except (FileNotFoundError, ValueError) as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        pix = pil_to_qpixmap(img2show)
        _apply_pixmap_to_label(self.img_original, pix)
        _clear_image_label(self.img_heatmap, self.PLACEHOLDER_HEATMAP)
        self.result_label.setText("—")
        self.prob_label.setText("—")
        self.heatmap_array = None
        self.btn_predict.setEnabled(True)

    def run_prediction(self):
        """Ejecuta la predicción en segundo plano usando PredictionWorker."""
        if self.array is None:
            return
        self.btn_predict.setEnabled(False)
        self.progress.setVisible(True)
        self._worker = PredictionWorker(self.array)
        self._worker.finished.connect(self._on_prediction_finished)
        self._worker.error.connect(self._on_prediction_error)
        self._worker.start()

    def _on_prediction_finished(self, label: str, proba: float, heatmap):
        self.progress.setVisible(False)
        self.btn_predict.setEnabled(True)
        self.label = label
        self.proba = proba
        self.heatmap_array = heatmap
        self.result_label.setText(get_display_label(label))
        self.prob_label.setText(f"{proba * 100:.2f}%")
        pix = numpy_rgb_to_qpixmap(heatmap)
        _apply_pixmap_to_label(self.img_heatmap, pix)

    def _on_prediction_error(self, msg: str):
        self.progress.setVisible(False)
        self.btn_predict.setEnabled(True)
        QMessageBox.critical(self, "Error en la predicción", msg)

    def save_results_csv(self):
        """Guarda los resultados en CSV."""
        cedula = self.cedula_edit.text().strip()
        if not cedula:
            QMessageBox.warning(
                self,
                "Cédula requerida",
                "Debe ingresar la cédula del paciente antes de guardar.",
            )
            return
        history_dir = os.path.join("reports", "history")
        os.makedirs(history_dir, exist_ok=True)
        csv_path = os.path.join(history_dir, "historial.csv")
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="-")
            w.writerow(
                [
                    "Paciente:CC." + cedula + " ",
                    " Diagnostíco: " + self.label + " ",
                    f" {self.proba  * 100:.2f}%",
                ]
            )
        QMessageBox.information(self, "Guardar", "Los datos se guardaron con éxito.")

    def export_pdf(self):
        """
        Exporta un reporte en PDF con la imagen original, heatmap y resultados.

        Requiere que se haya ingresado la cédula y que se haya ejecutado una predicción.
        """
        cedula = self.cedula_edit.text().strip()
        if not cedula:
            QMessageBox.warning(
                self,
                "Cédula requerida",
                "Debe ingresar la cédula del paciente antes de generar el PDF.",
            )
            return
        if self.heatmap_array is None:
            QMessageBox.warning(
                self,
                "Sin resultado",
                "Ejecute una predicción antes de exportar el PDF.",
            )
            return
        try:
            pdf_path = self._build_pdf(cedula)
            QMessageBox.information(
                self,
                "PDF generado",
                f"El PDF fue guardado correctamente:\n{pdf_path}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", str(e))

    def clear_all(self):
        """
        Limpia toda la información y restablece el estado inicial de la interfaz.

        Pide confirmación antes de borrar los datos.
        """
        ok = QMessageBox.question(
            self,
            "Confirmar",
            "¿Borrar todos los datos e imágenes mostradas?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ok != QMessageBox.Yes:
            return
        self.array = None
        self.label = ""
        self.proba = 0.0
        self.heatmap_array = None
        _clear_image_label(self.img_original, self.PLACEHOLDER_ORIGINAL)
        _clear_image_label(self.img_heatmap, self.PLACEHOLDER_HEATMAP)
        self.result_label.setText("—")
        self.prob_label.setText("—")
        self.cedula_edit.clear()
        self.btn_predict.setEnabled(False)
        QMessageBox.information(self, "Listo", "Se limpió la pantalla correctamente.")

    def _build_pdf(self, cedula: str) -> str:
        """Genera un PDF con imagen original, heatmap y datos (sin captura de pantalla)."""
        base_name = f"Resultado paciente CC. {cedula}"

        # Crear directorios para JPG y PDF
        jpg_dir = os.path.join("reports", "jpg")
        pdf_dir = os.path.join("reports", "pdf")
        os.makedirs(jpg_dir, exist_ok=True)
        os.makedirs(pdf_dir, exist_ok=True)

        jpg_path = os.path.join(jpg_dir, f"{base_name}.jpg")
        pdf_path = os.path.join(pdf_dir, f"{base_name}.pdf")

        # Imagen original desde self.array (para DICOM es RGB; para JPG puede ser BGR)
        if self.array is not None:
            if self.array.ndim == 2:
                orig_pil = Image.fromarray(self.array)
            else:
                arr = self.array[:, :, :3] if self.array.shape[2] >= 3 else self.array
                orig_pil = Image.fromarray(arr)
        else:
            orig_pil = Image.new("RGB", (512, 512), (240, 240, 240))

        if self.heatmap_array is not None:
            heat_pil = Image.fromarray(self.heatmap_array)
        else:
            heat_pil = Image.new("RGB", (512, 512), (240, 240, 240))

        # Redimensionar para el reporte
        w, h = 400, 400
        orig_pil = orig_pil.resize((w, h), Image.Resampling.LANCZOS)
        heat_pil = heat_pil.resize((w, h), Image.Resampling.LANCZOS)

        # Componer una sola imagen: título + datos + dos imágenes lado a lado
        header_h = 80
        gap = 20
        total_w = w * 2 + gap * 3
        total_h = header_h + h + gap * 2
        report = Image.new("RGB", (total_w, total_h), (255, 255, 255))
        draw = ImageDraw.Draw(report)

        try:
            font_large = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except OSError:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        draw.text((gap, 20), f"Reporte - CC. {cedula}", fill=(0, 0, 0), font=font_large)
        draw.text(
            (gap, 50),
            f"Resultado: {self.label}  |  Probabilidad: {self.proba * 100:.2f}%",
            fill=(60, 60, 60),
            font=font_small,
        )

        report.paste(orig_pil, (gap, header_h + gap))
        report.paste(heat_pil, (w + gap * 2, header_h + gap))

        report.save(jpg_path, "JPEG", quality=92)
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(jpg_path))
        return pdf_path


def main():
    """Punto de partida para el inicio de la GUI."""
    app = QApplication([])
    app.setApplicationName("Apoyo al diagnóstico médico de neumonía")
    win = DetectorWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
