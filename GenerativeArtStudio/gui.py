# gui.py

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSlider, QPushButton, QComboBox)
from PyQt5.QtCore import Qt

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Generative Art Controls')
        self.layout = QVBoxLayout()

        # Fractal Settings
        self.fractal_label = QLabel('Fractal Type')
        self.fractal_combo = QComboBox()
        self.fractal_combo.addItems(['Mandelbrot', 'Julia'])
        self.layout.addWidget(self.fractal_label)
        self.layout.addWidget(self.fractal_combo)

        # Max Iterations Slider
        self.iter_label = QLabel('Max Iterations')
        self.iter_slider = QSlider(Qt.Horizontal)
        self.iter_slider.setMinimum(50)
        self.iter_slider.setMaximum(500)
        self.iter_slider.setValue(100)
        self.layout.addWidget(self.iter_label)
        self.layout.addWidget(self.iter_slider)

        # Zoom Level Slider
        self.zoom_label = QLabel('Zoom Level')
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(20)
        self.zoom_slider.setValue(1)
        self.layout.addWidget(self.zoom_label)
        self.layout.addWidget(self.zoom_slider)

        # Harmony Selector
        self.harmony_label = QLabel('Color Harmony')
        self.harmony_combo = QComboBox()
        self.harmony_combo.addItems(['Analogous', 'Complementary', 'Triadic', 'Tetradic'])
        self.layout.addWidget(self.harmony_label)
        self.layout.addWidget(self.harmony_combo)

        # Update Button
        self.update_button = QPushButton('Update')
        self.layout.addWidget(self.update_button)

        self.setLayout(self.layout)

    def get_settings(self):
        settings = {
            'fractal_type': self.fractal_combo.currentText(),
            'max_iter': self.iter_slider.value(),
            'zoom': self.zoom_slider.value(),
            'harmony': self.harmony_combo.currentText()
        }
        return settings
