# GUI Core (PySide6 / Qt6)

A modern, ultra-compact, minimalist UI kit for Qt apps. Styling is centralized in a single theme.qss for a clean, grayscale-first look (dark accent #333333), tight spacing, and smaller controls.

## Key principles
- Single source of truth: theme.qss applied once via apply_theme(app)
- Avoid per-widget setStyleSheet; use properties/object names for variants
- Components are thin wrappers around Qt widgets

## Folder structure
```
/gui_core
  ├── __init__.py
  ├── apply_theme.py      # Load/apply theme.qss globally
  ├── theme.qss           # Unified theme for ALL elements
  ├── components/
  │   ├── button/         # PrimaryButton
  │   ├── radio_button/   # RadioButton
  │   ├── calendar/       # Calendar
  │   ├── line_edit/      # LineEdit
  │   ├── checkbox/       # CheckBox
  │   ├── slider/         # Slider
  │   ├── combo_box/      # ComboBox
  │   ├── progress_bar/   # ProgressBar
  │   ├── tab_widget/     # TabWidget
  │   ├── breadcrumbs/    # Breadcrumbs
  │   ├── pagination/     # Pagination
  │   ├── toolbar/        # ToolBar
  │   ├── tooltips/       # ToolTip
  │   ├── notifications/  # Notification, NotificationCenter
  │   ├── message_boxes/  # MessageBox (QMessageBox wrapper)
  │   ├── modals/         # Modal (QDialog-based)
  │   ├── accordion/      # Accordion (collapsible sections)
  │   ├── cards/          # Card content blocks
  │   ├── switch/         # Switch (CheckBox-based)
  │   └── ai_loader/      # AiLoader (orbiting dots loader)
  └── utils/
```

## How styling works
- The global theme is defined in theme.qss (Qt Style Sheets)
- Call apply_theme(app) once at startup; all widgets inherit the theme
- Variants are expressed via widget properties/object names and class selectors

## Typography & color tokens
- Font stack: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui
- Colors: primary/accent #333333, text #212121, surfaces #FAFAFA, outline #E5E7EB, subdued text #6B7280, tonal layer #F3F4F6, selection bg #333333

## Design tokens
- Radius: containers 8px, buttons 10px, small elements 4–6px
- Borders: subtle 1px outlines (#E5E7EB) on inputs/containers
- Focus: inputs/combos use border color #333333 on focus (no thick glow)
- Button variants and sizing (compact):
  - Default QPushButton = “text” style; min-height 26px; hover overlay rgba(51,51,51,0.08)
  - primary: bg #333333; hover #2B2B2B; pressed #1F1F1F; disabled bg #E5E7EB
  - outlined: 1px border #333333; hover bg rgba(51,51,51,0.05)
  - tonal: bg #F3F4F6; hover #E5E5E5; text #4B5563
- Slider: groove 3px #E5E7EB; handle 12px #333333; sub-page #333333
- ProgressBar: track #E5E7EB; chunk #333333; height 3px
- Tabs: segmented pill tabs; selected tab filled #333333, unselected #F3F4F6
- Lists/tables/text areas: white bg, 1px border #E5E7EB, 8px radius
- Calendar: white grid bg; selection #333333; minimal chrome
- Scrollbars: ultra-thin 4px track; handle #D1D5DB (hover #9CA3AF)
- Tooltip: dark bg #1F2937, white text, 4–6px radius
- Icons:
  - SVG assets in utils/icons; load via QIcon
  - Includes realistic toggle assets: switch_off.svg and switch_on.svg
  - Keep icons monochrome-friendly whenever possible

## Using the components
```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from gui_core.apply_theme import apply_theme
from gui_core.components.button.widgets import PrimaryButton
from gui_core.components.line_edit.widgets import LineEdit
from gui_core.components.switch.widgets import Switch
from gui_core.components.accordion import Accordion
from gui_core.components.cards import Card
from gui_core.components.ai_loader.widgets import AiLoader, AiLoaderSmall, AiLoaderMedium, AiLoaderBig

app = QApplication([])
apply_theme(app)

w = QWidget(); lay = QVBoxLayout(w)
lay.addWidget(PrimaryButton("Primary"))                  # filled
outlined = PrimaryButton("Outlined"); outlined.setProperty("variant", "outlined"); lay.addWidget(outlined)
tonal = PrimaryButton("Tonal"); tonal.setProperty("variant", "tonal"); lay.addWidget(tonal)
lay.addWidget(LineEdit("Search"))
lay.addWidget(Switch("Enable"))

# AiLoader usage
lay.addWidget(AiLoaderSmall())            # animated small loader
static_loader = AiLoaderMedium(animated=False)
lay.addWidget(static_loader)              # stopped state
lay.addWidget(AiLoaderBig())              # animated big loader

# Cards
card = Card(title="Welcome", subtitle="Cards are versatile blocks for content.")
lay.addWidget(card)

# Accordion
acc = Accordion()
acc.addSection("Section A", QWidget(), expanded=True)
acc.addSection("Section B", QWidget(), expanded=False)
lay.addWidget(acc)

w.show(); app.exec()
```

## Buttons (default text + variants)
- Default QPushButton = minimal “text” style (transparent bg, dark-accent label)
- PrimaryButton sets variant="primary" (filled) by default
- Supported: primary (filled), outlined (1px border), tonal (soft fill)
- Legacy: objectName("outlined") is still matched in theme.qss

## AiLoader (orbiting dots)
- Purpose: neutral, elegant activity indicator for AI tasks
- Look: white circular base with smaller grey dots orbiting smoothly inside
- Sizes: small (24px), medium (40px), big (64px)
- Control: start()/stop() or setAnimated(True/False)
- Imports:
  - from gui_core.components.ai_loader.widgets import AiLoader, AiLoaderSmall, AiLoaderMedium, AiLoaderBig
  - or from gui_core import AiLoader (re-export), etc.

## Components quick reference
- RadioButton: 14px circular indicator; checked border + dot in #333333
- CheckBox: 14px rounded indicator; checked fill #333333
- LineEdit & ComboBox: 1px border #D1D5DB, 8px radius; focus border #333333; compact heights (LineEdit 28px, ComboBox 28px)
- Slider: 3px groove, 12px handle; sub-page in #333333
- ProgressBar: 3px height; chunk in #333333
- Tabs: segmented pills; selected tab filled #333333
- Switch: styled via `Switch::indicator` and SVGs (utils/icons/switch_off.svg, utils/icons/switch_on.svg) for a realistic toggle (38×20)
- Breadcrumbs: compact pill-like buttons; dark accent hover
- Pagination: previous/next + pages; current page filled #333333
- ToolBar: text-beside-icon buttons; subtle hover
- ToolTip: inline tooltip widget; global QToolTip themed
- Notifications: toast-like; kinds: info/success/warning/error
- MessageBox: themed QMessageBox wrapper; static info/warn/critical/question
- Modal: simple modal dialog with title, body and OK/Cancel actions
- Card: versatile content block with optional media, title, subtitle, body and actions
- Accordion: vertical stack of collapsible sections (header + body)
- Containers & views (QFrame, QGroupBox, QTextEdit, QListView, QTreeView, QTableView, QAbstractItemView): transparent surfaces, subtle 1px outlines, 8px radius

## Calendar specifics
- Forced white date grid and viewport (works under dark OS themes)
- Light gridlines; dark-accent selection; minimal chrome
- Key selectors in theme.qss: QCalendarWidget QTableView, QAbstractItemView

## Extend the theme
- Prefer properties/object names for variants (e.g., setProperty("variant", "danger") and target with QPushButton[variant="danger"])
- Keep all styling centralized in theme.qss

## Run the demo
```bash
python -m gui_core.demo
# or
python gui_core/demo.py
```