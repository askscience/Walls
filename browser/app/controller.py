from __future__ import annotations
from typing import Dict, Any, List, Pattern
from collections import defaultdict
import re
from urllib.parse import quote_plus
from pathlib import Path
import tempfile
import urllib.request
import zipfile
import io

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, QObject, Signal
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo


class SimpleEasyListFilter:
    """
    Minimal EasyList-like filter with network and cosmetic filtering:
    - Supports comments starting with '!'
    - Supports exception rules starting with '@@' for network filtering
    - URL blocking rules subset:
      * '||domain^'  -> blocks any request to that domain or subdomains
      * full/partial patterns (with '*' wildcards) -> substring/regex matching
      * options after '$' are ignored
    - Cosmetic filtering (very simple subset):
      * element hiding rules 'domain##selector' collected per-domain
      * exception element hiding rules 'domain#@#selector' collected per-domain
      * global element hiding rules '##selector' are collected but not injected by default (to avoid huge CSS)
    This is intentionally simple and won't fully match Adblock specification.
    """
    def __init__(self):
        self.active = False
        self.block_patterns: List[Pattern] = []
        self.exception_patterns: List[Pattern] = []
        # Cosmetic filters
        self.cosmetic_by_domain: Dict[str, List[str]] = defaultdict(list)
        self.cosmetic_exceptions: Dict[str, List[str]] = defaultdict(list)
        self.cosmetic_global: List[str] = []

    def _compile_domain_rule(self, domain: str) -> Pattern:
        # convert example.com to regex for host match
        domain = re.escape(domain)
        regex = rf"^https?://([a-z0-9.-]*\.)?{domain}(?:[/:?]|$)"
        return re.compile(regex, re.IGNORECASE)

    def _compile_wildcard_rule(self, pat: str) -> Pattern:
        # Translate filter wildcards to regex
        # '^' roughly as separator; treat as a boundary of [^A-Za-z0-9_.%-]
        pat = pat.replace('^', r'[^A-Za-z0-9_.%-]')
        pat = re.escape(pat)
        pat = pat.replace(r"\*", ".*")
        # Unescape our substituted boundary
        pat = pat.replace(re.escape(r'[^A-Za-z0-9_.%-]'), r'[^A-Za-z0-9_.%-]')
        return re.compile(pat, re.IGNORECASE)

    def _parse_cosmetic_rule(self, line: str) -> None:
        # Handles both '##' and '#@#'
        is_exception = '#@#' in line
        sep = '#@#' if is_exception else '##'
        left, selector = line.split(sep, 1)
        selector = selector.strip()
        if not selector:
            return
        left = left.strip()
        # Global rule (no domains specified)
        if left == '':
            if not is_exception:
                self.cosmetic_global.append(selector)
            return
        # Domain-specific rules: domains separated by commas
        for dom in left.split(','):
            d = dom.strip()
            if not d:
                continue
            if is_exception:
                self.cosmetic_exceptions[d].append(selector)
            else:
                self.cosmetic_by_domain[d].append(selector)

    def load_easylist(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            return {"status": "error", "message": f"Failed to read EasyList: {e}"}

        blocks: List[Pattern] = []
        exceptions: List[Pattern] = []
        cosmetic_by_domain: Dict[str, List[str]] = defaultdict(list)
        cosmetic_exceptions: Dict[str, List[str]] = defaultdict(list)
        cosmetic_global: List[str] = []

        for raw in lines:
            line = raw.strip()
            if not line or line.startswith('!'):
                continue
            # Remove options
            if '$' in line:
                line = line.split('$', 1)[0]
            if not line:
                continue

            # Cosmetic filters
            if '##' in line or '#@#' in line:
                is_exception = '#@#' in line
                sep = '#@#' if is_exception else '##'
                left, selector = line.split(sep, 1)
                selector = selector.strip()
                if selector:
                    left = left.strip()
                    if left == '':
                        if not is_exception:
                            cosmetic_global.append(selector)
                    else:
                        for dom in left.split(','):
                            d = dom.strip()
                            if not d:
                                continue
                            if is_exception:
                                cosmetic_exceptions[d].append(selector)
                            else:
                                cosmetic_by_domain[d].append(selector)
                continue

            is_exception = line.startswith('@@')
            if is_exception:
                line = line[2:]

            if line.startswith('||'):
                dom = line[2:]
                # optionally strip trailing '^'
                if dom.endswith('^'):
                    dom = dom[:-1]
                if dom:
                    pat = self._compile_domain_rule(dom)
                    (exceptions if is_exception else blocks).append(pat)
                continue

            # Treat remaining line as wildcard/url pattern
            pat = self._compile_wildcard_rule(line)
            (exceptions if is_exception else blocks).append(pat)

        self.block_patterns = blocks
        self.exception_patterns = exceptions
        self.cosmetic_by_domain = cosmetic_by_domain
        self.cosmetic_exceptions = cosmetic_exceptions
        self.cosmetic_global = cosmetic_global
        return {"status": "success", "message": f"Loaded {len(blocks)} block rules, {len(exceptions)} exceptions, {sum(len(v) for v in cosmetic_by_domain.values())} cosmetic, {sum(len(v) for v in cosmetic_exceptions.values())} cosmetic exceptions, {len(cosmetic_global)} global cosmetics"}

    def load_easylist_multi(self, paths: List[str]) -> Dict[str, Any]:
        total_blocks: List[Pattern] = []
        total_exceptions: List[Pattern] = []
        cosmetic_by_domain: Dict[str, List[str]] = defaultdict(list)
        cosmetic_exceptions: Dict[str, List[str]] = defaultdict(list)
        cosmetic_global: List[str] = []
        loaded = 0
        for p in paths:
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception:
                continue
            loaded += 1
            for raw in lines:
                line = raw.strip()
                if not line or line.startswith('!'):
                    continue
                if '$' in line:
                    line = line.split('$', 1)[0]
                if not line:
                    continue
                # Cosmetic
                if '##' in line or '#@#' in line:
                    is_exception = '#@#' in line
                    sep = '#@#' if is_exception else '##'
                    left, selector = line.split(sep, 1)
                    selector = selector.strip()
                    if selector:
                        left = left.strip()
                        if left == '':
                            if not is_exception:
                                cosmetic_global.append(selector)
                        else:
                            for dom in left.split(','):
                                d = dom.strip()
                                if not d:
                                    continue
                                if is_exception:
                                    cosmetic_exceptions[d].append(selector)
                                else:
                                    cosmetic_by_domain[d].append(selector)
                    continue
                is_exception = line.startswith('@@')
                if is_exception:
                    line = line[2:]
                if line.startswith('||'):
                    dom = line[2:]
                    if dom.endswith('^'):
                        dom = dom[:-1]
                    if dom:
                        pat = self._compile_domain_rule(dom)
                        (total_exceptions if is_exception else total_blocks).append(pat)
                    continue
                pat = self._compile_wildcard_rule(line)
                (total_exceptions if is_exception else total_blocks).append(pat)
        self.block_patterns = total_blocks
        self.exception_patterns = total_exceptions
        self.cosmetic_by_domain = cosmetic_by_domain
        self.cosmetic_exceptions = cosmetic_exceptions
        self.cosmetic_global = cosmetic_global
        return {"status": "success", "message": f"Loaded {len(total_blocks)} block rules and {len(total_exceptions)} exceptions from {loaded} files; cosmetics: {sum(len(v) for v in cosmetic_by_domain.values())}, exceptions: {sum(len(v) for v in cosmetic_exceptions.values())}, global: {len(cosmetic_global)}"}

    def load_easylist_dir(self, dir_path: str) -> Dict[str, Any]:
        base = Path(dir_path)
        if not base.exists() or not base.is_dir():
            return {"status": "error", "message": f"Invalid directory: {dir_path}"}
        txt_files = [str(p) for p in base.rglob('*.txt')]
        if not txt_files:
            return {"status": "error", "message": f"No .txt filter files found under {dir_path}"}
        return self.load_easylist_multi(txt_files)

    def should_block(self, url: str, first_party: str | None = None) -> bool:
        if not self.active:
            return False
        # Exceptions win
        for r in self.exception_patterns:
            if r.search(url):
                return False
        for r in self.block_patterns:
            if r.search(url):
                return True
        return False

    def _host_suffixes(self, host: str) -> List[str]:
        parts = host.split('.') if host else []
        return ['.'.join(parts[i:]) for i in range(len(parts))]

    def cosmetic_selectors_for_host(self, host: str, include_global_limit: int = 0) -> List[str]:
        """Return cosmetic selectors applicable for host.
        include_global_limit: number of global selectors to include (0 to skip).
        """
        if not host:
            return []
        sels: List[str] = []
        exc: set[str] = set()
        for suf in self._host_suffixes(host):
            if suf in self.cosmetic_by_domain:
                sels.extend(self.cosmetic_by_domain[suf])
            if suf in self.cosmetic_exceptions:
                exc.update(self.cosmetic_exceptions[suf])
        if include_global_limit > 0 and self.cosmetic_global:
            sels.extend(self.cosmetic_global[:include_global_limit])
        # Apply exceptions
        if exc:
            sels = [s for s in sels if s not in exc]
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for s in sels:
            if s in seen:
                continue
            seen.add(s)
            deduped.append(s)
        return deduped

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    def toggle(self) -> bool:
        self.active = not self.active
        return self.active

    def status(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "block_rules": len(self.block_patterns),
            "exception_rules": len(self.exception_patterns),
            "cosmetic_domains": sum(len(v) for v in self.cosmetic_by_domain.values()),
            "cosmetic_exceptions": sum(len(v) for v in self.cosmetic_exceptions.values()),
            "cosmetic_global": len(self.cosmetic_global),
        }


class AdblockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, filt: SimpleEasyListFilter):
        super().__init__()
        self.filt = filt

    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:  # type: ignore[override]
        if not self.filt.active:
            return
        try:
            url = info.requestUrl().toString()
            first = info.firstPartyUrl().host() if info.firstPartyUrl().isValid() else None
            if self.filt.should_block(url, first):
                info.block(True)
        except Exception:
            # Never break loading if our filter fails
            pass


class BrowserController(QObject):
    htmlReady = Signal(str)

    def __init__(self, webview: QWebEngineView):
        super().__init__()
        self.webview = webview
        # Adblock setup
        self._adblock = SimpleEasyListFilter()
        try:
            profile = self.webview.page().profile()
            self._adblock_interceptor = AdblockInterceptor(self._adblock)
            profile.setUrlRequestInterceptor(self._adblock_interceptor)
        except Exception:
            self._adblock_interceptor = None
        # Inject CSS after each page load to remove default body/html margins and apply cosmetic filters
        self.webview.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self, ok: bool):
        if not ok:
            return
        # Base CSS to remove margins
        css = "html, body { margin: 0 !important; padding: 0 !important; }"
        js = f"""
            (function() {{
                try {{
                    let style = document.getElementById('__walls_global_css__');
                    if (!style) {{
                        style = document.createElement('style');
                        style.type = 'text/css';
                        style.id = '__walls_global_css__';
                        document.documentElement.appendChild(style);
                    }}
                    style.innerHTML = {css!r};
                    return true;
                }} catch (e) {{
                    return false;
                }}
            }} )();
        """
        self.webview.page().runJavaScript(js)

        # Inject cosmetic filters for current host if adblock is active
        if self._adblock.active:
            try:
                host = self.webview.url().host()
                # Include a limited number of global selectors to improve coverage
                selectors = self._adblock.cosmetic_selectors_for_host(host, include_global_limit=400)
                if selectors:
                    # Build CSS rules; keep it reasonable in size
                    max_rules = 500  # safety cap
                    rules = []
                    for sel in selectors[:max_rules]:
                        # Make sure we don't break CSS with stray braces
                        s = sel.replace('{', '').replace('}', '')
                        rules.append(f"{s}{{display:none !important; visibility:hidden !important;}}")
                    css_hide = "\n".join(rules)
                    js_hide = f"""
                        (function() {{
                            try {{
                                let style = document.getElementById('__walls_adblock_css__');
                                if (!style) {{
                                    style = document.createElement('style');
                                    style.type = 'text/css';
                                    style.id = '__walls_adblock_css__';
                                    document.documentElement.appendChild(style);
                                }}
                                style.innerHTML = {css_hide!r};
                                return true;
                            }} catch (e) {{
                                return false;
                            }}
                        }})();
                    """
                    self.webview.page().runJavaScript(js_hide)
            except Exception:
                pass

    def _normalize_url(self, url: str) -> QUrl:
        s = (url or '').strip()
        if not s:
            return QUrl()
        # If it's clearly a search query (contains space or no dot), send to DuckDuckGo
        if '://' not in s and not s.startswith(('about:', 'file:', 'data:')):
            if (' ' in s) or ('.' not in s):
                q = quote_plus(s)
                return QUrl(f"https://duckduckgo.com/?q={q}")
            # Otherwise default scheme to https
            s = 'https://' + s
        # fromUserInput handles host/authority and IDN, etc.
        return QUrl.fromUserInput(s)

    def open_url(self, url: str) -> Dict[str, Any]:
        qurl = self._normalize_url(url)
        if not qurl.isValid():
            return {"status": "error", "message": f"Invalid URL: {url}"}
        self.webview.setUrl(qurl)
        return {"status": "success", "message": f"Opening {qurl.toString()}"}

    def back(self) -> Dict[str, Any]:
        self.webview.back()
        return {"status": "success", "message": "Back"}

    def forward(self) -> Dict[str, Any]:
        self.webview.forward()
        return {"status": "success", "message": "Forward"}

    def reload(self) -> Dict[str, Any]:
        self.webview.reload()
        return {"status": "success", "message": "Reload"}

    def current_url(self) -> str:
        return self.webview.url().toString()

    def get_html(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"status": "pending"}

        def callback(html: str):
            result.update({"status": "success", "message": "HTML retrieved", "data": {"html": html}})
            self.htmlReady.emit(html)

        self.webview.page().toHtml(callback)
        return result

    def click_selector(self, selector: str) -> Dict[str, Any]:
        js = f"""
            (function() {{
                const el = document.querySelector({selector!r});
                if (el) {{ el.click(); return true; }}
                return false;
            }} )()
        """
        self.webview.page().runJavaScript(js)
        return {"status": "success", "message": f"Click via selector: {selector}"}

    def click_text(self, text: str) -> Dict[str, Any]:
        # Try clicking buttons or links that contain the given text
        js = f"""
            (function() {{
                function matchesText(el, txt) {{
                    return (el.innerText || el.textContent || '').trim().includes(txt);
                }}
                // Try anchor tags first
                const anchors = Array.from(document.querySelectorAll('a'));
                for (const a of anchors) {{
                    if (matchesText(a, {text!r})) {{ a.click(); return true; }}
                }}
                // Then buttons
                const buttons = Array.from(document.querySelectorAll('button, input[type=\"button\"], input[type=\"submit\"]'));
                for (const b of buttons) {{
                    if (matchesText(b, {text!r}) || (b.value && b.value.includes({text!r}))) {{ b.click(); return true; }}
                }}
                return false;
            }} )()
        """
        self.webview.page().runJavaScript(js)
        return {"status": "success", "message": f"Click by text: {text}"}

    # Adblock control methods
    def adblock_enable(self) -> Dict[str, Any]:
        self._adblock.enable()
        return {"status": "success", "message": "Adblock enabled", "data": self._adblock.status()}

    def adblock_disable(self) -> Dict[str, Any]:
        self._adblock.disable()
        return {"status": "success", "message": "Adblock disabled", "data": self._adblock.status()}

    def adblock_toggle(self) -> Dict[str, Any]:
        state = self._adblock.toggle()
        return {"status": "success", "message": f"Adblock {'enabled' if state else 'disabled'}", "data": self._adblock.status()}

    def adblock_status(self) -> Dict[str, Any]:
        return {"status": "success", "message": "Adblock status", "data": self._adblock.status()}

    def adblock_load(self, path: str) -> Dict[str, Any]:
        res = self._adblock.load_easylist(path)
        return res

    def adblock_load_dir(self, path: str) -> Dict[str, Any]:
        res = self._adblock.load_easylist_dir(path)
        return res

    def adblock_fetch_easylist(self, url: str | None = None) -> Dict[str, Any]:
        """Download the EasyList repo ZIP and load all .txt rules from it.
        Uses stdlib urllib + zipfile. Returns status dict.
        """
        repo_zip_url = url or "https://github.com/easylist/easylist/archive/refs/heads/master.zip"
        try:
            # Download into memory (zip ~10-20MB)
            with urllib.request.urlopen(repo_zip_url) as resp:
                data = resp.read()
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                # Extract to a temp dir
                with tempfile.TemporaryDirectory(prefix="walls_easylist_") as tmpdir:
                    zf.extractall(tmpdir)
                    # Find the top-level extracted directory
                    tmp_path = Path(tmpdir)
                    candidates = [p for p in tmp_path.iterdir() if p.is_dir()]
                    if not candidates:
                        return {"status": "error", "message": "Failed to extract EasyList archive"}
                    # Use first directory
                    extracted_root = candidates[0]
                    # Load every .txt file under the extracted root
                    res = self._adblock.load_easylist_dir(str(extracted_root))
                    return res
        except Exception as e:
            return {"status": "error", "message": f"Failed to fetch/load EasyList: {e}"}