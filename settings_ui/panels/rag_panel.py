"""Modern RAG Panel with flat design and gui_core components."""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon

# Import gui_core components
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from gui_core.components.cards.widgets import Card
from gui_core.components.line_edit.widgets import LineEdit
from gui_core.components.button.widgets import PrimaryButton
from gui_core.components.switch.widgets import Switch
from gui_core.components.checkbox.widgets import CheckBox
from gui_core.components.combo_box.widgets import ComboBox
from gui_core.components.slider.widgets import Slider


class RAGPanel(QWidget):
    """Modern RAG configuration panel for rag/config.json."""
    
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = {}
        self.widgets = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the modern flat user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameStyle(0)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 16, 0)  # Right margin for scrollbar
        content_layout.setSpacing(20)
        
        # Data configuration card
        data_card = self.create_data_card()
        content_layout.addWidget(data_card)
        
        # Models configuration card
        models_card = self.create_models_card()
        content_layout.addWidget(models_card)
        
        # LLM parameters card
        params_card = self.create_parameters_card()
        content_layout.addWidget(params_card)
        
        # Exclude list card
        exclude_card = self.create_exclude_card()
        content_layout.addWidget(exclude_card)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def create_data_card(self):
        """Create data configuration card matching rag/config.json structure."""
        card = Card("Data Configuration", "Configure RAG data directories and database settings")
        
        data_layout = QGridLayout()
        data_layout.setSpacing(12)
        
        # Data directory
        data_layout.addWidget(QLabel("Data Directory:"), 0, 0)
        self.widgets['data_dir'] = LineEdit()
        self.widgets['data_dir'].setPlaceholderText("data")
        self.widgets['data_dir'].textChanged.connect(self.on_config_changed)
        data_layout.addWidget(self.widgets['data_dir'], 0, 1)
        
        # ChromaDB path
        data_layout.addWidget(QLabel("ChromaDB Path:"), 1, 0)
        self.widgets['chroma_db_path'] = LineEdit()
        self.widgets['chroma_db_path'].setPlaceholderText("chroma_db")
        self.widgets['chroma_db_path'].textChanged.connect(self.on_config_changed)
        data_layout.addWidget(self.widgets['chroma_db_path'], 1, 1)
        
        # ChromaDB collection name
        data_layout.addWidget(QLabel("Collection Name:"), 2, 0)
        self.widgets['chroma_collection_name'] = LineEdit()
        self.widgets['chroma_collection_name'].setPlaceholderText("rag_documents")
        self.widgets['chroma_collection_name'].textChanged.connect(self.on_config_changed)
        data_layout.addWidget(self.widgets['chroma_collection_name'], 2, 1)
        
        data_widget = QWidget()
        data_widget.setLayout(data_layout)
        card.addWidget(data_widget)
        return card
    
    def create_models_card(self):
        """Create models configuration card matching rag/config.json structure."""
        card = Card("Models Configuration", "Configure embedding and LLM models")
        
        models_layout = QGridLayout()
        models_layout.setSpacing(12)
        
        # Ollama embedding model
        models_layout.addWidget(QLabel("Embedding Model:"), 0, 0)
        self.widgets['ollama_embedding_model'] = LineEdit()
        self.widgets['ollama_embedding_model'].setPlaceholderText("nomic-embed-text")
        self.widgets['ollama_embedding_model'].textChanged.connect(self.on_config_changed)
        models_layout.addWidget(self.widgets['ollama_embedding_model'], 0, 1)
        
        # Ollama LLM model
        models_layout.addWidget(QLabel("LLM Model:"), 1, 0)
        self.widgets['ollama_llm_model'] = LineEdit()
        self.widgets['ollama_llm_model'].setPlaceholderText("deepseek-r1:1.5b")
        self.widgets['ollama_llm_model'].textChanged.connect(self.on_config_changed)
        models_layout.addWidget(self.widgets['ollama_llm_model'], 1, 1)
        
        # Request timeout
        models_layout.addWidget(QLabel("Request Timeout (seconds):"), 2, 0)
        self.widgets['ollama_request_timeout'] = LineEdit()
        self.widgets['ollama_request_timeout'].setPlaceholderText("300.0")
        self.widgets['ollama_request_timeout'].textChanged.connect(self.on_config_changed)
        models_layout.addWidget(self.widgets['ollama_request_timeout'], 2, 1)
        
        models_widget = QWidget()
        models_widget.setLayout(models_layout)
        card.addWidget(models_widget)
        return card
    
    def create_parameters_card(self):
        """Create LLM parameters card matching rag/config.json structure."""
        card = Card("LLM Parameters", "Configure language model generation parameters")
        
        params_layout = QGridLayout()
        params_layout.setSpacing(12)
        
        # Temperature
        params_layout.addWidget(QLabel("Temperature:"), 0, 0)
        self.widgets['temperature'] = LineEdit()
        self.widgets['temperature'].setPlaceholderText("1.0")
        self.widgets['temperature'].textChanged.connect(self.on_config_changed)
        params_layout.addWidget(self.widgets['temperature'], 0, 1)
        
        # Top K
        params_layout.addWidget(QLabel("Top K:"), 1, 0)
        self.widgets['top_k'] = LineEdit()
        self.widgets['top_k'].setPlaceholderText("64")
        self.widgets['top_k'].textChanged.connect(self.on_config_changed)
        params_layout.addWidget(self.widgets['top_k'], 1, 1)
        
        # Top P
        params_layout.addWidget(QLabel("Top P:"), 2, 0)
        self.widgets['top_p'] = LineEdit()
        self.widgets['top_p'].setPlaceholderText("0.95")
        self.widgets['top_p'].textChanged.connect(self.on_config_changed)
        params_layout.addWidget(self.widgets['top_p'], 2, 1)
        
        # Min P
        params_layout.addWidget(QLabel("Min P:"), 3, 0)
        self.widgets['min_p'] = LineEdit()
        self.widgets['min_p'].setPlaceholderText("0.0")
        self.widgets['min_p'].textChanged.connect(self.on_config_changed)
        params_layout.addWidget(self.widgets['min_p'], 3, 1)
        
        params_widget = QWidget()
        params_widget.setLayout(params_layout)
        card.addWidget(params_widget)
        return card
    
    def create_exclude_card(self):
        """Create exclude list card matching rag/config.json structure."""
        card = Card("Exclude List", "Configure files and directories to exclude from indexing")
        
        exclude_layout = QVBoxLayout()
        exclude_layout.setSpacing(12)
        
        # Exclude list text area
        exclude_label = QLabel("Exclude Patterns (one per line):")
        exclude_layout.addWidget(exclude_label)
        
        self.widgets['exclude_list'] = QTextEdit()
        self.widgets['exclude_list'].setPlaceholderText("venv\n__pycache__\nnode_modules\nbuild\ndist\n*.egg-info\n*.pyc\n*.pyo\n*.so\n*.a\n*.o\nchroma_db\n*.tmp\n*.temp\n*.bak\n*~\n*.log\n*.swp\n*.part\n*.crdownload\n*.download\nprefs-*.js")
        self.widgets['exclude_list'].setMaximumHeight(200)
        self.widgets['exclude_list'].textChanged.connect(self.on_config_changed)
        exclude_layout.addWidget(self.widgets['exclude_list'])
        
        # Common patterns buttons
        buttons_layout = QHBoxLayout()
        
        add_python_button = PrimaryButton("Add Python Patterns")
        add_python_button.clicked.connect(self.add_python_patterns)
        buttons_layout.addWidget(add_python_button)
        
        add_node_button = PrimaryButton("Add Node.js Patterns")
        add_node_button.clicked.connect(self.add_node_patterns)
        buttons_layout.addWidget(add_node_button)
        
        add_build_button = PrimaryButton("Add Build Patterns")
        add_build_button.clicked.connect(self.add_build_patterns)
        buttons_layout.addWidget(add_build_button)
        
        buttons_layout.addStretch()
        exclude_layout.addLayout(buttons_layout)
        
        exclude_widget = QWidget()
        exclude_widget.setLayout(exclude_layout)
        card.addWidget(exclude_widget)
        return card
    
    def add_python_patterns(self):
        """Add common Python exclude patterns."""
        current_text = self.widgets['exclude_list'].toPlainText()
        python_patterns = ["__pycache__", "*.pyc", "*.pyo", "*.egg-info", "venv", "env", ".pytest_cache"]
        
        existing_lines = set(line.strip() for line in current_text.split('\n') if line.strip())
        new_patterns = [pattern for pattern in python_patterns if pattern not in existing_lines]
        
        if new_patterns:
            if current_text.strip():
                current_text += "\n"
            current_text += "\n".join(new_patterns)
            self.widgets['exclude_list'].setPlainText(current_text)
    
    def add_node_patterns(self):
        """Add common Node.js exclude patterns."""
        current_text = self.widgets['exclude_list'].toPlainText()
        node_patterns = ["node_modules", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*", ".npm", ".yarn"]
        
        existing_lines = set(line.strip() for line in current_text.split('\n') if line.strip())
        new_patterns = [pattern for pattern in node_patterns if pattern not in existing_lines]
        
        if new_patterns:
            if current_text.strip():
                current_text += "\n"
            current_text += "\n".join(new_patterns)
            self.widgets['exclude_list'].setPlainText(current_text)
    
    def add_build_patterns(self):
        """Add common build exclude patterns."""
        current_text = self.widgets['exclude_list'].toPlainText()
        build_patterns = ["build", "dist", "*.so", "*.a", "*.o", "*.tmp", "*.temp", "*.bak", "*~"]
        
        existing_lines = set(line.strip() for line in current_text.split('\n') if line.strip())
        new_patterns = [pattern for pattern in build_patterns if pattern not in existing_lines]
        
        if new_patterns:
            if current_text.strip():
                current_text += "\n"
            current_text += "\n".join(new_patterns)
            self.widgets['exclude_list'].setPlainText(current_text)
    
    def on_config_changed(self):
        """Handle configuration changes and emit signal."""
        # Parse exclude list from text area
        exclude_text = self.widgets['exclude_list'].toPlainText()
        exclude_list = [line.strip() for line in exclude_text.split('\n') if line.strip()]
        
        # Collect all configuration data matching rag/config.json structure
        config = {
            "data_dir": self.widgets['data_dir'].text() or "data",
            "chroma_db_path": self.widgets['chroma_db_path'].text() or "chroma_db",
            "chroma_collection_name": self.widgets['chroma_collection_name'].text() or "rag_documents",
            "ollama_embedding_model": self.widgets['ollama_embedding_model'].text() or "nomic-embed-text",
            "ollama_llm_model": self.widgets['ollama_llm_model'].text() or "deepseek-r1:1.5b",
            "llm_model_params": {
                "temperature": float(self.widgets['temperature'].text() or "1.0"),
                "top_k": int(self.widgets['top_k'].text() or "64"),
                "top_p": float(self.widgets['top_p'].text() or "0.95"),
                "min_p": float(self.widgets['min_p'].text() or "0.0")
            },
            "ollama_request_timeout": float(self.widgets['ollama_request_timeout'].text() or "300.0"),
            "exclude_list": exclude_list
        }
        
        self.config_data = config
        self.config_changed.emit(config)
    
    def load_config(self, config_data: Dict[str, Any]):
        """Load configuration data into the panel."""
        self.config_data = config_data.copy()
        
        # Load data settings
        self.widgets['data_dir'].setText(config_data.get("data_dir", "data"))
        self.widgets['chroma_db_path'].setText(config_data.get("chroma_db_path", "chroma_db"))
        self.widgets['chroma_collection_name'].setText(config_data.get("chroma_collection_name", "rag_documents"))
        
        # Load model settings
        self.widgets['ollama_embedding_model'].setText(config_data.get("ollama_embedding_model", "nomic-embed-text"))
        self.widgets['ollama_llm_model'].setText(config_data.get("ollama_llm_model", "deepseek-r1:1.5b"))
        self.widgets['ollama_request_timeout'].setText(str(config_data.get("ollama_request_timeout", 300.0)))
        
        # Load LLM parameters
        llm_params = config_data.get("llm_model_params", {})
        self.widgets['temperature'].setText(str(llm_params.get("temperature", 1.0)))
        self.widgets['top_k'].setText(str(llm_params.get("top_k", 64)))
        self.widgets['top_p'].setText(str(llm_params.get("top_p", 0.95)))
        self.widgets['min_p'].setText(str(llm_params.get("min_p", 0.0)))
        
        # Load exclude list
        exclude_list = config_data.get("exclude_list", [])
        exclude_text = "\n".join(exclude_list)
        self.widgets['exclude_list'].setPlainText(exclude_text)