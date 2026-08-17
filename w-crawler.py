#!/usr/bin/env python3

import json
import re
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


# ============================================================
# W-Crawler v1.0
# Terminal Web Crawler
# ============================================================

VERSION = "1.0"

BANNER = r"""
 __        __        ____               _
 \ \      / /__     / ___|_ __ __ __ _| | ___ _ __
  \ \ /\ / / _ \   | |   | '__/ _` | |/ _ \ '__|
   \ V  V / (_) |  | |___| | | (_| | |  __/ |
    \_/\_/ \___/    \____|_|  \__,_|_|\___|_|

              W-Crawler v1.0
          Web Discovery & Crawler
"""

HEADERS = {
    "User-Agent": "W-Crawler/1.0 (+web-crawler)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

PHONE_REGEX = re.compile(
    r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"
)


class WCrawler:
    def __init__(
        self,
        start_url,
        max_depth=2,
        threads=5,
        timeout=10,
        delay=0.0,
        respect_robots=True,
    ):
        self.start_url = self.normalize_url(start_url)
        parsed = urlparse(self.start_url)

        self.scheme = parsed.scheme
        self.domain = parsed.netloc.lower()

        self.max_depth = max_depth
        self.threads = max(1, threads)
        self.timeout = timeout
        self.delay = max(0.0, delay)
        self.respect_robots = respect_robots

        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        self.visited = set()
        self.discovered = set()

        self.results = []
        self.emails = set()
        self.phones = set()

        self.lock = __import__("threading").Lock()

        self.robot_parser = None

        self.stats = {
            "queued": 0,
            "visited": 0,
            "success": 0,
            "redirects": 0,
            "errors": 0,
            "non_html": 0,
            "links": 0,
        }

    # --------------------------------------------------------
    # URL helpers
    # --------------------------------------------------------

    @staticmethod
    def normalize_url(url):
        url = urldefrag(url.strip())[0]

        parsed = urlparse(url)

        if not parsed.scheme:
            url = "https://" + url

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            raise ValueError("Sadece HTTP/HTTPS URL'leri destekleniyor.")

        return url.rstrip("/") if parsed.path == "/" else url

    def is_same_domain(self, url):
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() == self.domain
        except Exception:
            return False

    # --------------------------------------------------------
    # robots.txt
    # --------------------------------------------------------

    def load_robots(self):
        if not self.respect_robots:
            return

        robots_url = f"{self.scheme}://{self.domain}/robots.txt"

        try:
            parser = RobotFileParser()
            parser.set_url(robots_url)
            parser.read()
            self.robot_parser = parser

            print(f"[+] robots.txt kontrol edildi: {robots_url}")

        except Exception:
            print("[!] robots.txt okunamadı, crawler devam ediyor.")

    def allowed_by_robots(self, url):
        if not self.respect_robots:
            return True

        if self.robot_parser is None:
            return True

        try:
            return self.robot_parser.can_fetch(
                HEADERS["User-Agent"],
                url
            )
        except Exception:
            return True

    # --------------------------------------------------------
    # Extraction
    # --------------------------------------------------------

    def extract_links(self, page_url, soup):
        links = set()

        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "").strip()

            if not href:
                continue

            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            absolute = urljoin(page_url, href)
            absolute = urldefrag(absolute)[0]

            try:
                absolute = self.normalize_url(absolute)
            except ValueError:
                continue

            if self.is_same_domain(absolute):
                links.add(absolute)

        return links

    def extract_assets(self, page_url, soup):
        images = set()
        scripts = set()
        stylesheets = set()

        for tag in soup.find_all("img", src=True):
            src = tag.get("src", "").strip()

            if src:
                images.add(urljoin(page_url, src))

        for tag in soup.find_all("script", src=True):
            src = tag.get("src", "").strip()

            if src:
                scripts.add(urljoin(page_url, src))

        for tag in soup.find_all("link", href=True):
            rel = tag.get("rel", [])

            if isinstance(rel, list):
                rel = [x.lower() for x in rel]

            if "stylesheet" in rel:
                stylesheets.add(
                    urljoin(page_url, tag.get("href"))
                )

        return images, scripts, stylesheets

    def extract_forms(self, soup):
        forms = []

        for form in soup.find_all("form"):
            action = form.get("action", "")
            method = form.get("method", "GET").upper()

            inputs = []

            for inp in form.find_all(
                ["input", "textarea", "select", "button"]
            ):
                inputs.append({
                    "tag": inp.name,
                    "type": inp.get("type", ""),
                    "name": inp.get("name", ""),
                })

            forms.append({
                "action": action,
                "method": method,
                "inputs": inputs,
            })

        return forms

    def extract_contacts(self, text):
        emails = set(EMAIL_REGEX.findall(text))
        phones = set(PHONE_REGEX.findall(text))

        return emails, phones

    # --------------------------------------------------------
    # Crawl single page
    # --------------------------------------------------------

    def fetch(self, url, depth):
        if not self.allowed_by_robots(url):
            print(f"[ROBOTS] {url}")
            return None

        try:
            if self.delay:
                time.sleep(self.delay)

            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
            )

            final_url = urldefrag(response.url)[0]

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            status = response.status_code

            result = {
                "url": url,
                "final_url": final_url,
                "depth": depth,
                "status": status,
                "content_type": content_type,
                "title": None,
                "links": [],
                "images": [],
                "scripts": [],
                "stylesheets": [],
                "forms": [],
                "emails": [],
                "phones": [],
            }

            if 300 <= status < 400:
                self.stats["redirects"] += 1

            if 200 <= status < 300:
                self.stats["success"] += 1
            else:
                self.stats["errors"] += 1

            if "text/html" not in content_type:
                self.stats["non_html"] += 1

                print(
                    f"[{status}] {url} "
                    f"(non-HTML)"
                )

                return result

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            if soup.title:
                result["title"] = soup.title.get_text(
                    " ",
                    strip=True
                )

            links = self.extract_links(
                final_url,
                soup
            )

            images, scripts, stylesheets = self.extract_assets(
                final_url,
                soup
            )

            forms = self.extract_forms(soup)

            emails, phones = self.extract_contacts(
                response.text
            )

            result["links"] = sorted(links)
            result["images"] = sorted(images)
            result["scripts"] = sorted(scripts)
            result["stylesheets"] = sorted(stylesheets)
            result["forms"] = forms
            result["emails"] = sorted(emails)
            result["phones"] = sorted(phones)

            with self.lock:
                self.emails.update(emails)
                self.phones.update(phones)
                self.stats["links"] += len(links)

            print(
                f"[{status}] "
                f"D{depth} "
                f"{url}"
            )

            return result

        except requests.RequestException as exc:
            print(f"[ERR] {url} -> {exc}")

            self.stats["errors"] += 1

            return {
                "url": url,
                "final_url": None,
                "depth": depth,
                "status": None,
                "content_type": None,
                "title": None,
                "links": [],
                "images": [],
                "scripts": [],
                "stylesheets": [],
                "forms": [],
                "emails": [],
                "phones": [],
                "error": str(exc),
            }

        except Exception as exc:
            print(f"[ERR] {url} -> {exc}")

            self.stats["errors"] += 1

            return {
                "url": url,
                "depth": depth,
                "error": str(exc),
            }

    # --------------------------------------------------------
    # Main crawler
    # --------------------------------------------------------

    def crawl(self):
        print("\n[+] Crawler başlatılıyor...")
        print(f"[+] Target : {self.start_url}")
        print(f"[+] Domain : {self.domain}")
        print(f"[+] Depth  : {self.max_depth}")
        print(f"[+] Threads: {self.threads}")
        print()

        self.load_robots()

        queue = deque()
        queue.append((self.start_url, 0))

        self.discovered.add(self.start_url)

        while queue:
            current_batch = []

            while queue:
                url, depth = queue.popleft()

                if url in self.visited:
                    continue

                if depth > self.max_depth:
                    continue

                self.visited.add(url)
                self.stats["visited"] += 1
                current_batch.append((url, depth))

            if not current_batch:
                break

            with ThreadPoolExecutor(
                max_workers=self.threads
            ) as executor:

                futures = {
                    executor.submit(
                        self.fetch,
                        url,
                        depth
                    ): (url, depth)
                    for url, depth in current_batch
                }

                for future in as_completed(futures):
                    url, depth = futures[future]

                    try:
                        result = future.result()

                        if result is None:
                            continue

                        self.results.append(result)

                        if depth >= self.max_depth:
                            continue

                        for link in result.get("links", []):
                            if link in self.discovered:
                                continue

                            if not self.is_same_domain(link):
                                continue

                            if not self.allowed_by_robots(link):
                                continue

                            self.discovered.add(link)
                            queue.append(
                                (link, depth + 1)
                            )

                    except Exception as exc:
                        print(
                            f"[ERR] Worker error: {exc}"
                        )

            print(
                f"\n[+] Progress: "
                f"{len(self.visited)} sayfa | "
                f"{len(self.discovered)} URL keşfedildi\n"
            )

        self.results.sort(
            key=lambda item: (
                item.get("depth", 0),
                item.get("url", "")
            )
        )

        return self.results

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    def save_json(self, filename):
        output = {
            "tool": "W-Crawler",
            "version": VERSION,
            "target": self.start_url,
            "domain": self.domain,
            "scan": {
                "max_depth": self.max_depth,
                "threads": self.threads,
                "timeout": self.timeout,
                "delay": self.delay,
                "respect_robots": self.respect_robots,
            },
            "statistics": self.stats,
            "contacts": {
                "emails": sorted(self.emails),
                "phones": sorted(self.phones),
            },
            "results": self.results,
        }

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                output,
                file,
                indent=4,
                ensure_ascii=False
            )

    # --------------------------------------------------------
    # Save TXT
    # --------------------------------------------------------

    def save_txt(self, filename):
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "========================================\n"
            )
            file.write(
                "             W-Crawler v1.0\n"
            )
            file.write(
                "========================================\n\n"
            )

            file.write(
                f"Target : {self.start_url}\n"
            )
            file.write(
                f"Domain : {self.domain}\n\n"
            )

            file.write(
                "--------------- STATISTICS -------------\n"
            )

            for key, value in self.stats.items():
                file.write(
                    f"{key:<15}: {value}\n"
                )

            file.write("\n--------------- EMAILS -----------------\n")

            for email in sorted(self.emails):
                file.write(
                    f"{email}\n"
                )

            file.write("\n--------------- PHONES -----------------\n")

            for phone in sorted(self.phones):
                file.write(
                    f"{phone}\n"
                )

            file.write("\n--------------- PAGES ------------------\n")

            for result in self.results:
                url = result.get("url", "")
                status = result.get("status", "")
                depth = result.get("depth", "")

                file.write(
                    f"[{status}] [D{depth}] {url}\n"
                )

            file.write("\n--------------- LINKS ------------------\n")

            all_links = set()

            for result in self.results:
                all_links.update(
                    result.get("links", [])
                )

            for link in sorted(all_links):
                file.write(
                    f"{link}\n"
                )


def ask_int(prompt, default):
    while True:
        value = input(
            f"{prompt} [{default}]: "
        ).strip()

        if not value:
            return default

        try:
            number = int(value)

            if number < 1:
                raise ValueError

            return number

        except ValueError:
            print("[!] Geçerli bir sayı gir.")


def ask_float(prompt, default):
    while True:
        value = input(
            f"{prompt} [{default}]: "
        ).strip()

        if not value:
            return default

        try:
            number = float(value)

            if number < 0:
                raise ValueError

            return number

        except ValueError:
            print("[!] Geçerli bir sayı gir.")


def main():
    print(BANNER)

    print("=" * 60)
    print("W-Crawler Web Discovery Tool")
    print("=" * 60)

    try:
        target = input(
            "\n[?] Hedef URL: "
        ).strip()

        if not target:
            print("[!] URL boş bırakılamaz.")
            return

        depth = ask_int(
            "[?] Maksimum crawl depth",
            2
        )

        threads = ask_int(
            "[?] Thread sayısı",
            5
        )

        timeout = ask_float(
            "[?] Request timeout",
            10
        )

        delay = ask_float(
            "[?] İstekler arası delay",
            0
        )

        robots_input = input(
            "[?] robots.txt kurallarına uyulsun? [E/h]: "
        ).strip().lower()

        respect_robots = robots_input not in (
            "h",
            "hayır",
            "hayir",
            "n",
            "no",
        )

        crawler = WCrawler(
            start_url=target,
            max_depth=depth,
            threads=threads,
            timeout=timeout,
            delay=delay,
            respect_robots=respect_robots,
        )

        start_time = time.time()

        crawler.crawl()

        elapsed = time.time() - start_time

        print("\n" + "=" * 60)
        print("SCAN TAMAMLANDI")
        print("=" * 60)

        print(
            f"[*] Süre       : {elapsed:.2f} saniye"
        )

        print(
            f"[*] Ziyaret    : {len(crawler.visited)}"
        )

        print(
            f"[*] URL keşfi  : {len(crawler.discovered)}"
        )

        print(
            f"[*] Sonuç      : {len(crawler.results)}"
        )

        print(
            f"[*] E-mail     : {len(crawler.emails)}"
        )

        print(
            f"[*] Telefon    : {len(crawler.phones)}"
        )

        print(
            f"[*] Link       : {crawler.stats['links']}"
        )

        json_name = input(
            "\n[?] JSON dosya adı [w-crawler-results.json]: "
        ).strip()

        if not json_name:
            json_name = "w-crawler-results.json"

        txt_name = input(
            "[?] TXT dosya adı [w-crawler-results.txt]: "
        ).strip()

        if not txt_name:
            txt_name = "w-crawler-results.txt"

        crawler.save_json(json_name)
        crawler.save_txt(txt_name)

        print(
            f"\n[+] JSON kaydedildi: {json_name}"
        )

        print(
            f"[+] TXT kaydedildi : {txt_name}"
        )

    except KeyboardInterrupt:
        print(
            "\n\n[!] Tarama kullanıcı tarafından durduruldu."
        )

    except ValueError as exc:
        print(
            f"\n[!] Hata: {exc}"
        )

    except Exception as exc:
        print(
            f"\n[!] Beklenmeyen hata: {exc}"
        )


if __name__ == "__main__":
    main()
