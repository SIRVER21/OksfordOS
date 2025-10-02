import sys
from PyQt5.QtWidgets import (
    QApplication,
    QGroupBox,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SpeakerSection(QWidget):
    def __init__(self, speaker_num, side):
        super().__init__()
        self.speaker_num = speaker_num
        self.side = side
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel(f"Mówca {self.speaker_num} ({self.side})")
        header.setAlignment(Qt.AlignCenter)  # type: ignore
        header_font = QFont("Arial", 14, QFont.Bold)
        header.setFont(header_font)
        layout.addWidget(header)

        self.info_text = QTextEdit()
        self.info_text.setPlaceholderText(
            f"Informacje mówcy {self.speaker_num} {self.side}"
        )
        self.info_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.info_text.setMinimumHeight(100)

        layout.addWidget(self.info_text)

        questions_group = QGroupBox("Pytania")
        q_layout = QVBoxLayout()

        self.question1 = QTextEdit()
        self.question1.setPlaceholderText("Pytanie 1")
        self.question1.setMinimumHeight(60)
        self.question1.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.MinimumExpanding
        )

        self.question2 = QTextEdit()
        self.question2.setPlaceholderText("Pytanie 2")
        self.question2.setMinimumHeight(60)
        self.question2.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.MinimumExpanding
        )

        q_layout.addWidget(self.question1)
        q_layout.addWidget(self.question2)
        questions_group.setLayout(q_layout)

        self.setLayout(layout)


class AdVocemSection(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(title)
        self.text_edit.setMinimumHeight(120)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)


class TimerPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.main_timer_label = QLabel("05:00")
        self.main_timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        font = QFont("Arial", 36, QFont.Bold)
        self.main_timer_label.setFont(font)

        self.question_timer_label = QLabel("")
        self.question_timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.question_timer_label.setFont(QFont("Arial", 18))

        layout.addStretch()
        layout.addWidget(self.main_timer_label)
        layout.addWidget(self.question_timer_label)
        layout.addStretch()
        self.setLayout(layout)


class DebateJudgeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sędzia Debat Oksfordzkich")
        self.setGeometry(100, 100, 1300, 900)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Timer panel on the Left
        self.timer_panel = TimerPanel()
        self.timer_panel.setFixedWidth(
            250
        )  # wydaje mi się że to może odpowiadać za błąd z niezmieszczeniem licznika

        # Right Panel for speakers and ad vocem
        right_container = QWidget()
        right_layout = QVBoxLayout()

        # Speakers grid: 8 speakers in vertical order, each one row
        self.speaker_grid = QGridLayout()
        self.speakers = []

        # Grid mówców
        for i in range(4):
            prop = SpeakerSection(i + 1, "Propozycja")
            opp = SpeakerSection(i + 1, "Opozycja")
            self.speakers.append(prop)
            self.speakers.append(opp)
            self.speaker_grid.addWidget(prop, i, 0)
            self.speaker_grid.addWidget(prop, i, 1)

        right_layout.addLayout(self.speaker_grid)

        # Ad vocem section: 2x2 grid beneath speakers
        self.ad_vocem_layout = QHBoxLayout()
        self.ad_vocem_1 = AdVocemSection("Ad Vocem Propozycja 1")
        self.ad_vocem_2 = AdVocemSection("Ad Vocem Opozycja 2")
        self.ad_vocem_layout.addWidget(self.ad_vocem_1)
        self.ad_vocem_layout.addWidget(self.ad_vocem_2)

        right_layout.addLayout(self.ad_vocem_layout)

        right_container.setLayout(right_layout)

        # Right side scrollable
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(right_container)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(self.timer_panel)
        main_layout.addWidget(self.scroll_area)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebateJudgeApp()
    window.show()
    sys.exit(app.exec_())
