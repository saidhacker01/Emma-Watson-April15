import re
import requests
import base64
import socket
import hashlib
from bs4 import BeautifulSoup
from colorama import Fore, init

init(autoreset=True)

# ======================
# CONFIG
# ======================
FLAG_REGEX = r"(flag\{.*?\}|ctf\{.*?\}|CTF\{.*?\}|picoCTF\{.*?\})"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ======================
# CORE FUNCTION
# ======================
def find_flag(text):
    return list(set(re.findall(FLAG_REGEX, text)))

# ======================
# WEB SCAN
# ======================
def web_scan():
    url = input("URL: ")
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        print(Fore.GREEN + "[+] Loaded")

        flags = find_flag(r.text)

        soup = BeautifulSoup(r.text, "html.parser")

        # comments + scripts
        for tag in soup.find_all(["script", "style"]):
            flags += find_flag(tag.text)

        for comment in soup.find_all(string=True):
            flags += find_flag(comment)

        flags = list(set(flags))

        if flags:
            print(Fore.YELLOW + "[!] FLAGS FOUND:")
            for f in flags:
                print(f)
        else:
            print(Fore.RED + "[-] No flag")

    except Exception as e:
        print("Error:", e)

# ======================
# BASE64 / HEX
# ======================
def base64_decode():
    data = input("Base64: ")
    try:
        decoded = base64.b64decode(data).decode()
        print("[+] Decoded:", decoded)
        print("[!] Flags:", find_flag(decoded))
    except:
        print("Invalid Base64")

def hex_decode():
    data = input("HEX: ")
    try:
        decoded = bytes.fromhex(data).decode()
        print("[+] Decoded:", decoded)
        print("[!] Flags:", find_flag(decoded))
    except:
        print("Invalid HEX")

# ======================
# FILE SCAN
# ======================
def file_scan():
    path = input("File path: ")
    try:
        with open(path, "rb") as f:
            data = f.read().decode(errors="ignore")

        flags = find_flag(data)

        if flags:
            print(Fore.YELLOW + "[!] Found:")
            for f in flags:
                print(f)
        else:
            print("No flag")
    except:
        print("Error reading file")

# ======================
# HASH CRACK (WORDLIST)
# ======================
def hash_crack():
    hash_value = input("Hash (MD5/SHA1): ")
    wordlist = input("Wordlist file path: ")

    try:
        with open(wordlist, "r") as f:
            for word in f:
                word = word.strip()

                if hashlib.md5(word.encode()).hexdigest() == hash_value:
                    print(Fore.GREEN + "[FOUND MD5]:", word)
                    return

                if hashlib.sha1(word.encode()).hexdigest() == hash_value:
                    print(Fore.GREEN + "[FOUND SHA1]:", word)
                    return

        print("Not found")

    except:
        print("Error")

# ======================
# SUBDOMAIN FINDER
# ======================
def subdomain_finder():
    domain = input("Domain: ")
    subs = ["www", "admin", "dev", "test", "api", "mail"]

    print("[+] Scanning...")

    for sub in subs:
        full = sub + "." + domain
        try:
            ip = socket.gethostbyname(full)
            print(Fore.GREEN + f"[FOUND] {full} -> {ip}")
        except:
            pass

# ======================
# DIRECTORY SCAN
# ======================
def dir_scan():
    url = input("URL: ")
    paths = ["admin", "login", "dashboard", "uploads", "config"]

    print("[+] Scanning dirs...")

    for p in paths:
        full = url.rstrip("/") + "/" + p
        try:
            r = requests.get(full, timeout=3)
            if r.status_code == 200:
                print(Fore.GREEN + "[FOUND]", full)
        except:
            pass

# ======================
# SIMPLE SQLi CHECK (SAFE)
# ======================
def sqli_test():
    url = input("URL with id param (example: site.com/item?id=1): ")

    payload = "' OR '1'='1"
    test_url = url + payload

    try:
        r = requests.get(test_url)

        if "error" in r.text.lower() or "sql" in r.text.lower():
            print(Fore.YELLOW + "[!] Possible SQL Injection")
        else:
            print("[-] Not vulnerable")
    except:
        print("Error")

# ======================
# XSS TEST
# ======================
def xss_test():
    url = input("URL (?q=): ")
    payload = "<script>alert(1)</script>"

    try:
        r = requests.get(url + payload)
        if payload in r.text:
            print(Fore.YELLOW + "[!] Possible XSS")
        else:
            print("[-] Not vulnerable")
    except:
        print("Error")

# ======================
# TEXT SCAN
# ======================
def text_scan():
    text = input("Text: ")
    print(find_flag(text))

# ======================
# MENU
# ======================
def menu():
    print(Fore.CYAN + """
======= ULTIMATE CTF TOOL =======

1. Web Flag Scanner
2. Base64 Decode
3. HEX Decode
4. File Scanner
5. Hash Cracker (MD5/SHA1)
6. Subdomain Finder
7. Directory Scanner
8. SQLi Test (Safe)
9. XSS Test (Safe)
10. Text Flag Finder

================================
""")

    choice = input("Select: ")

    if choice == "1":
        web_scan()
    elif choice == "2":
        base64_decode()
    elif choice == "3":
        hex_decode()
    elif choice == "4":
        file_scan()
    elif choice == "5":
        hash_crack()
    elif choice == "6":
        subdomain_finder()
    elif choice == "7":
        dir_scan()
    elif choice == "8":
        sqli_test()
    elif choice == "9":
        xss_test()
    elif choice == "10":
        text_scan()
    else:
        print("Invalid")

menu()
