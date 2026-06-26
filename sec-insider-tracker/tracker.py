#!/usr/bin/env python3
"""
SEC EDGAR Insider Buy Tracker
Daily monitor: scans all Form 4 filings, emails significant insider purchases.
Target: mingshian.tsai@gmail.com
"""

import os, sys, json, ssl, smtplib, time, logging, threading
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import xml.etree.ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────
TO_EMAIL   = "mingshian.tsai@gmail.com"
FROM_EMAIL = os.environ.get("GMAIL_USER", "mingshian.tsai@gmail.com")
APP_PASS   = os.environ.get("GMAIL_APP_PASSWORD", "")
MIN_VALUE  = 100_000   # $100K threshold
MAX_PAGES  = 25        # 25 × 100 = up to 2,500 filings per scan
WORKERS    = 15        # parallel XML download threads

EFTS_URL  = "https://efts.sec.gov/LATEST/search-index"
ARCHIVES  = "https://www.sec.gov/Archives/edgar/data"
UA        = f"InsiderBuyTracker {TO_EMAIL}"

# ─── Thread-local sessions ────────────────────────────────────────────────────
_tls = threading.local()

def session() -> requests.Session:
    if not hasattr(_tls, "s"):
        s = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        s.mount("https://", HTTPAdapter(max_retries=retry))
        s.headers["User-Agent"] = UA
        _tls.s = s
    return _tls.s


# ─── EDGAR EFTS search ────────────────────────────────────────────────────────
def search_form4(start: str, end: str) -> list[str]:
    """Return accession numbers for all Form 4 filings in date range."""
    result, page = [], 0
    while page < MAX_PAGES:
        url = (f"{EFTS_URL}?forms=4&dateRange=custom"
               f"&startdt={start}&enddt={end}&from={page*100}&size=100")
        try:
            r = session().get(url, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            log.warning(f"EFTS page {page} error: {e}")
            break
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break
        for h in hits:
            acc = h.get("_source", {}).get("accession_no") or h.get("_id", "")
            if acc and "-" in acc:
                result.append(acc)
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        log.info(f"  Page {page+1}: {len(hits)} hits (total={total})")
        page += 1
        if page * 100 >= total:
            break
        time.sleep(0.2)
    return result


# ─── Filing XML download ──────────────────────────────────────────────────────
def cik_from_acc(acc: str) -> str:
    """Strip leading zeros from the CIK embedded in the accession number."""
    return str(int(acc.split("-")[0]))

def fetch_xml(acc: str) -> Optional[str]:
    cik       = cik_from_acc(acc)
    acc_clean = acc.replace("-", "")
    sess      = session()

    # Discover filename from filing index JSON
    xml_name = None
    try:
        idx_url = f"{ARCHIVES}/{cik}/{acc_clean}/{acc}-index.json"
        r = sess.get(idx_url, timeout=15)
        if r.ok:
            idx = r.json()
            xml_name = idx.get("primaryDocument", "")
            if not (xml_name and xml_name.endswith(".xml")):
                for doc in idx.get("documents", []):
                    fname = doc.get("document", doc.get("name", ""))
                    if doc.get("type") == "4" and fname.endswith(".xml"):
                        xml_name = fname
                        break
            if not (xml_name and xml_name.endswith(".xml")):
                for doc in idx.get("documents", []):
                    fname = doc.get("document", doc.get("name", ""))
                    if fname.endswith(".xml") and "full-submission" not in fname:
                        xml_name = fname
                        break
    except Exception:
        pass

    for candidate in filter(None, [xml_name, f"{acc}.xml"]):
        try:
            r = sess.get(f"{ARCHIVES}/{cik}/{acc_clean}/{candidate}", timeout=15)
            if r.ok and r.text.strip().startswith("<"):
                return r.text
        except Exception:
            pass
    return None


# ─── XML parse ────────────────────────────────────────────────────────────────
def _txt(el: ET.Element, *paths: str) -> str:
    for p in paths:
        for suf in (f"{p}/value", p):
            n = el.find(suf)
            if n is not None and n.text:
                return n.text.strip()
    return ""

def parse_form4(xml: str, acc: str) -> Optional[dict]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return None

    issuer = root.find("issuer")
    if issuer is None:
        return None

    company    = _txt(issuer, "issuerName")
    ticker     = _txt(issuer, "issuerTradingSymbol")
    issuer_cik = _txt(issuer, "issuerCik")

    ow = root.find("reportingOwner")
    if ow is None:
        return None
    owner  = _txt(ow, "reportingOwnerId/rptOwnerName")
    rel    = ow.find("reportingOwnerRelationship")
    is_dir = rel is not None and _txt(rel, "isDirector") == "1"
    is_off = rel is not None and _txt(rel, "isOfficer")  == "1"
    title  = _txt(rel, "officerTitle") if rel is not None else ""

    if not (is_dir or is_off):
        return None   # skip 10% holders and other filer types

    buys = []
    tbl  = root.find("nonDerivativeTable")
    if tbl is not None:
        for txn in tbl.findall("nonDerivativeTransaction"):
            cod = txn.find("transactionCoding")
            if not cod or _txt(cod, "transactionCode") != "P":
                continue   # P = open-market purchase only
            amt = txn.find("transactionAmounts")
            if not amt or _txt(amt, "transactionAcquiredDisposedCode") != "A":
                continue
            try:
                shares = float(_txt(amt, "transactionShares")       or "0")
                price  = float(_txt(amt, "transactionPricePerShare") or "0")
            except ValueError:
                continue
            if shares <= 0 or price <= 0:
                continue
            post = txn.find("postTransactionAmounts")
            buys.append({
                "security":    _txt(txn, "securityTitle") or "Common Stock",
                "date":        _txt(txn, "transactionDate"),
                "shares":      shares,
                "price":       price,
                "value":       shares * price,
                "owned_after": float(_txt(post, "sharesOwnedFollowingTransaction") or "0")
                               if post else 0,
            })

    if not buys:
        return None

    total = sum(b["value"] for b in buys)
    return {
        "company":    company,
        "ticker":     ticker,
        "issuer_cik": issuer_cik,
        "owner":      owner,
        "role":       title or ("Director" if is_dir else "Officer"),
        "buys":       buys,
        "total":      total,
        "acc":        acc,
        "sec_url":    (f"https://www.sec.gov/cgi-bin/browse-edgar"
                       f"?action=getcompany&CIK={issuer_cik}&type=4"
                       f"&dateb=&owner=include&count=5"),
    }

def process(acc: str) -> Optional[dict]:
    try:
        xml = fetch_xml(acc)
        if not xml:
            return None
        r = parse_form4(xml, acc)
        return r if (r and r["total"] >= MIN_VALUE) else None
    except Exception as e:
        log.debug(f"{acc}: {e}")
        return None


# ─── Email ────────────────────────────────────────────────────────────────────
def _fmt(v: float) -> str:
    return f"${v/1e6:.1f}M" if v >= 1e6 else f"${v/1e3:.0f}K"

def build_html(results: list[dict], label: str, n_scanned: int) -> str:
    if results:
        rows = ""
        for i, r in enumerate(results, 1):
            bg  = "#f8f9fa" if i % 2 else "#ffffff"
            t   = f"<b>{r['ticker']}</b>" if r["ticker"] else "OTC"
            b   = r["buys"][0]
            lnk = f'<a href="{r["sec_url"]}" style="color:#0366d6">EDGAR↗</a>'
            rows += (
                f'<tr style="background:{bg}">'
                f'<td style="padding:9px 13px;color:#aaa;font-size:.82em">{i}</td>'
                f'<td style="padding:9px 13px"><b>{r["company"]}</b><br>'
                f'<span style="color:#666;font-size:.83em">{t}</span></td>'
                f'<td style="padding:9px 13px">{r["owner"]}<br>'
                f'<span style="color:#666;font-size:.83em">{r["role"]}</span></td>'
                f'<td style="padding:9px 13px;text-align:right;color:#1a7a1a;'
                f'font-weight:700;font-size:1.05em">{_fmt(r["total"])}</td>'
                f'<td style="padding:9px 13px;text-align:right;color:#555;font-size:.88em">'
                f'{b["shares"]:,.0f} 股<br>@ ${b["price"]:,.2f}</td>'
                f'<td style="padding:9px 13px;text-align:center">{lnk}</td></tr>'
            )
    else:
        rows = ('<tr><td colspan="6" style="padding:28px;text-align:center;color:#aaa">'
                '今日未发现 $100K+ 公开市场内幕买入记录</td></tr>')

    return f"""<!DOCTYPE html><html lang="zh-Hant">
<head><meta charset="utf-8"><style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;background:#edf0f5;margin:0}}
.w{{max-width:920px;margin:24px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 14px rgba(0,0,0,.12)}}
.hd{{background:linear-gradient(135deg,#0d1b2a 0%,#1b2d45 100%);padding:26px 30px;color:#fff}}
h1{{margin:0;font-size:1.35em;letter-spacing:-.2px}}
.sub{{color:#7aaddc;font-size:.86em;margin-top:6px}}
.note{{padding:13px 30px;background:#f0f5ff;border-bottom:1px solid #dce4f5;color:#445;font-size:.88em;line-height:1.65}}
table{{width:100%;border-collapse:collapse}}
thead tr{{background:#0d1b2a;color:#fff}}
th{{padding:10px 13px;font-size:.82em;font-weight:600;text-align:left}}
.ft{{padding:13px 30px;background:#f7f8fa;color:#aaa;font-size:.76em;line-height:1.9}}
</style></head>
<body><div class="w">
<div class="hd">
  <h1>📈 SEC 内幕增持日报</h1>
  <div class="sub">{label} &nbsp;·&nbsp; 共扫描 {n_scanned} 份 Form 4 &nbsp;·&nbsp; 筛选公开市场买入 &gt; $100,000</div>
</div>
<div class="note">
以下为过去 24 小时内，公司<strong>高管（Officer）</strong>及<strong>董事（Director）</strong>
通过 SEC Form 4 申报的<strong>公开市场买入</strong>记录（交易代码 P），按买入金额由高到低排列。<br>
内部人主动掏钱买自家股票，通常只有一个原因：他们相信这笔钱会增值。
</div>
<table>
<thead><tr>
  <th>#</th><th>公司 / 代码</th><th>内部人 / 职位</th>
  <th style="text-align:right">买入金额</th>
  <th style="text-align:right">股数 / 单价</th>
  <th style="text-align:center">来源</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
<div class="ft">
数据来源：SEC EDGAR Form 4 &nbsp;|&nbsp; 仅限交易代码「P」= 公开市场买入，不含期权行权、定向增发、赠股等 <br>
本报告由 GitHub Actions 自动生成 &nbsp;·&nbsp; 仅供参考，不构成任何投资建议
</div>
</div></body></html>"""

def send_email(subject: str, html: str):
    if not APP_PASS:
        log.error("GMAIL_APP_PASSWORD env var not set — cannot send email")
        sys.exit(1)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = FROM_EMAIL
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as smtp:
        smtp.login(FROM_EMAIL, APP_PASS)
        smtp.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
    log.info(f"✓ Email sent to {TO_EMAIL}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    today  = date.today()
    end    = (today - timedelta(days=1)).isoformat()
    start  = (today - timedelta(days=2)).isoformat()
    label  = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    log.info(f"=== SEC Insider Buy Tracker | scanning {start} → {end} ===")

    accs = search_form4(start, end)
    log.info(f"Total filings to process: {len(accs)}")

    qualifying, done = [], 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(process, a): a for a in accs}
        for f in as_completed(futs):
            done += 1
            if done % 250 == 0:
                log.info(f"  {done}/{len(accs)} processed | {len(qualifying)} qualifying")
            r = f.result()
            if r:
                qualifying.append(r)

    qualifying.sort(key=lambda x: x["total"], reverse=True)
    log.info(f"✓ Found {len(qualifying)} insider buy(s) ≥ $100K out of {len(accs)} filings")

    subject = f"📈 SEC内幕增持日报 {label} — {len(qualifying)} 笔大额买入"
    html    = build_html(qualifying, label, len(accs))
    send_email(subject, html)
    log.info("Done!")

if __name__ == "__main__":
    main()
