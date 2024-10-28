import sys
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer

class WebcamDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Webcam Capture")
        self.setGeometry(100, 100, 640, 480)
        
        # Webcam feed display label
        self.webcam_label = QLabel(self)
        self.webcam_label.setAlignment(Qt.AlignCenter)
        
        # Capture button
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_image)

        layout = QVBoxLayout()
        layout.addWidget(self.webcam_label)
        layout.addWidget(self.capture_button)
        self.setLayout(layout)

        # Video capture and timer
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms for a smooth video feed
        
        # Placeholder for the captured image
        self.captured_image = None

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            self.display_frame(frame)

    def display_frame(self, frame):
        """ Convert and display the current frame in webcam_label """
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.webcam_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.webcam_label.width(), self.webcam_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def capture_image(self):
        """ Capture the current frame and close the dialog """
        ret, frame = self.capture.read()
        if ret:
            self.captured_image = frame  # Save the captured frame
            self.accept()  # Close the dialog with an accepted status

    def closeEvent(self, event):
        """ Stop the video feed and release the camera when closing the dialog """
        self.timer.stop()
        self.capture.release()
        event.accept()

class ImageFilterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Filtering App")
        self.setGeometry(100, 100, 800, 600)
        self.setAcceptDrops(True)  # Enable drag-and-drop functionality

        # Create labels for original and filtered images
        self.original_image_label = QLabel(self)
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setText("Drop Image Here - or - Click to Upload")
        self.original_image_label.setStyleSheet("border: 2px dashed #aaa; padding: 10px;")
        
        self.filtered_image_label = QLabel(self)
        self.filtered_image_label.setAlignment(Qt.AlignCenter)
        self.filtered_image_label.setText("Filtered Image Will Appear Here")
        self.filtered_image_label.setStyleSheet("border: 2px dashed #aaa; padding: 10px;")

        # Create filter selection combo box
        self.filter_combo = QComboBox(self)
        self.filter_combo.addItems(["Select Filter", "Gaussian Blur", "Edge Detection", "Grayscale", 
                                    "Horizontal Mirror", "Vertical Mirror", "Increase Red", "Increase Green", 
                                    "Increase Blue", "Increase Yellow", "Retro Sepia", "Increase Brightness", 
                                    "Decrease Brightness", "Add Noise", "Sharpen", "Emboss", "Pencil Sketch"])

        # Buttons
        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.clicked.connect(self.load_image)
        
        self.webcam_button = QPushButton("Capture from Webcam", self)
        self.webcam_button.clicked.connect(self.open_webcam_dialog)
        
        self.execute_button = QPushButton("Execute", self)
        self.execute_button.clicked.connect(self.apply_filter)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.filter_combo)
        
        # Create horizontal layout for image frames
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.original_image_label)
        image_layout.addWidget(self.filtered_image_label)
        
        layout.addLayout(image_layout)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.webcam_button)
        layout.addWidget(self.execute_button)
        self.setLayout(layout)

        # Placeholder for the original image
        self.original_image = None

    def open_webcam_dialog(self):
        """ Open the WebcamDialog and capture an image """
        webcam_dialog = WebcamDialog()
        if webcam_dialog.exec_() == QDialog.Accepted and webcam_dialog.captured_image is not None:
            self.original_image = webcam_dialog.captured_image  # Save captured image
            self.display_image(self.original_image, self.original_image_label)  # Display in original image frame
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.load_image(file_path)
    
    def load_image(self):
        # Open the file dialog with `DontUseNativeDialog` to ensure compatibility
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)", options=QFileDialog.DontUseNativeDialog)
    
        # Load and display the image if a valid file path is selected
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.display_image(self.original_image, self.original_image_label)
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Image", "Could not load the image. Please try another file.")


    def display_image(self, image, label):
        """ Display an image on the specified label """
        label_width = label.width()
        label_height = label.height()
        image_height, image_width = image.shape[:2]

        # Calculate scaling factor
        scale_factor = min(label_width / image_width, label_height / image_height)
        if scale_factor < 1:
            new_width = int(image_width * scale_factor)
            new_height = int(image_height * scale_factor)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def apply_filter(self):
        if self.original_image is None:
            QtWidgets.QMessageBox.warning(self, "No Image", "Please load an image first!")
            return

        filter_name = self.filter_combo.currentText()
        if filter_name == "Select Filter":
            QtWidgets.QMessageBox.warning(self, "No Filter Selected", "Please select a filter!")
            return

        filtered_image = self.original_image.copy()

        # Apply selected filter based on filter_name
        if filter_name == "Gaussian Blur":
            filtered_image = cv2.GaussianBlur(filtered_image, (15, 15), 0)
        elif filter_name == "Edge Detection":
            gray_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)
            filtered_image = cv2.Canny(gray_image, 100, 200)
            filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
        elif filter_name == "Grayscale":
            filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)
            filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
        elif filter_name == "Horizontal Mirror":
            filtered_image = cv2.flip(self.original_image, 1)
        elif filter_name == "Vertical Mirror":
            filtered_image = cv2.flip(self.original_image, 0)
        elif filter_name == "Increase Red":
            filtered_image[:, :, 2] = cv2.add(filtered_image[:, :, 2], 50)
        elif filter_name == "Increase Green":
            filtered_image[:, :, 1] = cv2.add(filtered_image[:, :, 1], 50)
        elif filter_name == "Increase Blue":
            filtered_image[:, :, 0] = cv2.add(filtered_image[:, :, 0], 50)
        elif filter_name == "Increase Yellow":
            filtered_image[:, :, 1] = cv2.add(filtered_image[:, :, 1], 50)
            filtered_image[:, :, 2] = cv2.add(filtered_image[:, :, 2], 50)
        elif filter_name == "Retro Sepia":
            sepia_filter = np.array([[0.272, 0.534, 0.131],
                                    [0.349, 0.686, 0.168],
                                    [0.393, 0.769, 0.189]])
            filtered_image = cv2.transform(filtered_image, sepia_filter)
            filtered_image = np.clip(filtered_image, 0, 255)
        elif filter_name == "Increase Brightness":
            filtered_image = cv2.convertScaleAbs(filtered_image, alpha=1, beta=50)
        elif filter_name == "Decrease Brightness":
            filtered_image = cv2.convertScaleAbs(filtered_image, alpha=1, beta=-50)
        elif filter_name == "Add Noise":
            noise = np.random.normal(0, 25, filtered_image.shape).astype(np.uint8)
            filtered_image = cv2.add(filtered_image, noise)
        elif filter_name == "Sharpen":
            kernel = np.array([[0, -1, 0],
                            [-1, 5, -1],
                            [0, -1, 0]])
            filtered_image = cv2.filter2D(filtered_image, -1, kernel)
        elif filter_name == "Emboss":
            kernel = np.array([[-2, -1, 0],
                            [-1, 1, 1],
                            [0, 1, 2]])
            filtered_image = cv2.filter2D(filtered_image, -1, kernel)
        elif filter_name == "Pencil Sketch":
            gray_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)
            inverted_image = cv2.bitwise_not(gray_image)
            blurred = cv2.GaussianBlur(inverted_image, (21, 21), 0)
            inverted_blur = cv2.bitwise_not(blurred)
            filtered_image = cv2.divide(gray_image, inverted_blur, scale=256.0)
            filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)

        self.display_image(filtered_image, self.filtered_image_label)


app = QApplication(sys.argv)
window = ImageFilterApp()
window.show()
sys.exit(app.exec_())
