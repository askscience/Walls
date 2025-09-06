from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt

class Pagination(QWidget):
    """Simple pagination control with prev/next and page number buttons.
    Use setTotalPages() and setCurrentPage() to configure.
    Emits pageChanged(int).
    """
    pageChanged = Signal(int)

    def __init__(self, total_pages: int = 1, current_page: int = 1, parent=None):
        super().__init__(parent)
        self.setObjectName("pagination")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)

        self._total_pages = max(1, total_pages)
        self._current_page = max(1, min(current_page, self._total_pages))

        self._prev = QPushButton("‹")
        self._prev.setFixedHeight(28)
        self._prev.clicked.connect(self.prev)
        self._next = QPushButton("›")
        self._next.setFixedHeight(28)
        self._next.clicked.connect(self.next)

        self._layout.addWidget(self._prev)
        self._page_buttons: list[QPushButton] = []
        self._layout.addWidget(self._next)

        self._rebuild()

    def totalPages(self) -> int:
        return self._total_pages

    def currentPage(self) -> int:
        return self._current_page

    def setTotalPages(self, n: int):
        self._total_pages = max(1, int(n))
        self._current_page = max(1, min(self._current_page, self._total_pages))
        self._rebuild()

    def setCurrentPage(self, n: int):
        n = max(1, min(int(n), self._total_pages))
        if n != self._current_page:
            self._current_page = n
            self.pageChanged.emit(self._current_page)
            self._update_buttons()

    def prev(self):
        if self._current_page > 1:
            self.setCurrentPage(self._current_page - 1)

    def next(self):
        if self._current_page < self._total_pages:
            self.setCurrentPage(self._current_page + 1)

    def _rebuild(self):
        # Remove old numbered buttons (between prev and next)
        for btn in self._page_buttons:
            self._layout.removeWidget(btn)
            btn.deleteLater()
        self._page_buttons.clear()

        # Show at most 7 buttons: current, two on each side, first/last with ellipsis policy
        pages = self._visible_pages()
        insert_index = 1  # after prev
        for p in pages:
            btn = QPushButton(str(p) if isinstance(p, int) else "…")
            btn.setFixedHeight(28)
            if isinstance(p, int):
                btn.clicked.connect(lambda _, n=p: self.setCurrentPage(n))
                if p == self._current_page:
                    btn.setProperty("current", True)
                else:
                    btn.setProperty("current", False)
            else:
                btn.setEnabled(False)
            self._layout.insertWidget(insert_index, btn)
            self._page_buttons.append(btn)
            insert_index += 1

        self._update_buttons()

    def _visible_pages(self):
        n = self._total_pages
        c = self._current_page
        if n <= 7:
            return list(range(1, n + 1))
        pages = [1]
        if c > 4:
            pages.append("…")
        start = max(2, c - 2)
        end = min(n - 1, c + 2)
        pages.extend(range(start, end + 1))
        if c < n - 3:
            pages.append("…")
        pages.append(n)
        return pages

    def _update_buttons(self):
        self._prev.setDisabled(self._current_page <= 1)
        self._next.setDisabled(self._current_page >= self._total_pages)
        for btn in self._page_buttons:
            text = btn.text()
            if text.isdigit() and int(text) == self._current_page:
                btn.setProperty("current", True)
            else:
                btn.setProperty("current", False)
            btn.style().unpolish(btn); btn.style().polish(btn)