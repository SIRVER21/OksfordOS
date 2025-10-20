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
    QShortcut,
    QFrame,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QKeySequence


class AutoResizingTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TypingFont = QFont("Arial", 11)  # czcionka pisana
        self.setFont(TypingFont)

        self.textChanged.connect(self.resize_for_content)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.setMinimumHeight(40)
        self.max_height = 600  # lub inna sensowna granica

    def focusInEvent(self, event):  # type: ignore
        super().focusInEvent(event)
        self.setStyleSheet(
            "border: 3px solid #1976d2; background: #f8faff; border-radius: 4px;"
        )

    def focusOutEvent(self, event):  # type: ignore
        super().focusOutEvent(event)
        self.setStyleSheet(
            "border: 1px solid #cccccc; background: #ffffff; border-radius: 4px;"
        )

    def resize_for_content(self):
        doc = self.document()
        if doc is None:
            return
        doc_height = doc.size().height()
        h = max(40, min(int(doc_height) + 12, self.max_height))
        self.setMinimumHeight(h)
        self.updateGeometry()


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

        self.info_text = AutoResizingTextEdit()
        self.info_text.setPlaceholderText(
            f"Informacje mówcy {self.speaker_num} {self.side}"
        )
        self.info_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.info_text.setMinimumHeight(40)

        layout.addWidget(self.info_text)

        questions_group = QGroupBox("Pytania")
        q_layout = QVBoxLayout()

        self.question1 = AutoResizingTextEdit()
        self.question1.setPlaceholderText("Pytanie 1")
        self.question1.setMinimumHeight(60)
        self.question1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.question2 = AutoResizingTextEdit()
        self.question2.setPlaceholderText("Pytanie 2")
        self.question2.setMinimumHeight(60)
        self.question2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.question1.setVisible(False)
        self.question2.setVisible(False)

        self.question1.textChanged.connect(self.show_question1)
        self.question2.textChanged.connect(self.show_question2)  # Check

        q_layout.addWidget(self.question1)
        q_layout.addWidget(self.question2)
        questions_group.setLayout(q_layout)

        layout.addWidget(questions_group)
        self.setLayout(layout)

    def create_new_section(self):
        cursor = self.info_text.textCursor()
        cursor.insertText("\n--- Nowa Sekcja ---\n")
        self.info_text.setTextCursor(cursor)
        self.info_text.setFocus()

    def show_question1(self):
        if self.question1.toPlainText().strip():
            self.question1.setVisible(True)

    def show_question2(self):
        if self.question2.toPlainText().strip():
            self.question2.setVisible(True)


class AdVocemSection(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout()
        self.text_edit = AutoResizingTextEdit()
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

        # Main timer
        self.main_timer_label = QLabel("4:00")
        self.main_timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        font = QFont("Arial", 36, QFont.Bold)
        self.main_timer_label.setFont(font)

        # Ad Vocem timer
        self.ad_vocem_timer_label = QLabel("30")
        self.ad_vocem_timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        ad_font = QFont("Arial", 24, QFont.Bold)
        self.ad_vocem_timer_label.setFont(ad_font)
        self.ad_vocem_timer_label.setStyleSheet("color: #555;")  # opcjonalnie

        self.question_timer_label = QLabel("")
        self.question_timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.question_timer_label.setFont(QFont("Arial", 18))

        # layout.addStretch() # To nam daje że timer jest u góry, można zmienić!
        layout.addWidget(self.main_timer_label)
        layout.addWidget(self.ad_vocem_timer_label)
        layout.addWidget(self.question_timer_label)
        layout.addStretch()

        shortcuts_label = QLabel("""
        <span style="color: #9a9a9a; font-size:14px;">
        Ctrl+L/H – sekcja<br>
        Alt+L/H – mówca<br>
        Ctrl+⏎ – nowa sekcja<br>
        Ctrl+␣ – timer<br>
        Alt+␣ – ad vocem timer<br>
        Ctrl+1-8 – mówca
        </span>
        """)

        shortcuts_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        shortcuts_label.setTextFormat(Qt.RichText)  # HTML
        shortcuts_label.setWordWrap(True)
        layout.addWidget(shortcuts_label)

        self.setLayout(layout)


class DebateJudgeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OksfordOS")
        self.setGeometry(100, 100, 1300, 900)

        # Main Timer
        self.timer_running = False
        self.timer_seconds_left = 240  # 4:00

        # Ad vocem Timer
        self.ad_timer_running = False
        self.ad_timer_seconds_left = 30  # 30s

        # Index
        self.current_speaker_index = 0
        self.current_section_index = 0  # 0=info, 1=question1, 2=question2

        # Qtimer
        self.timer_qt = QTimer(self)
        self.timer_qt.timeout.connect(self.update_timer)

        self.ad_timer_qt = QTimer(self)
        self.ad_timer_qt.timeout.connect(self.update_ad_timer)

        self.init_ui()
        self.setup_shortcuts()

        self.update_timer_label()
        self.update_ad_timer_label()

    def start_timer(self):
        if not self.timer_running:
            self.timer_qt.start(1000)  # Tick co sekunde
            self.timer_running = True

    def pause_timer(self):
        if self.timer_running:
            self.timer_qt.stop()
            self.timer_running = False

    def reset_timer(self, seconds=240):
        self.pause_timer()
        self.timer_seconds_left = seconds
        self.update_timer_label()

    def update_timer(self):
        if self.timer_seconds_left > 0:
            self.timer_seconds_left -= 1
            self.update_timer_label()
        else:
            self.pause_timer()
            # Jakieś dźwięki, wizualne efekty tutaj można dodać

    def update_timer_label(self):
        m, s = divmod(self.timer_seconds_left, 60)
        self.timer_panel.main_timer_label.setText(f"{m:02}:{s:02}")

    def start_ad_timer(self):
        if not self.ad_timer_running:
            self.ad_timer_qt.start(1000)  # Tick co sekunde
            self.ad_timer_running = True

    def pause_ad_timer(self):
        if self.ad_timer_running:
            self.ad_timer_qt.stop()
            self.ad_timer_running = False

    def reset_ad_timer(self, seconds=30):
        self.pause_ad_timer()
        self.ad_timer_seconds_left = seconds
        self.update_ad_timer_label()

    def update_ad_timer(self):
        if self.ad_timer_seconds_left > 0:
            self.ad_timer_seconds_left -= 1
            self.update_ad_timer_label()
        else:
            self.pause_ad_timer()
            # Jakieś dźwięki, wizualne efekty tutaj można dodać

    def update_ad_timer_label(self):
        m, s = divmod(self.ad_timer_seconds_left, 60)
        self.timer_panel.ad_vocem_timer_label.setText(f"{m:02}:{s:02}")

    # GUI
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Timer panel on the Left
        self.timer_panel = TimerPanel()
        self.timer_panel.setFixedWidth(180)

        # Right Panel for speakers and ad vocem
        right_container = QWidget()
        right_layout = QVBoxLayout()

        # Speakers grid
        self.speaker_grid = QGridLayout()
        self.speakers = []

        # Grid mówców
        for i in range(4):
            prop = SpeakerSection(i + 1, "Propozycja")
            opp = SpeakerSection(i + 1, "Opozycja")
            self.speakers.append(prop)
            self.speakers.append(opp)
            self.speaker_grid.addWidget(prop, i, 0)
            self.speaker_grid.addWidget(opp, i, 1)

        right_layout.addLayout(self.speaker_grid)

        # Ad vocem section: 2x2 grid beneath speakers
        self.ad_vocem_layout = QHBoxLayout()
        self.ad_vocem_1 = AdVocemSection("Ad Vocem Propozycja")
        self.ad_vocem_2 = AdVocemSection("Ad Vocem Opozycja")
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

    def setup_shortcuts(self):
        # Ctrl+l/h - przejścia pomiędzy sekcjami mówcy
        QShortcut(QKeySequence("Ctrl+l"), self, self.next_section)
        QShortcut(QKeySequence("Ctrl+h"), self, self.previous_section)
        QShortcut(QKeySequence("Alt+l"), self, self.next_speaker)
        QShortcut(QKeySequence("Alt+h"), self, self.previous_speaker)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.create_section)

        # Ctrl+1-8 do przeskoku do mówcy
        for i in range(8):
            QShortcut(
                QKeySequence(f"Ctrl+{i + 1}"),
                self,
                lambda idx=i: self.jump_to_speaker(idx),
            )
        # Alt+A – przejście do Ad Vocem PROPOZYCJA (lewe pole)
        QShortcut(QKeySequence("Alt+a"), self, self.focus_ad_vocem_proposition)
        # Alt+Shift+A – przejście do Ad Vocem OPOZYCJI (prawe pole)
        QShortcut(QKeySequence("Alt+d"), self, self.focus_ad_vocem_opposition)
        # Ctrl+Space - start/stop Main Timer; Ctrl+R - reset Timer
        QShortcut(QKeySequence("Ctrl+space"), self, self.toggle_timer)
        QShortcut(QKeySequence("Ctrl+r"), self, lambda: self.reset_timer(240))
        # Alt+Space - start/stop Ad-Vocem Timer; Alt+R - reset Ad-Vocem Timer
        QShortcut(QKeySequence("Alt+space"), self, self.toggle_ad_timer)
        QShortcut(QKeySequence("Alt+r"), self, lambda: self.reset_ad_timer(30))

    def focus_current_section(self):
        speaker = self.speakers[self.current_speaker_index]
        if self.current_section_index == 0:
            speaker.info_text.setFocus()
            self.ensure_widget_visible(speaker)

        elif self.current_section_index == 1:
            speaker.question1.setVisible(True)
            speaker.question1.setFocus()
            self.ensure_widget_visible(speaker)

        elif self.current_section_index == 2:
            if not speaker.question1.toPlainText().strip():
                self.current_section_index = 1
                speaker.question1.setFocus()
                self.ensure_widget_visible(speaker)
            else:
                speaker.question2.setVisible(True)
                speaker.question2.setFocus()
                self.ensure_widget_visible(speaker)

    def ensure_widget_visible(self, widget):
        rect = widget.geometry()
        self.scroll_area.ensureVisible(rect.x(), rect.y(), rect.width(), rect.height())

    def toggle_timer(self):
        if self.timer_running:
            self.pause_timer()
        else:
            self.start_timer()

    def toggle_ad_timer(self):
        if self.ad_timer_running:
            self.pause_ad_timer()
        else:
            self.start_ad_timer()

    def next_section(self):
        self.current_section_index = (self.current_section_index + 1) % 3
        self.focus_current_section()

    def previous_section(self):
        self.current_section_index = (self.current_section_index - 1) % 3
        self.focus_current_section()

    def next_speaker(self):
        self.current_speaker_index = (self.current_speaker_index + 1) % len(
            self.speakers
        )
        self.current_section_index = 0
        self.focus_current_section()

    def previous_speaker(self):
        self.current_speaker_index = (self.current_speaker_index - 1) % len(
            self.speakers
        )
        self.current_section_index = 0
        self.focus_current_section()

    def create_section(self):
        speaker = self.speakers[self.current_speaker_index]
        if self.current_section_index == 0:
            cursor = speaker.info_text.textCursor()
            cursor.insertText("\n--- Nowa Sekcja ---\n")
            speaker.info_text.setTextCursor(cursor)
            speaker.info_text.setFocus()
        elif self.current_section_index == 1:
            speaker.question1.setVisible(True)
            cursor = speaker.question1.textCursor()
            cursor.insertText("\n--- Nowa Sekcja ---\n")
            speaker.question1.setTextCursor(cursor)
            speaker.question1.setFocus()
        elif self.current_section_index == 2:
            speaker.question2.setVisible(True)
            cursor = speaker.question2.textCursor()
            cursor.insertText("\n--- Nowa Sekcja ---\n")
            speaker.question2.setTextCursor(cursor)
            speaker.question2.setFocus()

    def jump_to_speaker(self, idx):
        self.current_speaker_index = idx
        self.current_section_index = 0
        self.focus_current_section()
        self.ensure_widget_visible(self.speakers[idx])

    def focus_ad_vocem_proposition(self):
        self.ad_vocem_1.text_edit.setFocus()
        self.ensure_widget_visible(self.ad_vocem_1)

    def focus_ad_vocem_opposition(self):
        self.ad_vocem_2.text_edit.setFocus()
        self.ensure_widget_visible((self.ad_vocem_2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebateJudgeApp()
    window.show()
    sys.exit(app.exec_())
