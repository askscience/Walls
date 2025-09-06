"""RAG Integration Service

Integration with the main RAG system using subprocess calls to main.py --query
This service provides a Qt-compatible interface to the RAG CLI.
"""

import sys
import os
import re
import subprocess
import json
import os
import sys
from typing import Optional
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread

# Get the main RAG directory path
rag_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'rag')
rag_main_path = os.path.join(rag_path, 'main.py')


class RAGInitWorker(QObject):
    """Worker for initializing RAG service in a separate thread."""
    
    progress = Signal(str)
    success = Signal()
    error = Signal(str)
    
    def __init__(self, rag_main_path: str):
        super().__init__()
        self.rag_main_path = rag_main_path
    
    def run(self):
        """Run the initialization process."""
        try:
            self.progress.emit("Verifying RAG system availability...")
            
            # Check if RAG main.py exists
            if not os.path.exists(self.rag_main_path):
                raise FileNotFoundError(f"RAG main.py not found at {self.rag_main_path}")
            
            self.progress.emit("Testing RAG system...")
            
            # Lightweight health check to avoid heavy initialization
            test_cmd = [sys.executable, self.rag_main_path, '--health']
            test_process = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=10  # quick check
            )
            
            if test_process.returncode != 0 or 'OK' not in (test_process.stdout or ''):
                raise RuntimeError(f"RAG system health check failed: {test_process.stderr or test_process.stdout}")
            
            self.success.emit()
            
        except Exception as e:
            self.error.emit(str(e))


class RAGQueryWorker(QObject):
    """Worker thread for handling RAG queries using subprocess calls to main.py --query."""
    
    response_chunk = Signal(str)  # Signal for streaming response chunks
    response_finished = Signal(str)  # Signal when response is complete
    error_occurred = Signal(str)  # Signal for errors
    
    def __init__(self, rag_main_path: str, query: str, hide_think: bool = True):
        super().__init__()
        self.rag_main_path = rag_main_path
        self.query = query
        self.full_response = ""
        # Manage DeepSeek-style reasoning tags
        self._hide_think = hide_think
        self._inside_think = False
        self._stream_buf = ""  # small lookbehind buffer to handle tag boundaries

    def _remove_think_from_text(self, text: str) -> str:
        """Remove <think>...</think> blocks from text, preserving other content.
        Maintains self._inside_think state across calls for streaming correctness.
        """
        if not self._hide_think or not text:
            return text
        out_chars = []
        i = 0
        while i < len(text):
            if not self._inside_think:
                if text.startswith("<think>", i):
                    self._inside_think = True
                    i += 7
                    continue
                if text.startswith("</think>", i):
                    # stray closing tag
                    i += 8
                    continue
                out_chars.append(text[i])
                i += 1
            else:
                # currently inside a <think> block, skip until we see closing tag
                if text.startswith("</think>", i):
                    self._inside_think = False
                    i += 8
                    continue
                i += 1
        return "".join(out_chars)

    def _filter_think_streaming(self, chunk: str) -> str:
        """Filter a streaming chunk, keeping a small buffer to catch tag boundaries.
        We hold back the last up to 8 chars (max tag length) to avoid emitting
        partial tag starts. Call _flush_streaming_filter() at the end to emit leftovers.
        """
        if not self._hide_think:
            return chunk
        if not chunk:
            return ""
        # Append new chunk to buffer
        self._stream_buf += chunk
        s = self._stream_buf
        # Keep a lookbehind window of 8 chars (covers '</think>')
        emit_len = max(0, len(s) - 8)
        to_process = s[:emit_len]
        # Keep the tail as buffer for next chunk
        self._stream_buf = s[emit_len:]
        return self._remove_think_from_text(to_process)

    def _flush_streaming_filter(self) -> str:
        """Flush any remaining buffered chars at the end of streaming."""
        if not self._hide_think:
            leftover = self._stream_buf
            self._stream_buf = ""
            return leftover
        leftover = self._remove_think_from_text(self._stream_buf)
        self._stream_buf = ""
        return leftover

    def _strip_think_blocks(self, text: str) -> str:
        """Non-streaming removal of <think>...</think> blocks using regex."""
        if not self._hide_think or not text:
            return text
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    def run_query(self):
        """Execute the RAG query using subprocess call to main.py --query."""
        try:
            # Prepare the subprocess command
            cmd = [sys.executable, self.rag_main_path, '--query', self.query]
            
            # Execute the subprocess with timeout protection
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Process will be handled with basic exception handling
            
            # Read output line by line for pseudo-streaming
            output_lines = []
            response_started = False
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.rstrip('\n')
                    # Skip safety-policy and command-execution noise lines entirely
                    noise_markers = (
                        "Bash command detected but rejected by safety policy",
                        "Rejected command:",
                        "--- Detected bash command from LLM ---",
                        "--- Command Output (stdout) ---",
                        "--- Command Output (stderr) ---",
                        "--- Command Exit Code:",
                        "Processing radio search results with AI...",
                        "--- Radio Search Results ---",
                    )
                    if any(marker in line for marker in noise_markers):
                        continue
                    
                    output_lines.append(line)
                    
                    # Skip process messages and only emit actual response content
                    if line.startswith("Response:"):
                        response_started = True
                        continue  # Skip the "Response:" line itself
                    elif line in ["Loading index for querying...", "Asking LLM..."] or line.startswith("Query: "):
                        continue  # Skip process messages
                    elif response_started:
                        # This is actual response content
                        filtered = self._filter_think_streaming(line + '\n')
                        if filtered:
                            self.full_response += filtered
                            self.response_chunk.emit(filtered)
            
            # Wait for process to complete
            process.wait()
            
            # Process completed normally
            
            # Check for errors
            if process.returncode != 0:
                stderr_output = process.stderr.read()
                self.error_occurred.emit(f"RAG subprocess failed: {stderr_output}")
                return
            
            # Flush any remaining buffer
            tail = self._flush_streaming_filter()
            if tail:
                self.full_response += tail
                self.response_chunk.emit(tail)
            
            # If no streaming output was captured, get the full output and filter process messages
            if not self.full_response:
                # Filter out process messages from the full output
                response_lines = []
                response_started = False
                for line in output_lines:
                    if line.startswith("Response:"):
                        response_started = True
                        continue
                    elif line in ["Loading index for querying...", "Asking LLM..."] or line.startswith("Query: "):
                        continue
                    elif response_started:
                        response_lines.append(line)
                
                if response_lines:
                    full_output = '\n'.join(response_lines)
                    self.full_response = self._strip_think_blocks(full_output)
                    if self.full_response:
                        self.response_chunk.emit(self.full_response)
            
            # Emit finished signal
            self.response_finished.emit(self.full_response)
            
        except TimeoutError as e:
            self.error_occurred.emit(f"RAG query timed out: {str(e)}")
        except Exception as e:
            # Handle other exceptions
            self.error_occurred.emit(f"Error during subprocess query: {str(e)}")


class RAGIntegrationService(QObject):
    """Service that integrates with the main RAG system using subprocess calls."""
    
    response_chunk = Signal(str)  # Signal for streaming response chunks
    response_finished = Signal(str)  # Signal when response is complete
    error_occurred = Signal(str)  # Signal for errors
    initialization_progress = Signal(str)  # Signal for initialization progress
    
    def __init__(self):
        super().__init__()
        self.rag_main_path = rag_main_path
        self.worker = None
        self.worker_thread = None
        self.is_initialized = False
        self._initialization_in_progress = False
        # Preference: hide or show <think> blocks
        self.hide_think = True

    def set_hide_think(self, hide: bool) -> None:
        """Configure whether to hide <think> reasoning content in outputs."""
        self.hide_think = bool(hide)

    def initialize_async(self) -> None:
        """Initialize the RAG service by verifying main.py availability."""
        if self._initialization_in_progress or self.is_initialized:
            return
            
        self._initialization_in_progress = True
        
        # Create initialization worker and thread
        self.init_worker = RAGInitWorker(self.rag_main_path)
        self.init_thread = QThread()
        
        # Move worker to thread
        self.init_worker.moveToThread(self.init_thread)
        
        # Connect signals
        self.init_worker.progress.connect(self.initialization_progress.emit)
        self.init_worker.success.connect(self._on_init_success)
        self.init_worker.error.connect(self._on_init_error)
        
        # Connect thread signals
        self.init_thread.started.connect(self.init_worker.run)
        self.init_worker.success.connect(self.init_thread.quit)
        self.init_worker.error.connect(self.init_thread.quit)
        self.init_thread.finished.connect(self._cleanup_init_thread)
        
        # Start the thread
        self.init_thread.start()
    
    def _on_init_success(self):
        """Handle successful initialization."""
        self.is_initialized = True
        self._initialization_in_progress = False
        self.initialization_progress.emit("RAG service ready!")
    
    def _on_init_error(self, error_message: str):
        """Handle initialization error."""
        self._initialization_in_progress = False
        self.error_occurred.emit(f"Failed to initialize RAG service: {error_message}")
    
    def _cleanup_init_thread(self):
        """Clean up initialization thread resources."""
        if hasattr(self, 'init_worker'):
            self.init_worker = None
        if hasattr(self, 'init_thread'):
            self.init_thread = None

    def initialize(self) -> bool:
        """Synchronous initialization (for backward compatibility)."""
        if self.is_initialized:
            return True
            
        try:
            # Check if RAG main.py exists
            if not os.path.exists(self.rag_main_path):
                self.error_occurred.emit(f"RAG main.py not found at {self.rag_main_path}")
                return False
            
            # Lightweight health check to avoid heavy initialization
            test_cmd = [sys.executable, self.rag_main_path, '--health']
            test_process = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=10  # quick check
            )
            
            if test_process.returncode != 0 or 'OK' not in (test_process.stdout or ''):
                self.error_occurred.emit(f"RAG system health check failed: {test_process.stderr or test_process.stdout}")
                return False
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize RAG service: {str(e)}")
            return False

    def query(self, question: str):
        """Execute a query against the main RAG system."""
        if not self.is_initialized:
            if not self._initialization_in_progress:
                self.error_occurred.emit("RAG service not initialized. Call initialize_async() first.")
            else:
                self.error_occurred.emit("RAG service is still initializing. Please wait...")
            return
        
        if not question.strip():
            self.error_occurred.emit("Query cannot be empty")
            return
        
        # Clean up previous worker if exists
        self.cleanup_worker()
        
        # Create worker and thread using subprocess calls to main.py
        self.worker = RAGQueryWorker(self.rag_main_path, question, hide_think=self.hide_think)
        self.worker_thread = QThread()
        
        # Move worker to thread
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.response_chunk.connect(self.response_chunk.emit)
        self.worker.response_finished.connect(self.response_finished.emit)
        self.worker.error_occurred.connect(self.error_occurred.emit)
        
        # Connect thread signals
        self.worker_thread.started.connect(self.worker.run_query)
        self.worker.response_finished.connect(self.worker_thread.quit)
        self.worker.error_occurred.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.cleanup_worker)
        
        # Start the thread
        self.worker_thread.start()

    def cleanup_worker(self):
        """Clean up worker thread resources."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        self.worker = None
        self.worker_thread = None
    
    def is_ready(self) -> bool:
        """Check if the service is ready to handle queries."""
        return self.is_initialized
    
    def is_initializing(self) -> bool:
        """Check if the service is currently initializing."""
        return self._initialization_in_progress