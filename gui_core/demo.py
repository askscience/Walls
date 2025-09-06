#!/usr/bin/env python3
"""
GUI Core Demo Application
Showcases all themed components using the unified QSS theme.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QGroupBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer

# Import theme applier
from apply_theme import apply_theme

# Import all components
from components.button.widgets import PrimaryButton
from components.radio_button.widgets import RadioButton
from components.line_edit.widgets import LineEdit
from components.checkbox.widgets import CheckBox
from components.slider.widgets import Slider
from components.combo_box.widgets import ComboBox
from components.progress_bar.widgets import ProgressBar
from components.tab_widget.widgets import TabWidget
from components.switch.widgets import Switch
from components.toolbar.widgets import ToolBar
from components.breadcrumbs.widgets import Breadcrumbs
from components.pagination.widgets import Pagination
from components.tooltips.widgets import ToolTip
from components.notifications.widgets import NotificationCenter
from components.message_boxes.widgets import MessageBox
from components.modals.widgets import Modal
from components.accordion.widgets import Accordion
from components.cards.widgets import Card
from components.ai_loader.widgets import AiLoaderSmall, AiLoaderMedium, AiLoaderBig
from components.calendar.widgets import Calendar


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI Core Demo - Unified Theme")
        self.setGeometry(100, 100, 1000, 700)
        self.setup_ui()
        self.setup_demo_interactions()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("GUI Core Components Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Scroll area for content
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Buttons Section
        buttons_group = self.create_buttons_section()
        scroll_layout.addWidget(buttons_group)
        
        # Form Controls Section
        form_group = self.create_form_controls_section()
        scroll_layout.addWidget(form_group)
        
        # Progress & Sliders Section
        progress_group = self.create_progress_section()
        scroll_layout.addWidget(progress_group)
        
        # Tabs Section
        tabs_group = self.create_tabs_section()
        scroll_layout.addWidget(tabs_group)

        # Navigation Section (NEW)
        nav_group = self.create_navigation_section()
        scroll_layout.addWidget(nav_group)
        
        # Feedback & Overlays Section (NEW)
        feedback_group = self.create_feedback_section()
        scroll_layout.addWidget(feedback_group)

        # AI Loaders Section (NEW)
        ai_group = self.create_ai_loader_section()
        scroll_layout.addWidget(ai_group)
        
        # Calendar Section
        calendar_group = self.create_calendar_section()
        scroll_layout.addWidget(calendar_group)

        # Cards Section (NEW)
        cards_group = self.create_cards_section()
        scroll_layout.addWidget(cards_group)

        # Accordion Section (NEW)
        accordion_group = self.create_accordion_section()
        scroll_layout.addWidget(accordion_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

    def create_buttons_section(self):
        group = QGroupBox("Buttons")
        layout = QHBoxLayout(group)
        
        # Primary button
        primary_btn = PrimaryButton("Primary Button")
        layout.addWidget(primary_btn)
        
        # Outlined button (uses variant property)
        outlined_btn = PrimaryButton("Outlined Button")
        outlined_btn.setProperty("variant", "outlined")
        layout.addWidget(outlined_btn)
        
        # Tonal button (subtle filled)
        tonal_btn = PrimaryButton("Tonal Button")
        tonal_btn.setProperty("variant", "tonal")
        layout.addWidget(tonal_btn)
        
        # Disabled button
        disabled_btn = PrimaryButton("Disabled")
        disabled_btn.setEnabled(False)
        layout.addWidget(disabled_btn)
        
        layout.addStretch()
        return group

    def create_form_controls_section(self):
        group = QGroupBox("Form Controls")
        layout = QGridLayout(group)
        
        # Line edits
        layout.addWidget(QLabel("Text Input:"), 0, 0)
        line_edit = LineEdit("Enter your name...")
        layout.addWidget(line_edit, 0, 1)
        
        # Radio buttons
        layout.addWidget(QLabel("Options:"), 1, 0)
        radio_layout = QHBoxLayout()
        radio1 = RadioButton("Option A")
        radio2 = RadioButton("Option B")
        radio3 = RadioButton("Option C")
        radio1.setChecked(True)
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addWidget(radio3)
        radio_layout.addStretch()
        layout.addLayout(radio_layout, 1, 1)
        
        # Checkboxes
        layout.addWidget(QLabel("Features:"), 2, 0)
        checkbox_layout = QHBoxLayout()
        cb1 = CheckBox("Enable notifications")
        cb2 = CheckBox("Auto-save")
        cb3 = CheckBox("Dark mode")
        cb1.setChecked(True)
        cb3.setChecked(True)
        checkbox_layout.addWidget(cb1)
        checkbox_layout.addWidget(cb2)
        checkbox_layout.addWidget(cb3)
        checkbox_layout.addStretch()
        layout.addLayout(checkbox_layout, 2, 1)
        
        # Switch
        layout.addWidget(QLabel("Toggle:"), 3, 0)
        switch = Switch("Enable feature")
        switch.setChecked(True)
        layout.addWidget(switch, 3, 1)
        
        # Combo box
        layout.addWidget(QLabel("Selection:"), 4, 0)
        combo = ComboBox()
        combo.addItems(["Choose option...", "Friends", "Family", "Work", "Other"])
        layout.addWidget(combo, 4, 1)
        
        return group

    def create_progress_section(self):
        group = QGroupBox("Progress & Sliders")
        layout = QVBoxLayout(group)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(65)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)
        
        # Slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Volume:"))
        self.slider = Slider()
        self.slider.setRange(0, 100)
        self.slider.setValue(75)
        self.volume_label = QLabel("75")
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.volume_label)
        layout.addLayout(slider_layout)
        
        return group

    def create_tabs_section(self):
        group = QGroupBox("Tab Widget")
        layout = QVBoxLayout(group)
        
        tabs = TabWidget()
        
        # Tab 1 - Info
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("This is the first tab with some information."))
        tab1_layout.addWidget(QLabel("All components use the same unified theme."))
        tab1_layout.addStretch()
        tabs.addTab(tab1, "Information")
        
        # Tab 2 - Settings
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("Settings tab with more controls:"))
        setting_cb = CheckBox("Enable advanced features")
        tab2_layout.addWidget(setting_cb)
        setting_edit = LineEdit("Configuration value...")
        tab2_layout.addWidget(setting_edit)
        tab2_layout.addStretch()
        tabs.addTab(tab2, "Settings")
        
        # Tab 3 - About
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.addWidget(QLabel("GUI Core Demo Application"))
        tab3_layout.addWidget(QLabel("Modern, flat, rounded theme for PySide6"))
        tab3_layout.addWidget(QLabel("All styling is defined in a single theme.qss file"))
        tab3_layout.addStretch()
        tabs.addTab(tab3, "About")
        
        layout.addWidget(tabs)
        return group

    def create_navigation_section(self):
        group = QGroupBox("Navigation Components (New)")
        layout = QVBoxLayout(group)

        # Toolbar
        toolbar_frame = QFrame()
        toolbar_layout = QVBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        tb = ToolBar("Main Toolbar")
        tb.add_button("New")
        tb.add_button("Open")
        tb.add_button("Save")
        toolbar_layout.addWidget(tb)
        layout.addWidget(toolbar_frame)

        # Breadcrumbs
        bc = Breadcrumbs(["Home", "Projects", "GUI Core", "Demo"])
        layout.addWidget(bc)

        # Pagination
        self.pagination_label = QLabel("Page: 1")
        pg = Pagination(total_pages=10, current_page=1)
        pg.pageChanged.connect(lambda p: self.pagination_label.setText(f"Page: {p}"))
        layout.addWidget(pg)
        layout.addWidget(self.pagination_label)

        return group

    def create_feedback_section(self):
        group = QGroupBox("Feedback & Overlays (New)")
        v = QVBoxLayout(group)

        # ToolTip demo
        v.addWidget(QLabel("Inline ToolTip:"))
        tip_row = QHBoxLayout()
        tip_btn = PrimaryButton("Show Tooltip")
        # keep a single tooltip instance
        if not hasattr(self, "inline_tooltip"):
            self.inline_tooltip = ToolTip("This is an inline tooltip", self)
        tip_btn.clicked.connect(lambda: self.show_inline_tooltip(tip_btn))
        tip_row.addWidget(tip_btn)
        tip_row.addStretch()
        v.addLayout(tip_row)

        # Notifications demo
        v.addWidget(QLabel("Notifications:"))
        self.notification_center = NotificationCenter(self)
        notif_row = QHBoxLayout()
        btn_info = PrimaryButton("Notify Info")
        btn_success = PrimaryButton("Notify Success")
        btn_warning = PrimaryButton("Notify Warning")
        btn_error = PrimaryButton("Notify Error")
        btn_success.setProperty("variant", "tonal")
        btn_warning.setProperty("variant", "outlined")
        btn_error.setProperty("variant", "outlined")
        btn_info.clicked.connect(lambda: self.notification_center.showNotification("Informational message", "info", app_icon="information.svg"))
        btn_success.clicked.connect(lambda: self.notification_center.showNotification("Operation successful", "success", app_icon="circle-check.svg"))
        btn_warning.clicked.connect(lambda: self.notification_center.showNotification("Please check your settings", "warning", app_icon="exclamation.svg"))
        btn_error.clicked.connect(lambda: self.notification_center.showNotification("Something went wrong", "error", app_icon="circle-xmark.svg"))
        for b in (btn_info, btn_success, btn_warning, btn_error):
            notif_row.addWidget(b)
        notif_row.addStretch()
        v.addLayout(notif_row)

        # Message boxes demo
        v.addWidget(QLabel("Message Boxes:"))
        mb_row = QHBoxLayout()
        mb_info = PrimaryButton("Info Box")
        mb_warn = PrimaryButton("Warning Box")
        mb_crit = PrimaryButton("Critical Box")
        mb_q = PrimaryButton("Question Box")
        mb_info.clicked.connect(lambda: MessageBox.show_information(self, "Information", "This is an information message box."))
        mb_warn.clicked.connect(lambda: MessageBox.show_warning(self, "Warning", "This is a warning message box."))
        mb_crit.clicked.connect(lambda: MessageBox.show_critical(self, "Critical", "This is a critical error message box."))
        mb_q.clicked.connect(lambda: MessageBox.show_question(self, "Question", "Do you want to proceed?"))
        for b in (mb_info, mb_warn, mb_crit, mb_q):
            mb_row.addWidget(b)
        mb_row.addStretch()
        v.addLayout(mb_row)

        # Modal demo
        v.addWidget(QLabel("Modal Dialog:"))
        modal_row = QHBoxLayout()
        modal_btn = PrimaryButton("Open Modal")
        modal_btn.clicked.connect(lambda: Modal("Confirm Action", "This is a modal dialog. Continue?", self).exec())
        modal_row.addWidget(modal_btn)
        modal_row.addStretch()
        v.addLayout(modal_row)

        return group

    def create_ai_loader_section(self):
        group = QGroupBox("AI Loaders (New)")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Small:"))
        layout.addWidget(AiLoaderSmall())
        layout.addSpacing(12)

        layout.addWidget(QLabel("Medium (stopped):"))
        medium_loader = AiLoaderMedium(animated=False)
        layout.addWidget(medium_loader)
        layout.addSpacing(12)

        layout.addWidget(QLabel("Big:"))
        layout.addWidget(AiLoaderBig())

        layout.addStretch()
        return group

    def create_calendar_section(self):
        group = QGroupBox("Calendar")
        layout = QVBoxLayout(group)
        
        calendar = Calendar()
        layout.addWidget(calendar)
        
        return group

    def create_cards_section(self):
        group = QGroupBox("Cards (New)")
        layout = QHBoxLayout(group)

        # Simple text card
        card1 = Card(title="Welcome", subtitle="Cards are versatile blocks for content.")
        layout.addWidget(card1)

        # Card with extra body content and actions
        card2 = Card(title="Project Alpha", subtitle="This project explores building a cohesive PySide6 design system.")
        body_label = QLabel("Key points:\n- Themed components\n- Consistent spacing\n- Reusable patterns")
        body_label.setWordWrap(True)
        card2.addWidget(body_label)
        act1 = PrimaryButton("Details")
        act1.setProperty("variant", "outlined")
        act2 = PrimaryButton("Open")
        card2.addActionButton(act1)
        card2.addActionButton(act2)
        layout.addWidget(card2)

        # Compact card
        card3 = Card(title="Status", subtitle="All systems operational.")
        layout.addWidget(card3)

        layout.addStretch()
        return group

    def create_accordion_section(self):
        group = QGroupBox("Accordion (New)")
        layout = QVBoxLayout(group)

        acc = Accordion()
        # Section 1
        s1_body = QWidget()
        s1_l = QVBoxLayout(s1_body)
        s1_l.addWidget(QLabel("Section 1 content: explanatory text and controls."))
        s1_l.addWidget(PrimaryButton("Action 1"))
        acc.addSection("Getting Started", s1_body, expanded=True)

        # Section 2
        s2_body = QWidget()
        s2_l = QVBoxLayout(s2_body)
        s2_l.addWidget(QLabel("Section 2 body can contain arbitrary widgets."))
        acc.addSection("Advanced Options", s2_body, expanded=False)

        # Section 3
        s3_body = QWidget()
        s3_l = QVBoxLayout(s3_body)
        s3_l.addWidget(QLabel("Another section with more content."))
        acc.addSection("More", s3_body, expanded=False)

        layout.addWidget(acc)
        return group

    def show_inline_tooltip(self, anchor_widget: QWidget):
        # Position tooltip below left of the anchor and auto-hide after a short delay
        pos = anchor_widget.mapToGlobal(anchor_widget.rect().bottomLeft())
        # Slight offset
        pos.setY(pos.y() + 6)
        self.inline_tooltip.showAt(pos)
        QTimer.singleShot(1500, self.inline_tooltip.hide)

    def setup_demo_interactions(self):
        # Connect slider to label
        self.slider.valueChanged.connect(
            lambda v: self.volume_label.setText(str(v))
        )
        
        # Animate progress bar
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(100)  # Update every 100ms
        self.progress_direction = 1

    def update_progress(self):
        current = self.progress_bar.value()
        if current >= 100:
            self.progress_direction = -1
        elif current <= 0:
            self.progress_direction = 1
        
        self.progress_bar.setValue(current + self.progress_direction)


def main():
    app = QApplication(sys.argv)
    
    # Apply the unified theme
    apply_theme(app)
    
    # Create and show demo window
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()