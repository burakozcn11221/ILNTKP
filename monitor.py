import os, re, sys, json, time, random
import requests
from bs4 import BeautifulSoup

URL = "https://www.gamermarkt.com/tr/ilanlar/valorant-hesap?sort_by=51&servers[]=EU&divisions[]=0"
MIN_LEVEL = 19
MAX_TRY = 170
MAX_EUR = 3.70
SEEN_FILE = "seen.json"
TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT = os.environ.get("TG_CHAT_ID", "")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}


def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": text, "disable_web_page_preview": "true"},
        timeout=20,
    )
    r.raise_for_status()


def parse_num(s):
    s = s.strip(".,")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") == 1 and len(s.split(".")[1]) == 3:
        s = s.replace(".", "")
    return float(s)


def main():
    if "test" in sys.argv:
        send("Test mesaji: bot calisiyor.")
        print("test sent")
        return

    time.sleep(random.uniform(0, 120))
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    print("HTTP", resp.status_code)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    seen = set()
    if os.path.exists(SEEN_FILE):
        seen = set(json.load(open(SEEN_FILE)))

    cards = soup.select('a[href*="/tr/ilan/"]')
    print("ilan sayisi:", len(cards))
    new_hits = 0
    for a in cards:
        href = a.get("href", "").split("?")[0]
        if href in seen:
            continue
        text = a.get_text(" ", strip=True)
        pm = re.search(r"([€₺$])\s*([\d.,]+)", text)
        lm = re.search(r"(?:EU|NA)\s*(\d+)\s*\.?\s*Level", text)
        if not pm or not lm:
            continue
        sym, amount = pm.group(1), parse_num(pm.group(2))
        level = int(lm.group(1))
        if sym == "₺":
            ok = amount < MAX_TRY
        elif sym == "€":
            ok = amount < MAX_EUR
        else:
            continue
        if level >= MIN_LEVEL and ok:
            send(f"Yeni ilan!\nLevel: {level}\nFiyat: {sym}{amount:.2f}\n{href}")
            seen.add(href)
            new_hits += 1
    print("bildirim:", new_hits)
    json.dump(sorted(seen), open(SEEN_FILE, "w"))


if __name__ == "__main__":
    main()
