from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCalendarWidget
from PySide6.QtCore import Qt, QDate, QLocale
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import QToolButton

class _M3Calendar(QCalendarWidget):
    """Custom painted calendar to achieve modern calendar look matching the reference design.
    - Draw filled circles for selected dates
    - Draw outline circle for today
    - Better spacing and typography
    """
    def __init__(self, parent=None, accent: QColor | None = None):
        super().__init__(parent)
        self._accent = QColor("#6E56CF") if accent is None else accent
        self._today_color = QColor("#1D1B20")  # Dark outline for today
        # Let layout determine size; minimum size for comfortable cells
        self.setMinimumSize(260, 220)
        
    def paintCell(self, painter: QPainter, rect, date: QDate):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        is_selected = (date == self.selectedDate())
        is_today = (date == QDate.currentDate())
        in_current_month = (date.month() == self.monthShown() and date.year() == self.yearShown())

        # Base text color
        text_color = QColor("#1D1B20") if in_current_month else QColor("#9E9E9E")
        
        # Calculate circle properties with better spacing
        cell_size = min(rect.width(), rect.height())
        circle_diameter = cell_size - 8  # More padding for cleaner look
        circle_rect = rect.adjusted((rect.width()-circle_diameter)//2, (rect.height()-circle_diameter)//2,
                                    -(rect.width()-circle_diameter)//2, -(rect.height()-circle_diameter)//2)

        # Selection: filled circular background
        if is_selected:
            painter.setBrush(self._accent)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(circle_rect)
            text_color = QColor("#FFFFFF")
        # Today indicator: outline circle (only if not selected)
        elif is_today and in_current_month:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(self._today_color, 2))  # 2px outline
            painter.drawEllipse(circle_rect)

        # Draw the day number with better typography
        font = painter.font()
        font.setPointSize(13)  # Slightly larger for better readability
        font.setWeight(QFont.Weight.Medium if is_selected or is_today else QFont.Weight.Normal)
        painter.setFont(font)
        
        painter.setPen(QPen(text_color))
        painter.drawText(rect, Qt.AlignCenter, str(date.day()))

        painter.restore()


class Calendar(QWidget):
    """Material 3–like date picker composed around QCalendarWidget.
    - Header shows large localized selected date
    - No caption and no footer buttons (mimics dialog body)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Identify container for QSS styling
        self.setObjectName("datePicker")

        # Internal calendar
        self._calendar = _M3Calendar(self)
        self._calendar.setGridVisible(False)
        self._calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        try:
            self._calendar.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
        except AttributeError:
            self._calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        self._calendar.setNavigationBarVisible(True)
        self._calendar.setDateEditEnabled(False)
        self._calendar.setLocale(QLocale.system())

        # Layout
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)

        # Localized headline for selected date
        self._headline = QLabel(self._selected_date_text(self._calendar.selectedDate()))
        self._headline.setObjectName("calendarHeadline")
        self._headline.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        root.addWidget(self._headline)

        # Month label like "November 2018"
        self._month_label = QLabel(self._month_text(self._calendar.yearShown(), self._calendar.monthShown()))
        self._month_label.setObjectName("calendarMonthLabel")
        self._month_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        root.addWidget(self._month_label)

        root.addWidget(self._calendar)

        # Strip month/year text from the navigation bar but keep prev/next arrows
        self._hide_nav_title()
        # Re-apply after page changes (Qt can rebuild nav bar)
        self._calendar.currentPageChanged.connect(lambda *_: (self._hide_nav_title(), self._refresh_month_label()))

        # Signals
        self._calendar.selectionChanged.connect(self._on_selection_changed)

    def _hide_nav_title(self):
        nav = self._calendar.findChild(QWidget, "qt_calendar_navigationbar")
        if not nav:
            return
        # Tighten nav layout
        if nav.layout():
            nav.layout().setContentsMargins(0, 0, 0, 0)
            nav.layout().setSpacing(0)
        # Hide everything except prev/next month buttons
        for w in nav.findChildren(QWidget):
            name = w.objectName()
            if isinstance(w, QToolButton) and name in ("qt_calendar_prevmonth", "qt_calendar_nextmonth"):
                w.show()
            else:
                w.hide()

    def _selected_date_text(self, date: QDate) -> str:
        loc = QLocale.system()
        return loc.toString(date, "ddd, MMM d")

    def _month_text(self, year: int, month: int) -> str:
        loc = QLocale.system()
        date = QDate(year, month, 1)
        return loc.toString(date, "MMMM yyyy")

    def _refresh_month_label(self):
        self._month_label.setText(self._month_text(self._calendar.yearShown(), self._calendar.monthShown()))

    def _on_selection_changed(self):
        self._headline.setText(self._selected_date_text(self._calendar.selectedDate()))

    def calendar(self) -> QCalendarWidget:
        return self._calendar

    def selectedDate(self) -> QDate:
        return self._calendar.selectedDate()

    def setSelectedDate(self, date: QDate):
        self._calendar.setSelectedDate(date)
        self._headline.setText(self._selected_date_text(date))
        self._refresh_month_label()
