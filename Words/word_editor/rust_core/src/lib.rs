use pyo3::exceptions::{PyIOError, PyIndexError};
use pyo3::prelude::*;
use quick_xml::events::Event;
use quick_xml::Reader;
use std::fs::File;
use std::io::{Read, Write};
use std::path::Path;
use std::sync::{Arc, Mutex};
use zip::write::FileOptions;
use zip::{CompressionMethod, ZipArchive, ZipWriter};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use indexmap::IndexMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextStyle {
    pub bold: bool,
    pub italic: bool,
    pub underline: bool,
    pub font_size: Option<String>,
    pub font_family: Option<String>,
    pub color: Option<String>,
}

impl Default for TextStyle {
    fn default() -> Self {
        Self {
            bold: false,
            italic: false,
            underline: false,
            font_size: None,
            font_family: None,
            color: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextRun {
    pub text: String,
    pub style: TextStyle,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DocumentElement {
    Paragraph { runs: Vec<TextRun> },
    Heading { level: u8, runs: Vec<TextRun> },
    List { items: Vec<Vec<TextRun>>, ordered: bool },
    Table { rows: Vec<Vec<Vec<TextRun>>> },
    LineBreak,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StructuredDocument {
    pub elements: Vec<DocumentElement>,
    pub styles: HashMap<String, TextStyle>,
}

impl StructuredDocument {
    pub fn new() -> Self {
        Self {
            elements: Vec::new(),
            styles: HashMap::new(),
        }
    }

    pub fn to_html(&self) -> String {
        let mut html = String::new();
        for element in &self.elements {
            match element {
                DocumentElement::Paragraph { runs } => {
                    html.push_str("<p>");
                    for run in runs {
                        html.push_str(&self.run_to_html(run));
                    }
                    html.push_str("</p>\n");
                }
                DocumentElement::Heading { level, runs } => {
                    html.push_str(&format!("<h{}>", level));
                    for run in runs {
                        html.push_str(&self.run_to_html(run));
                    }
                    html.push_str(&format!("</h{}>\n", level));
                }
                DocumentElement::List { items, ordered } => {
                    let tag = if *ordered { "ol" } else { "ul" };
                    html.push_str(&format!("<{}>", tag));
                    for item in items {
                        html.push_str("<li>");
                        for run in item {
                            html.push_str(&self.run_to_html(run));
                        }
                        html.push_str("</li>");
                    }
                    html.push_str(&format!("</{}>", tag));
                }
                DocumentElement::Table { rows } => {
                    html.push_str("<table>");
                    for row in rows {
                        html.push_str("<tr>");
                        for cell in row {
                            html.push_str("<td>");
                            for run in cell {
                                html.push_str(&self.run_to_html(run));
                            }
                            html.push_str("</td>");
                        }
                        html.push_str("</tr>");
                    }
                    html.push_str("</table>");
                }
                DocumentElement::LineBreak => {
                    html.push_str("<br/>\n");
                }
            }
        }
        html
    }

    fn run_to_html(&self, run: &TextRun) -> String {
        let mut result = xml_escape(&run.text);
        
        if run.style.bold {
            result = format!("<b>{}</b>", result);
        }
        if run.style.italic {
            result = format!("<i>{}</i>", result);
        }
        if run.style.underline {
            result = format!("<u>{}</u>", result);
        }
        
        result
    }

    pub fn to_plain_text(&self) -> String {
        let mut text = String::new();
        for element in &self.elements {
            match element {
                DocumentElement::Paragraph { runs } | DocumentElement::Heading { runs, .. } => {
                    for run in runs {
                        text.push_str(&run.text);
                    }
                    text.push('\n');
                }
                DocumentElement::List { items, .. } => {
                    for item in items {
                        for run in item {
                            text.push_str(&run.text);
                        }
                        text.push('\n');
                    }
                }
                DocumentElement::Table { rows } => {
                    for row in rows {
                        for cell in row {
                            for run in cell {
                                text.push_str(&run.text);
                            }
                            text.push('\t');
                        }
                        text.push('\n');
                    }
                }
                DocumentElement::LineBreak => {
                    text.push('\n');
                }
            }
        }
        text
    }
}

fn ext_lower(path: &str) -> String {
    Path::new(path)
        .extension()
        .and_then(|s| s.to_str())
        .unwrap_or("")
        .to_ascii_lowercase()
}

fn local_name(name: &[u8]) -> &[u8] {
    if let Some(pos) = name.iter().position(|&b| b == b':') {
        &name[pos + 1..]
    } else {
        name
    }
}

fn read_zip_file_to_string<R: Read>(mut reader: R) -> std::io::Result<String> {
    let mut s = String::new();
    reader.read_to_string(&mut s)?;
    Ok(s)
}

fn read_docx_text(path: &str) -> std::io::Result<String> {
    let f = File::open(path)?;
    let mut zip = ZipArchive::new(f)?;
    let mut docxml = zip.by_name("word/document.xml")?;
    let xml = read_zip_file_to_string(&mut docxml)?;

    let mut reader = Reader::from_str(&xml);
    reader.trim_text(true);
    let mut buf = Vec::new();
    let mut out = String::new();

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(_)) => {}
            Ok(Event::Empty(e)) => {
                if local_name(e.name().as_ref()) == b"p" {
                    out.push('\n');
                }
            }
            Ok(Event::End(e)) => {
                if local_name(e.name().as_ref()) == b"p" {
                    out.push('\n');
                }
            }
            Ok(Event::Text(t)) => {
                match t.unescape() {
                    Ok(cow) => out.push_str(&cow),
                    Err(_) => out.push_str(&String::from_utf8_lossy(t.as_ref())),
                }
            }
            Ok(Event::CData(t)) => {
                let txt = String::from_utf8_lossy(t.as_ref());
                out.push_str(&txt);
            }
            Ok(Event::Eof) => break,
            Err(e) => return Err(std::io::Error::new(std::io::ErrorKind::Other, e.to_string())),
            _ => {}
        }
        buf.clear();
    }

    Ok(out)
}

fn xml_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

fn write_docx_text(path: &str, text: &str) -> std::io::Result<()> {
    let mut f = File::create(path)?;
    let mut zip = ZipWriter::new(&mut f);

    let deflated = FileOptions::default().compression_method(CompressionMethod::Deflated);

    // [Content_Types].xml
    let content_types = r#"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>
</Types>"#;
    zip.start_file("[Content_Types].xml", deflated)?;
    zip.write_all(content_types.as_bytes())?;

    // _rels/.rels
    let rels_root = r#"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>
</Relationships>"#;
    zip.start_file("_rels/.rels", deflated)?;
    zip.write_all(rels_root.as_bytes())?;

    // word/document.xml
    let mut body = String::new();
    for line in text.split_terminator('\n') {
        if line.is_empty() {
            body.push_str("<w:p/>");
        } else {
            body.push_str("<w:p><w:r><w:t>");
            body.push_str(&xml_escape(line));
            body.push_str("</w:t></w:r></w:p>");
        }
    }

    let document_xml = format!(
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\
<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">\
<w:body>{}</w:body>\
</w:document>",
        body
    );
    zip.start_file("word/document.xml", deflated)?;
    zip.write_all(document_xml.as_bytes())?;

    zip.finish()?;
    Ok(())
}

fn read_odt_structured(path: &str) -> std::io::Result<StructuredDocument> {
    let f = File::open(path)?;
    let mut zip = ZipArchive::new(f)?;
    
    // Read styles.xml first to get style definitions
    let mut styles = HashMap::new();
    if let Ok(mut styles_file) = zip.by_name("styles.xml") {
        let styles_xml = read_zip_file_to_string(&mut styles_file)?;
        styles = parse_odt_styles(&styles_xml);
    }
    
    // Read content.xml
    let mut content = zip.by_name("content.xml")?;
    let xml = read_zip_file_to_string(&mut content)?;
    
    let mut doc = StructuredDocument::new();
    doc.styles = styles;
    
    let mut reader = Reader::from_str(&xml);
    reader.trim_text(true);
    let mut buf = Vec::new();
    
    let mut in_body = false;
    let mut current_element: Option<DocumentElement> = None;
    let mut current_runs: Vec<TextRun> = Vec::new();
    let mut current_style = TextStyle::default();
    let mut text_buffer = String::new();
    let mut element_stack: Vec<String> = Vec::new();
    let mut table_rows: Vec<Vec<Vec<TextRun>>> = Vec::new();
    let mut current_row: Vec<Vec<TextRun>> = Vec::new();
    let mut list_items: Vec<Vec<TextRun>> = Vec::new();
    
    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(e)) => {
                let element_name = e.name();
                let name = String::from_utf8_lossy(local_name(element_name.as_ref()));
                element_stack.push(name.to_string());
                
                match name.as_ref() {
                    "body" => in_body = true,
                    "p" => {
                        current_runs.clear();
                        current_style = TextStyle::default();
                        text_buffer.clear();
                    }
                    "h" => {
                        current_runs.clear();
                        current_style = TextStyle::default();
                        text_buffer.clear();
                    }
                    "span" => {
                        // Check for style attributes
                        for attr in e.attributes() {
                            if let Ok(attr) = attr {
                                if attr.key.as_ref() == b"text:style-name" {
                                    let style_str = String::from_utf8_lossy(&attr.value);
                                    if let Some(style) = doc.styles.get(&style_str.to_string()) {
                                        current_style = style.clone();
                                    }
                                }
                            }
                        }
                    }
                    "list" => {
                        list_items.clear();
                    }
                    "list-item" => {
                        current_runs.clear();
                    }
                    "table" => {
                        table_rows.clear();
                    }
                    "table-row" => {
                        current_row.clear();
                    }
                    "table-cell" => {
                        current_runs.clear();
                    }
                    _ => {}
                }
            }
            Ok(Event::End(e)) => {
                let element_name = e.name();
                let name = String::from_utf8_lossy(local_name(element_name.as_ref()));
                element_stack.pop();
                
                if !in_body {
                    buf.clear();
                    continue;
                }
                
                match name.as_ref() {
                    "p" => {
                        if !text_buffer.is_empty() {
                            current_runs.push(TextRun {
                                text: text_buffer.clone(),
                                style: current_style.clone(),
                            });
                            text_buffer.clear();
                        }
                        if !current_runs.is_empty() {
                            doc.elements.push(DocumentElement::Paragraph { runs: current_runs.clone() });
                        }
                        current_runs.clear();
                    }
                    "h" => {
                        if !text_buffer.is_empty() {
                            current_runs.push(TextRun {
                                text: text_buffer.clone(),
                                style: current_style.clone(),
                            });
                            text_buffer.clear();
                        }
                        if !current_runs.is_empty() {
                            // Try to get heading level from outline-level attribute
                            let level = 1; // Default level, could be enhanced to parse from XML
                            doc.elements.push(DocumentElement::Heading { level, runs: current_runs.clone() });
                        }
                        current_runs.clear();
                    }
                    "span" => {
                        if !text_buffer.is_empty() {
                            current_runs.push(TextRun {
                                text: text_buffer.clone(),
                                style: current_style.clone(),
                            });
                            text_buffer.clear();
                        }
                        current_style = TextStyle::default();
                    }
                    "list-item" => {
                        if !text_buffer.is_empty() {
                            current_runs.push(TextRun {
                                text: text_buffer.clone(),
                                style: current_style.clone(),
                            });
                            text_buffer.clear();
                        }
                        list_items.push(current_runs.clone());
                        current_runs.clear();
                    }
                    "list" => {
                        if !list_items.is_empty() {
                            doc.elements.push(DocumentElement::List { items: list_items.clone(), ordered: false });
                        }
                        list_items.clear();
                    }
                    "table-cell" => {
                        if !text_buffer.is_empty() {
                            current_runs.push(TextRun {
                                text: text_buffer.clone(),
                                style: current_style.clone(),
                            });
                            text_buffer.clear();
                        }
                        current_row.push(current_runs.clone());
                        current_runs.clear();
                    }
                    "table-row" => {
                        table_rows.push(current_row.clone());
                        current_row.clear();
                    }
                    "table" => {
                        if !table_rows.is_empty() {
                            doc.elements.push(DocumentElement::Table { rows: table_rows.clone() });
                        }
                        table_rows.clear();
                    }
                    "line-break" => {
                        doc.elements.push(DocumentElement::LineBreak);
                    }
                    _ => {}
                }
            }
            Ok(Event::Text(t)) => {
                if in_body {
                    match t.unescape() {
                        Ok(cow) => text_buffer.push_str(&cow),
                        Err(_) => text_buffer.push_str(&String::from_utf8_lossy(t.as_ref())),
                    }
                }
            }
            Ok(Event::CData(t)) => {
                if in_body {
                    let txt = String::from_utf8_lossy(t.as_ref());
                    text_buffer.push_str(&txt);
                }
            }
            Ok(Event::Eof) => break,
            Err(e) => return Err(std::io::Error::new(std::io::ErrorKind::Other, e.to_string())),
            _ => {}
        }
        buf.clear();
    }
    
    Ok(doc)
}

fn parse_odt_styles(styles_xml: &str) -> HashMap<String, TextStyle> {
    let mut styles = HashMap::new();
    let mut reader = Reader::from_str(styles_xml);
    reader.trim_text(true);
    let mut buf = Vec::new();
    
    let mut current_style_name = String::new();
    let mut current_style = TextStyle::default();
    let mut in_style = false;
    
    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(e)) => {
                let element_name = e.name();
                let name = String::from_utf8_lossy(local_name(element_name.as_ref()));
                match name.as_ref() {
                    "style" => {
                        for attr in e.attributes() {
                            if let Ok(attr) = attr {
                                if attr.key.as_ref() == b"style:name" {
                                    current_style_name = String::from_utf8_lossy(&attr.value).to_string();
                                    current_style = TextStyle::default();
                                    in_style = true;
                                }
                            }
                        }
                    }
                    "text-properties" if in_style => {
                        // Parse text formatting properties
                        for attr in e.attributes() {
                            if let Ok(attr) = attr {
                                match attr.key.as_ref() {
                                    b"fo:font-weight" => {
                                        let weight_val = String::from_utf8_lossy(&attr.value);
                                        current_style.bold = weight_val == "bold" || weight_val == "700";
                                    }
                                    b"fo:font-style" => {
                                        let style_val = String::from_utf8_lossy(&attr.value);
                                        current_style.italic = style_val == "italic";
                                    }
                                    b"style:text-underline-style" => {
                                        let underline_val = String::from_utf8_lossy(&attr.value);
                                        current_style.underline = underline_val != "none" && !underline_val.is_empty();
                                    }
                                    b"fo:font-size" => {
                                        current_style.font_size = Some(String::from_utf8_lossy(&attr.value).to_string());
                                    }
                                    b"fo:font-family" => {
                                        current_style.font_family = Some(String::from_utf8_lossy(&attr.value).to_string());
                                    }
                                    b"fo:color" => {
                                        current_style.color = Some(String::from_utf8_lossy(&attr.value).to_string());
                                    }
                                    _ => {}
                                }
                            }
                        }
                    }
                    _ => {}
                }
            }
            Ok(Event::End(e)) => {
                let element_name = e.name();
                let name = String::from_utf8_lossy(local_name(element_name.as_ref()));
                if name == "style" && in_style {
                    styles.insert(current_style_name.clone(), current_style.clone());
                    in_style = false;
                    current_style_name.clear();
                }
            }
            Ok(Event::Eof) => break,
            Err(_) => break,
            _ => {}
        }
        buf.clear();
    }
    
    // Add some common default styles
    styles.insert("Bold".to_string(), TextStyle { bold: true, ..Default::default() });
    styles.insert("Italic".to_string(), TextStyle { italic: true, ..Default::default() });
    styles.insert("Underline".to_string(), TextStyle { underline: true, ..Default::default() });
    
    styles
}

fn read_odt_text(path: &str) -> std::io::Result<String> {
    let structured = read_odt_structured(path)?;
    Ok(structured.to_plain_text())
}

fn write_odt_text(path: &str, text: &str) -> std::io::Result<()> {
    let mut f = File::create(path)?;
    let mut zip = ZipWriter::new(&mut f);

    // The mimetype entry MUST be the first entry and stored (no compression)
    let stored = FileOptions::default().compression_method(CompressionMethod::Stored);
    zip.start_file("mimetype", stored)?;
    zip.write_all(b"application/vnd.oasis.opendocument.text")?;

    let deflated = FileOptions::default().compression_method(CompressionMethod::Deflated);

    // content.xml
    let mut body = String::new();
    for line in text.split_terminator('\n') {
        body.push_str("<text:p>");
        body.push_str(&xml_escape(line));
        body.push_str("</text:p>");
    }

    let content_xml = format!(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\
<office:document-content \
 xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\" \
 xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\">\
  <office:body>\
    <office:text>{}</office:text>\
  </office:body>\
</office:document-content>",
        body
    );
    zip.start_file("content.xml", deflated)?;
    zip.write_all(content_xml.as_bytes())?;

    // META-INF/manifest.xml
    let manifest_xml = r#"<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<manifest:manifest xmlns:manifest=\"urn:oasis:names:tc:opendocument:xmlns:manifest:1.0\">
  <manifest:file-entry manifest:media-type=\"application/vnd.oasis.opendocument.text\" manifest:full-path=\"/\"/>
  <manifest:file-entry manifest:media-type=\"text/xml\" manifest:full-path=\"content.xml\"/>
</manifest:manifest>"#;
    zip.start_file("META-INF/manifest.xml", deflated)?;
    zip.write_all(manifest_xml.as_bytes())?;

    zip.finish()?;
    Ok(())
}

#[pyclass]
pub struct Document {
    inner: Arc<Mutex<String>>, // plain text representation
    structured: Arc<Mutex<Option<StructuredDocument>>>, // structured representation
}

#[pymethods]
impl Document {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: Arc::new(Mutex::new(String::new())),
            structured: Arc::new(Mutex::new(None)),
        }
    }

    pub fn set_text(&self, text: String) {
        if let Ok(mut guard) = self.inner.lock() {
            *guard = text;
        }
        // Clear structured representation when text is manually set
        *self.structured.lock().unwrap() = None;
    }

    pub fn insert_text(&self, offset: usize, text: String) -> PyResult<()> {
        let mut guard = self.inner.lock().unwrap();
        if offset > guard.len() {
            return Err(PyErr::new::<PyIndexError, _>("offset out of bounds"));
        }
        guard.insert_str(offset, &text);
        Ok(())
    }

    pub fn get_text(&self) -> String {
        self.inner.lock().unwrap().clone()
    }

    pub fn clear(&self) {
        if let Ok(mut guard) = self.inner.lock() {
            guard.clear();
        }
        // Clear structured representation when text is cleared
        *self.structured.lock().unwrap() = None;
    }

    pub fn load_odt_structured(&self, path: String) -> PyResult<()> {
        match read_odt_structured(&path) {
            Ok(structured_doc) => {
                *self.inner.lock().unwrap() = structured_doc.to_plain_text();
                *self.structured.lock().unwrap() = Some(structured_doc);
                Ok(())
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                "Failed to read ODT file: {}",
                e
            ))),
        }
    }

    pub fn get_html(&self) -> String {
        if let Some(structured) = self.structured.lock().unwrap().as_ref() {
            structured.to_html()
        } else {
            // Fallback to plain text wrapped in <p> tags
            let text = self.inner.lock().unwrap().clone();
            if text.is_empty() {
                String::new()
            } else {
                format!("<p>{}</p>", text.replace('\n', "<br/>"))
            }
        }
    }

    pub fn has_structured_content(&self) -> bool {
        self.structured.lock().unwrap().is_some()
    }

    pub fn open(&self, path: String) -> PyResult<()> {
        let ext = ext_lower(&path);
        let text = match ext.as_str() {
            "docx" => read_docx_text(&path)
                .map_err(|e| PyErr::new::<PyIOError, _>(format!("{}", e)))?,
            "odt" => read_odt_text(&path)
                .map_err(|e| PyErr::new::<PyIOError, _>(format!("{}", e)))?,
            _ => std::fs::read_to_string(&path)
                .map_err(|e| PyErr::new::<PyIOError, _>(format!("{}", e)))?,
        };
        self.set_text(text);
        Ok(())
    }

    pub fn save(&self, path: String) -> PyResult<()> {
        let ext = ext_lower(&path);
        let content = self.get_text();
        match ext.as_str() {
            "docx" => write_docx_text(&path, &content)
                .map_err(|e| PyErr::new::<PyIOError, _>(format!("{}", e)))?,
            "odt" => write_odt_text(&path, &content)
                .map_err(|e| PyErr::new::<PyIOError, _>(format!("{}", e)))?,
            _ => std::fs::write(&path, content)
                .map_err(|e| PyErr::new::<PyIOError, _>(format!("{}", e)))?,
        }
        Ok(())
    }
}

#[pyfunction]
fn read_odt(path: String) -> PyResult<String> {
    match read_odt_text(&path) {
        Ok(content) => Ok(content),
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
            "Failed to read ODT file: {}",
            e
        ))),
    }
}

#[pyfunction]
fn read_odt_structured_json(path: String) -> PyResult<String> {
    match read_odt_structured(&path) {
        Ok(structured_doc) => {
            match serde_json::to_string(&structured_doc) {
                Ok(json) => Ok(json),
                Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Failed to serialize structured document: {}",
                    e
                ))),
            }
        }
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
            "Failed to read ODT file: {}",
            e
        ))),
    }
}

#[pymodule]
fn word_core(_py: Python, m: &Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
    m.add_class::<Document>()?;
    m.add_function(wrap_pyfunction!(read_odt, m)?)?;
    m.add_function(wrap_pyfunction!(read_odt_structured_json, m)?)?;
    Ok(())
}