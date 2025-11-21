import sys
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QGroupBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QShortcut,
    QTableWidget,
    QHeaderView,
    QFileDialog,
)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont, QKeySequence, QFontMetrics, QIcon
import json


def apply_theme(app, theme="Jasny"):
    theme_files = {
        "Jasny": "light.qss",
        "Ciemny": "dark.qss",
        "Różowy": "pink.qss",
        "Miętowy": "mietowy.qss",
        "Baby blue": "baby-blue.qss",
        "Jasny zielony": "light-green.qss",
        "Lawendowy": "lawendowy.qss",
    }
    file = theme_files.get(theme, "light.qss")
    with open(file, "r") as f:
        app.setStyleSheet(f.read())


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

        fontmetrics = QFontMetrics(self.font())
        self.setTabStopDistance(fontmetrics.width(" ") * 5)  # Tab = 4 spacje

    def resize_for_content(self):
        doc = self.document()
        if doc is None:
            return
        doc_height = doc.size().height()
        h = max(40, min(int(doc_height) + 12, self.max_height))
        self.setMinimumHeight(h)
        self.updateGeometry()


# Sekcja Ustawień
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Ustawienia")
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()

        # Main Timer
        main_timer_group = QGroupBox("Czas głównego timera")
        main_timer_layout = QHBoxLayout()
        self.main_timer_minutes = QSpinBox()
        self.main_timer_minutes.setRange(0, 99)
        self.main_timer_seconds = QSpinBox()
        self.main_timer_seconds.setRange(0, 59)
        main_timer_layout.addWidget(QLabel("Min:"))
        main_timer_layout.addWidget(self.main_timer_minutes)
        main_timer_layout.addWidget(QLabel("Sek:"))
        main_timer_layout.addWidget(self.main_timer_seconds)
        main_timer_group.setLayout(main_timer_layout)
        layout.addWidget(main_timer_group)

        # Ad Vocem Timer
        ad_timer_group = QGroupBox("Czas mini timera")
        ad_timer_layout = QHBoxLayout()
        self.ad_timer_seconds = QSpinBox()
        self.ad_timer_seconds.setRange(1, 300)  # 5 min
        ad_timer_layout.addWidget(QLabel("Sekundy:"))
        ad_timer_layout.addWidget(self.ad_timer_seconds)
        ad_timer_group.setLayout(ad_timer_layout)
        layout.addWidget(ad_timer_group)

        # Theme select
        theme_group = QGroupBox("Motyw")
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(
            [
                "Jasny",
                "Ciemny",
                "Różowy",
                "Miętowy",
                "Baby blue",
                "Jasny zielony",
                "Lawendowy",
            ]
        )
        theme_layout.addWidget(QLabel("Motyw:"))
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        self.settings = QSettings("OksfordOS", "DebateJudgeApp")
        current_theme = self.settings.value("theme", "Jasny")
        self.theme_combo.setCurrentText(current_theme)

        # Load defaults
        self.settings = QSettings("OksfordOS", "DebateJudgeApp")
        m = int(self.settings.value("main_minutes", 4))
        s = int(self.settings.value("main_seconds", 0))
        ads = int(self.settings.value("ad_seconds", 30))
        self.main_timer_minutes.setValue(m)
        self.main_timer_seconds.setValue(s)
        self.ad_timer_seconds.setValue(ads)

        # Save button
        save_btn = QPushButton("Zapisz i zamknij")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save_settings(self):
        theme = self.theme_combo.currentText()
        self.settings.setValue("theme", theme)
        m = self.main_timer_minutes.value()
        s = self.main_timer_seconds.value()
        ads = self.ad_timer_seconds.value()
        self.settings.setValue("main_minutes", m)
        self.settings.setValue("main_seconds", s)
        self.settings.setValue("ad_seconds", ads)
        self.accept()  # zamyka dialog


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
        self.question2.textChanged.connect(self.show_question2)

        q_layout.addWidget(self.question1)
        q_layout.addWidget(self.question2)
        questions_group.setLayout(q_layout)

        layout.addWidget(questions_group)
        self.setLayout(layout)

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

        # Ad Vocem/mini timer
        self.ad_vocem_timer_label = QLabel("30")
        self.ad_vocem_timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        ad_font = QFont("Arial", 24, QFont.Bold)
        self.ad_vocem_timer_label.setFont(ad_font)
        self.ad_vocem_timer_label.setStyleSheet("color: #555;")

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
        Ctrl+L/H – Sekcja<br>
        Alt+L/H – Mówca<br>
        Ctrl+⏎ – Nowa sekcja<br>
        Ctrl+␣ – Timer<br>
        Alt+␣ – Ad vocem timer<br>
        Ctrl+1-8 – Mówca<br>
        Ctrl+N - Notatnik<br>
        Ctrl+R - Reset timer<br>
        Alt+R - Reset mini timer<br>
        Alt+O - Strona w górę<br>
        Alt+P - Strona w dół<br>
        Ctrl+. - Ustawienia<br>
        </span>
        """)

        shortcuts_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)  # type: ignore
        shortcuts_label.setTextFormat(Qt.RichText)  # type: ignore # HTML
        shortcuts_label.setWordWrap(True)
        layout.addWidget(shortcuts_label)

        self.setLayout(layout)


class DebateJudgeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OksfordOS")
        self.setWindowIcon(QIcon("logo.png"))
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

        self.reset_timer()
        self.reset_ad_timer()
        self.update_timer_label()
        self.update_ad_timer_label()

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_():
            self.reload_theme()

    def reload_theme(self):
        settings = QSettings("OksfordOS", "DebateJudgeApp")
        theme = settings.value("theme", "Jasny")
        apply_theme(QApplication.instance(), theme)
        # Reload timer defaults
        self.reset_timer()
        self.reset_ad_timer()

        # Timer

    def start_timer(self):
        if not self.timer_running:
            self.timer_qt.start(1000)  # Tick co sekunde
            self.timer_running = True

    def pause_timer(self):
        if self.timer_running:
            self.timer_qt.stop()
            self.timer_running = False

    def reset_timer(self, seconds=None):
        if seconds is not None:
            self.timer_seconds_left = seconds
        else:
            settings = QSettings("OksfordOS", "DebateJudgeApp")
            m = int(settings.value("main_minutes", 4))
            s = int(settings.value("main_seconds", 0))
            self.timer_seconds_left = m * 60 + s
        self.pause_timer()
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

    def reset_ad_timer(self, seconds=None):
        if seconds is not None:
            self.ad_timer_seconds_left = seconds
        else:
            settings = QSettings("OksfordOS", "DebateJudgeApp")
            self.ad_timer_seconds_left = int(settings.value("ad_seconds", 30))
        self.pause_ad_timer()
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

        # Timer panel po lewej
        self.timer_panel = TimerPanel()
        self.timer_panel.setFixedWidth(180)

        # Prawy Panel na mówców
        right_container = QWidget()
        right_layout = QVBoxLayout()

        # Grid mówców
        self.speaker_grid = QGridLayout()
        self.speakers = []

        for i in range(4):
            prop = SpeakerSection(i + 1, "Propozycja")
            opp = SpeakerSection(i + 1, "Opozycja")
            self.speakers.append(prop)
            self.speakers.append(opp)
            self.speaker_grid.addWidget(prop, i, 0)
            self.speaker_grid.addWidget(opp, i, 1)

        right_layout.addLayout(self.speaker_grid)

        # Ad vocem: 2x2 grid
        self.ad_vocem_layout = QHBoxLayout()
        self.ad_vocem_1 = AdVocemSection("Ad Vocem Propozycja")
        self.ad_vocem_2 = AdVocemSection("Ad Vocem Opozycja")
        self.ad_vocem_layout.addWidget(self.ad_vocem_1)
        self.ad_vocem_layout.addWidget(self.ad_vocem_2)
        right_layout.addLayout(self.ad_vocem_layout)

        # Notatnik
        self.notatnik_box = AutoResizingTextEdit()
        self.notatnik_box.setPlaceholderText("Notatnik")
        self.notatnik_box.setMinimumHeight(120)
        self.notatnik_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.notatnik_box)

        # Punktacja
        self.scores_group = QGroupBox("Punktacja")
        self.scores_group.setObjectName("scores_group")
        scores_layout = QVBoxLayout()

        speakers_names = [
            "Pro 1",
            "Pro 2",
            "Pro 3",
            "Pro 4",
            "Opo 1",
            "Opo 2",
            "Opo 3",
            "Opo 4",
        ]
        self.scores_table = QTableWidget(1, 8)
        self.scores_table.setHorizontalHeaderLabels(speakers_names)
        self.scores_table.verticalHeader().setVisible(False)  # type: ignore
        header = self.scores_table.horizontalHeader()
        for i in range(self.scores_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)  # type: ignore
        header.setSectionsMovable(False)  # type: ignore
        header.setSectionsClickable(False)  # type: ignore
        header.setStretchLastSection(True)  # type: ignore

        self.scores_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore
        self.scores_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore

        for i in range(8):
            spin = QSpinBox()
            spin.setRange(0, 10)
            spin.setStyleSheet("QSpinBox {font-size: 18px; min-width: 50px;}")
            self.scores_table.setCellWidget(0, i, spin)

        scores_layout.addWidget(self.scores_table)
        self.scores_group.setLayout(scores_layout)
        right_layout.addWidget(self.scores_group)

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
        QShortcut(QKeySequence("Ctrl+n"), self, self.focus_notatnik)
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
        QShortcut(QKeySequence("Ctrl+r"), self, lambda: self.reset_timer())
        # Alt+Space - start/stop Ad-Vocem Timer; Alt+R - reset Ad-Vocem Timer
        QShortcut(QKeySequence("Alt+space"), self, self.toggle_ad_timer)
        QShortcut(QKeySequence("Alt+r"), self, lambda: self.reset_ad_timer())

        # Ustawienia
        QShortcut(QKeySequence("Ctrl+."), self, self.open_settings)
        # Zapis i Wczytywanie plików json
        QShortcut(QKeySequence("Ctrl+S"), self, self.export_current_state)  # Zapis
        QShortcut(QKeySequence("Ctrl+O"), self, self.import_state_from_json)  # Odczyt

        # Przewijanie
        QShortcut(
            QKeySequence("Alt+o"),
            self,
            lambda: self.scroll_area.verticalScrollBar().triggerAction(  # type: ignore
                self.scroll_area.verticalScrollBar().SliderPageStepSub  # type: ignore
            ),
        )
        QShortcut(
            QKeySequence("Alt+p"),
            self,
            lambda: self.scroll_area.verticalScrollBar().triggerAction(  # type: ignore
                self.scroll_area.verticalScrollBar().SliderPageStepAdd  # type: ignore
            ),
        )

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
        focus_wid = QApplication.focusWidget()
        # Speaker fields
        for sp in self.speakers:
            if focus_wid in [sp.info_text, sp.question1, sp.question2]:
                cursor = focus_wid.textCursor()
                cursor.insertText("\n------------------\n")
                focus_wid.setTextCursor(cursor)
                focus_wid.setFocus()
                return
        # Ad vocem
        if hasattr(self, "ad_vocem_1") and focus_wid == self.ad_vocem_1.text_edit:
            cursor = self.ad_vocem_1.text_edit.textCursor()
            cursor.insertText("\n------------------\n")
            self.ad_vocem_1.text_edit.setTextCursor(cursor)
            self.ad_vocem_1.text_edit.setFocus()
            return
        if hasattr(self, "ad_vocem_2") and focus_wid == self.ad_vocem_2.text_edit:
            cursor = self.ad_vocem_2.text_edit.textCursor()
            cursor.insertText("\n------------------\n")
            self.ad_vocem_2.text_edit.setTextCursor(cursor)
            self.ad_vocem_2.text_edit.setFocus()
            return
        # Notatnik
        if hasattr(self, "notatnik_box") and focus_wid == self.notatnik_box:
            cursor = self.notatnik_box.textCursor()
            cursor.insertText("\n------------------\n")
            self.notatnik_box.setTextCursor(cursor)
            self.notatnik_box.setFocus()
            return

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

    def focus_notatnik(self):
        self.notatnik_box.setFocus()
        self.ensure_widget_visible(self.notatnik_box)

    def export_current_state(self, filename=None):
        if filename is None:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Zapisz stan", "", "Pliki JSON (*.json)"
            )
            if not filename:
                return  # anulowano wybór pliku
            if not filename.lower().endswith(".json"):
                filename += ".json"
        data = {
            "speakers": [
                {
                    "info": s.info_text.toPlainText(),
                    "question1": s.question1.toPlainText(),
                    "question2": s.question2.toPlainText(),
                }
                for s in self.speakers
            ],
            "ad_vocem": [
                self.ad_vocem_1.text_edit.toPlainText(),
                self.ad_vocem_2.text_edit.toPlainText(),
            ],
            "notatnik": self.notatnik_box.toPlainText(),
            "punkty": [
                self.scores_table.cellWidget(0, i).value()  # type: ignore
                for i in range(self.scores_table.columnCount())
            ],
        }
        save_session_to_json(filename, data)

    def import_state_from_json(self, filename=None):
        if filename is None:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Otwórz stan", "", "Pliki JSON (*.json)"
            )
            if not filename:
                return  # Anulowano wybór pliku
        data = load_session_from_json(filename)
        for i, s in enumerate(self.speakers):
            s.info_text.setPlainText(data["speakers"][i]["info"])
            s.question1.setPlainText(data["speakers"][i]["question1"])
            s.question2.setPlainText(data["speakers"][i]["question2"])
        self.ad_vocem_1.text_edit.setPlainText(data["ad_vocem"][0])
        self.ad_vocem_2.text_edit.setPlainText(data["ad_vocem"][1])
        self.notatnik_box.setPlainText(data.get("notatnik", ""))
        for i, val in enumerate(data["punkty"]):
            self.scores_table.cellWidget(0, i).setValue(val)  # type: ignore


def save_session_to_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_session_from_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line for line in f if not line.strip().startswith("//")]
        return json.loads("".join(lines))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = QSettings("OksfordOS", "DebateJudgeApp")
    theme = settings.value("theme", "Jasny")
    apply_theme(app, theme)

    window = DebateJudgeApp()
    window.show()
    sys.exit(app.exec_())
