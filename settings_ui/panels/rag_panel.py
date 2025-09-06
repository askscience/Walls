"""Modern RAG Panel with flat design and gui_core components."""

import sys
import os
from pathlib import Path
from typing import Dict, Any

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
from gui_core.components.progress_bar.widgets import ProgressBar


class RAGPanel(QWidget):
    """Modern RAG (Retrieval-Augmented Generation) configuration panel."""
    
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = {}
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
        
        # RAG status card
        status_card = self.create_status_card()
        content_layout.addWidget(status_card)
        
        # Data sources card
        sources_card = self.create_data_sources_card()
        content_layout.addWidget(sources_card)
        
        # Embedding settings card
        embedding_card = self.create_embedding_card()
        content_layout.addWidget(embedding_card)
        
        # Vector store settings card
        vector_card = self.create_vector_store_card()
        content_layout.addWidget(vector_card)
        
        # Retrieval settings card
        retrieval_card = self.create_retrieval_card()
        content_layout.addWidget(retrieval_card)
        
        # Performance settings card
        performance_card = self.create_performance_card()
        content_layout.addWidget(performance_card)
        
        # Actions card
        actions_card = self.create_actions_card()
        content_layout.addWidget(actions_card)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def create_status_card(self):
        """Create RAG system status card."""
        card = Card("RAG System Status", "Current status of retrieval-augmented generation system")
        
        status_layout = QGridLayout()
        status_layout.setSpacing(12)
        
        # System status
        status_layout.addWidget(QLabel("Status:"), 0, 0)
        self.status_indicator = QLabel("● Inactive")
        self.status_indicator.setObjectName("statusIndicator")
        status_layout.addWidget(self.status_indicator, 0, 1)
        
        # Vector store status
        status_layout.addWidget(QLabel("Vector Store:"), 1, 0)
        self.vector_status = QLabel("Not initialized")
        status_layout.addWidget(self.vector_status, 1, 1)
        
        # Document count
        status_layout.addWidget(QLabel("Documents:"), 2, 0)
        self.doc_count_label = QLabel("0")
        status_layout.addWidget(self.doc_count_label, 2, 1)
        
        # Index size
        status_layout.addWidget(QLabel("Index Size:"), 3, 0)
        self.index_size_label = QLabel("0 MB")
        status_layout.addWidget(self.index_size_label, 3, 1)
        
        # Last update
        status_layout.addWidget(QLabel("Last Update:"), 4, 0)
        self.last_update_label = QLabel("Never")
        status_layout.addWidget(self.last_update_label, 4, 1)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        card.addWidget(status_widget)
        return card
    
    def create_data_sources_card(self):
        """Create data sources configuration card."""
        card = Card("Data Sources", "Configure document sources for RAG indexing")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Data directory
        dir_layout = QVBoxLayout()
        dir_layout.addWidget(QLabel("Data Directory:"))
        dir_row = QHBoxLayout()
        self.data_dir_edit = LineEdit("data/")
        self.data_dir_edit.textChanged.connect(self.on_config_changed)
        dir_row.addWidget(self.data_dir_edit)
        browse_button = PrimaryButton("Browse")
        browse_button.clicked.connect(self.browse_data_directory)
        dir_row.addWidget(browse_button)
        dir_layout.addLayout(dir_row)
        layout.addLayout(dir_layout)
        
        # File types
        types_layout = QVBoxLayout()
        types_layout.addWidget(QLabel("Supported File Types:"))
        
        types_grid = QGridLayout()
        self.file_type_checkboxes = {}
        file_types = [
            ("Markdown (.md)", "md", True),
            ("Text (.txt)", "txt", True),
            ("PDF (.pdf)", "pdf", False),
            ("Word (.docx)", "docx", False),
            ("HTML (.html)", "html", False),
            ("JSON (.json)", "json", True)
        ]
        
        for i, (label, ext, default) in enumerate(file_types):
            checkbox = CheckBox(label)
            checkbox.setChecked(default)
            checkbox.toggled.connect(self.on_config_changed)
            self.file_type_checkboxes[ext] = checkbox
            types_grid.addWidget(checkbox, i // 2, i % 2)
        
        types_layout.addLayout(types_grid)
        layout.addLayout(types_layout)
        
        # Auto-watch for changes
        watch_layout = QHBoxLayout()
        self.auto_watch_switch = Switch("Auto-watch directories for changes")
        self.auto_watch_switch.toggled.connect(self.on_config_changed)
        watch_layout.addWidget(self.auto_watch_switch)
        watch_layout.addStretch()
        layout.addLayout(watch_layout)
        
        # Exclude patterns
        exclude_layout = QVBoxLayout()
        exclude_layout.addWidget(QLabel("Exclude Patterns (one per line):"))
        self.exclude_patterns_edit = QTextEdit()
        self.exclude_patterns_edit.setMaximumHeight(80)
        self.exclude_patterns_edit.setPlainText("*.tmp\n*.log\n__pycache__")
        self.exclude_patterns_edit.textChanged.connect(self.on_config_changed)
        exclude_layout.addWidget(self.exclude_patterns_edit)
        layout.addLayout(exclude_layout)
        
        sources_widget = QWidget()
        sources_widget.setLayout(layout)
        card.addWidget(sources_widget)
        return card
    
    def create_embedding_card(self):
        """Create embedding model configuration card."""
        card = Card("Embedding Settings", "Configure text embedding model and parameters")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Embedding model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Embedding Model:"))
        self.embedding_model_combo = ComboBox()
        self.embedding_model_combo.addItems([
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "text-embedding-ada-002",
            "text-embedding-3-small",
            "text-embedding-3-large"
        ])
        self.embedding_model_combo.currentTextChanged.connect(self.on_config_changed)
        model_layout.addWidget(self.embedding_model_combo)
        layout.addLayout(model_layout)
        
        # Model provider
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Provider:"))
        self.provider_combo = ComboBox()
        self.provider_combo.addItems(["HuggingFace", "OpenAI", "Local"])
        self.provider_combo.currentTextChanged.connect(self.on_config_changed)
        provider_layout.addWidget(self.provider_combo)
        layout.addLayout(provider_layout)
        
        # API key (for OpenAI)
        api_layout = QVBoxLayout()
        api_layout.addWidget(QLabel("API Key (if required):"))
        self.api_key_edit = LineEdit()
        self.api_key_edit.setEchoMode(LineEdit.EchoMode.Password)
        self.api_key_edit.textChanged.connect(self.on_config_changed)
        api_layout.addWidget(self.api_key_edit)
        layout.addLayout(api_layout)
        
        # Embedding dimensions
        dim_layout = QHBoxLayout()
        dim_layout.addWidget(QLabel("Embedding Dimensions:"))
        self.dimensions_edit = LineEdit("384")
        self.dimensions_edit.textChanged.connect(self.on_config_changed)
        dim_layout.addWidget(self.dimensions_edit)
        layout.addLayout(dim_layout)
        
        # Batch size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("Batch Size:"))
        self.batch_size_slider = Slider()
        self.batch_size_slider.setMinimum(1)
        self.batch_size_slider.setMaximum(64)
        self.batch_size_slider.setValue(16)
        self.batch_size_slider.valueChanged.connect(self.on_config_changed)
        batch_layout.addWidget(self.batch_size_slider)
        self.batch_size_label = QLabel("16")
        batch_layout.addWidget(self.batch_size_label)
        layout.addLayout(batch_layout)
        
        embedding_widget = QWidget()
        embedding_widget.setLayout(layout)
        card.addWidget(embedding_widget)
        return card
    
    def create_vector_store_card(self):
        """Create vector store configuration card."""
        card = Card("Vector Store Settings", "Configure vector database and indexing")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Vector store type
        store_layout = QHBoxLayout()
        store_layout.addWidget(QLabel("Vector Store:"))
        self.vector_store_combo = ComboBox()
        self.vector_store_combo.addItems(["FAISS", "Chroma", "Pinecone", "Weaviate"])
        self.vector_store_combo.currentTextChanged.connect(self.on_config_changed)
        store_layout.addWidget(self.vector_store_combo)
        layout.addLayout(store_layout)
        
        # Index path
        index_layout = QVBoxLayout()
        index_layout.addWidget(QLabel("Index Storage Path:"))
        index_row = QHBoxLayout()
        self.index_path_edit = LineEdit("vector_store/")
        self.index_path_edit.textChanged.connect(self.on_config_changed)
        index_row.addWidget(self.index_path_edit)
        browse_index_button = PrimaryButton("Browse")
        browse_index_button.clicked.connect(self.browse_index_directory)
        index_row.addWidget(browse_index_button)
        index_layout.addLayout(index_row)
        layout.addLayout(index_layout)
        
        # Similarity metric
        metric_layout = QHBoxLayout()
        metric_layout.addWidget(QLabel("Similarity Metric:"))
        self.similarity_combo = ComboBox()
        self.similarity_combo.addItems(["cosine", "euclidean", "dot_product"])
        self.similarity_combo.currentTextChanged.connect(self.on_config_changed)
        metric_layout.addWidget(self.similarity_combo)
        layout.addLayout(metric_layout)
        
        # Index parameters
        params_layout = QVBoxLayout()
        params_layout.addWidget(QLabel("Index Parameters:"))
        
        # FAISS specific
        faiss_layout = QHBoxLayout()
        faiss_layout.addWidget(QLabel("FAISS Index Type:"))
        self.faiss_type_combo = ComboBox()
        self.faiss_type_combo.addItems(["IndexFlatL2", "IndexIVFFlat", "IndexHNSWFlat"])
        self.faiss_type_combo.currentTextChanged.connect(self.on_config_changed)
        faiss_layout.addWidget(self.faiss_type_combo)
        params_layout.addLayout(faiss_layout)
        
        layout.addLayout(params_layout)
        
        vector_widget = QWidget()
        vector_widget.setLayout(layout)
        card.addWidget(vector_widget)
        return card
    
    def create_retrieval_card(self):
        """Create retrieval configuration card."""
        card = Card("Retrieval Settings", "Configure document retrieval parameters")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Chunk size
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Chunk Size (tokens):"))
        self.chunk_size_slider = Slider()
        self.chunk_size_slider.setMinimum(100)
        self.chunk_size_slider.setMaximum(2000)
        self.chunk_size_slider.setValue(500)
        self.chunk_size_slider.valueChanged.connect(self.on_config_changed)
        chunk_layout.addWidget(self.chunk_size_slider)
        self.chunk_size_label = QLabel("500")
        chunk_layout.addWidget(self.chunk_size_label)
        layout.addLayout(chunk_layout)
        
        # Chunk overlap
        overlap_layout = QHBoxLayout()
        overlap_layout.addWidget(QLabel("Chunk Overlap (tokens):"))
        self.overlap_slider = Slider()
        self.overlap_slider.setMinimum(0)
        self.overlap_slider.setMaximum(200)
        self.overlap_slider.setValue(50)
        self.overlap_slider.valueChanged.connect(self.on_config_changed)
        overlap_layout.addWidget(self.overlap_slider)
        self.overlap_label = QLabel("50")
        overlap_layout.addWidget(self.overlap_label)
        layout.addLayout(overlap_layout)
        
        # Top-k results
        topk_layout = QHBoxLayout()
        topk_layout.addWidget(QLabel("Top-K Results:"))
        self.topk_slider = Slider()
        self.topk_slider.setMinimum(1)
        self.topk_slider.setMaximum(20)
        self.topk_slider.setValue(5)
        self.topk_slider.valueChanged.connect(self.on_config_changed)
        topk_layout.addWidget(self.topk_slider)
        self.topk_label = QLabel("5")
        topk_layout.addWidget(self.topk_label)
        layout.addLayout(topk_layout)
        
        # Similarity threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Similarity Threshold:"))
        self.threshold_slider = Slider()
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(100)
        self.threshold_slider.setValue(70)
        self.threshold_slider.valueChanged.connect(self.on_config_changed)
        threshold_layout.addWidget(self.threshold_slider)
        self.threshold_label = QLabel("0.70")
        threshold_layout.addWidget(self.threshold_label)
        layout.addLayout(threshold_layout)
        
        # Reranking
        rerank_layout = QHBoxLayout()
        self.rerank_switch = Switch("Enable Result Reranking")
        self.rerank_switch.toggled.connect(self.on_config_changed)
        rerank_layout.addWidget(self.rerank_switch)
        rerank_layout.addStretch()
        layout.addLayout(rerank_layout)
        
        retrieval_widget = QWidget()
        retrieval_widget.setLayout(layout)
        card.addWidget(retrieval_widget)
        return card
    
    def create_performance_card(self):
        """Create performance settings card."""
        card = Card("Performance Settings", "Configure system performance and caching")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Cache settings
        cache_layout = QHBoxLayout()
        self.cache_switch = Switch("Enable Query Caching")
        self.cache_switch.toggled.connect(self.on_config_changed)
        cache_layout.addWidget(self.cache_switch)
        cache_layout.addStretch()
        layout.addLayout(cache_layout)
        
        # Cache size
        cache_size_layout = QHBoxLayout()
        cache_size_layout.addWidget(QLabel("Cache Size (MB):"))
        self.cache_size_edit = LineEdit("100")
        self.cache_size_edit.textChanged.connect(self.on_config_changed)
        cache_size_layout.addWidget(self.cache_size_edit)
        layout.addLayout(cache_size_layout)
        
        # Parallel processing
        parallel_layout = QHBoxLayout()
        parallel_layout.addWidget(QLabel("Parallel Workers:"))
        self.workers_slider = Slider()
        self.workers_slider.setMinimum(1)
        self.workers_slider.setMaximum(8)
        self.workers_slider.setValue(2)
        self.workers_slider.valueChanged.connect(self.on_config_changed)
        parallel_layout.addWidget(self.workers_slider)
        self.workers_label = QLabel("2")
        parallel_layout.addWidget(self.workers_label)
        layout.addLayout(parallel_layout)
        
        # Memory optimization
        memory_layout = QHBoxLayout()
        self.memory_opt_switch = Switch("Enable Memory Optimization")
        self.memory_opt_switch.toggled.connect(self.on_config_changed)
        memory_layout.addWidget(self.memory_opt_switch)
        memory_layout.addStretch()
        layout.addLayout(memory_layout)
        
        performance_widget = QWidget()
        performance_widget.setLayout(layout)
        card.addWidget(performance_widget)
        return card
    
    def create_actions_card(self):
        """Create RAG system control actions card."""
        card = Card("RAG System Control", "Manage indexing and system operations")
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Progress bar for operations
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.index_button = PrimaryButton("Build Index")
        self.index_button.clicked.connect(self.build_index)
        button_layout.addWidget(self.index_button)
        
        self.update_button = PrimaryButton("Update Index")
        self.update_button.clicked.connect(self.update_index)
        button_layout.addWidget(self.update_button)
        
        self.clear_button = PrimaryButton("Clear Index")
        self.clear_button.clicked.connect(self.clear_index)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        self.test_button = PrimaryButton("Test Query")
        self.test_button.clicked.connect(self.test_query)
        button_layout.addWidget(self.test_button)
        
        layout.addLayout(button_layout)
        
        actions_widget = QWidget()
        actions_widget.setLayout(layout)
        card.addWidget(actions_widget)
        return card
    
    def on_config_changed(self):
        """Handle configuration changes and emit signal."""
        # Update slider labels
        if hasattr(self, 'batch_size_slider'):
            self.batch_size_label.setText(str(self.batch_size_slider.value()))
        if hasattr(self, 'chunk_size_slider'):
            self.chunk_size_label.setText(str(self.chunk_size_slider.value()))
        if hasattr(self, 'overlap_slider'):
            self.overlap_label.setText(str(self.overlap_slider.value()))
        if hasattr(self, 'topk_slider'):
            self.topk_label.setText(str(self.topk_slider.value()))
        if hasattr(self, 'threshold_slider'):
            self.threshold_label.setText(f"{self.threshold_slider.value() / 100:.2f}")
        if hasattr(self, 'workers_slider'):
            self.workers_label.setText(str(self.workers_slider.value()))
        
        # Collect configuration data
        config = {
            "data_sources": {
                "data_directory": self.data_dir_edit.text(),
                "file_types": [ext for ext, checkbox in self.file_type_checkboxes.items() if checkbox.isChecked()],
                "auto_watch": self.auto_watch_switch.isChecked(),
                "exclude_patterns": [pattern.strip() for pattern in self.exclude_patterns_edit.toPlainText().split('\n') if pattern.strip()]
            },
            "embedding": {
                "model": self.embedding_model_combo.currentText(),
                "provider": self.provider_combo.currentText(),
                "api_key": self.api_key_edit.text(),
                "dimensions": int(self.dimensions_edit.text() or "384"),
                "batch_size": self.batch_size_slider.value()
            },
            "vector_store": {
                "type": self.vector_store_combo.currentText(),
                "index_path": self.index_path_edit.text(),
                "similarity_metric": self.similarity_combo.currentText(),
                "faiss_index_type": self.faiss_type_combo.currentText()
            },
            "retrieval": {
                "chunk_size": self.chunk_size_slider.value(),
                "chunk_overlap": self.overlap_slider.value(),
                "top_k": self.topk_slider.value(),
                "similarity_threshold": self.threshold_slider.value() / 100,
                "enable_reranking": self.rerank_switch.isChecked()
            },
            "performance": {
                "enable_caching": self.cache_switch.isChecked(),
                "cache_size_mb": int(self.cache_size_edit.text() or "100"),
                "parallel_workers": self.workers_slider.value(),
                "memory_optimization": self.memory_opt_switch.isChecked()
            }
        }
        
        self.config_data = config
        self.config_changed.emit(config)
    
    def browse_data_directory(self):
        """Browse for data directory."""
        # Implement directory browser
        pass
    
    def browse_index_directory(self):
        """Browse for index directory."""
        # Implement directory browser
        pass
    
    def build_index(self):
        """Build the RAG index."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        # Implement index building logic
        pass
    
    def update_index(self):
        """Update the existing index."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        # Implement index update logic
        pass
    
    def clear_index(self):
        """Clear the RAG index."""
        # Implement index clearing logic
        self.doc_count_label.setText("0")
        self.index_size_label.setText("0 MB")
        self.vector_status.setText("Cleared")
        pass
    
    def test_query(self):
        """Test a query against the RAG system."""
        # Implement query testing
        pass
    
    def load_config(self, config_data: Dict[str, Any]):
        """Load configuration data into the panel."""
        self.config_data = config_data.copy()
        
        # Load data sources
        data_sources = config_data.get("data_sources", {})
        self.data_dir_edit.setText(data_sources.get("data_directory", "data/"))
        self.auto_watch_switch.setChecked(data_sources.get("auto_watch", False))
        
        file_types = data_sources.get("file_types", ["md", "txt", "json"])
        for ext, checkbox in self.file_type_checkboxes.items():
            checkbox.setChecked(ext in file_types)
        
        exclude_patterns = data_sources.get("exclude_patterns", [])
        self.exclude_patterns_edit.setPlainText('\n'.join(exclude_patterns))
        
        # Load embedding settings
        embedding = config_data.get("embedding", {})
        self.embedding_model_combo.setCurrentText(embedding.get("model", "sentence-transformers/all-MiniLM-L6-v2"))
        self.provider_combo.setCurrentText(embedding.get("provider", "HuggingFace"))
        self.api_key_edit.setText(embedding.get("api_key", ""))
        self.dimensions_edit.setText(str(embedding.get("dimensions", 384)))
        self.batch_size_slider.setValue(embedding.get("batch_size", 16))
        
        # Load vector store settings
        vector_store = config_data.get("vector_store", {})
        self.vector_store_combo.setCurrentText(vector_store.get("type", "FAISS"))
        self.index_path_edit.setText(vector_store.get("index_path", "vector_store/"))
        self.similarity_combo.setCurrentText(vector_store.get("similarity_metric", "cosine"))
        self.faiss_type_combo.setCurrentText(vector_store.get("faiss_index_type", "IndexFlatL2"))
        
        # Load retrieval settings
        retrieval = config_data.get("retrieval", {})
        self.chunk_size_slider.setValue(retrieval.get("chunk_size", 500))
        self.overlap_slider.setValue(retrieval.get("chunk_overlap", 50))
        self.topk_slider.setValue(retrieval.get("top_k", 5))
        self.threshold_slider.setValue(int(retrieval.get("similarity_threshold", 0.7) * 100))
        self.rerank_switch.setChecked(retrieval.get("enable_reranking", False))
        
        # Load performance settings
        performance = config_data.get("performance", {})
        self.cache_switch.setChecked(performance.get("enable_caching", False))
        self.cache_size_edit.setText(str(performance.get("cache_size_mb", 100)))
        self.workers_slider.setValue(performance.get("parallel_workers", 2))
        self.memory_opt_switch.setChecked(performance.get("memory_optimization", False))
        
        # Update labels
        self.on_config_changed()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration data."""
        return self.config_data.copy()