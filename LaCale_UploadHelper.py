import subprocess, json, os
from tkinter import Tk, filedialog

# =====================
# MediaInfo
# =====================
def run_mediainfo(file):
    r = subprocess.run(["mediainfo", "--Output=JSON", file], stdout=subprocess.PIPE, text=True)
    return json.loads(r.stdout)["media"]["track"]

def choose_file():
    Tk().withdraw()
    return filedialog.askopenfilename(filetypes=[("Videos","*.mkv *.mp4 *.avi *.mov *.iso")])

def safe(v):
    try:
        return int(str(v).replace(" ","").replace("px",""))
    except:
        return 0

# =====================
# Qualité
# =====================
def detect_quality(w,h):
    if w >= 7600: return "4320p (8K)"
    if w >= 3800: return "2160p (4K)"
    if w >= 1900: return "1080p (Full HD)"
    if w >= 1200: return "720p (HD)"
    return "SD"

# =====================
# Codec Vidéo
# =====================
def detect_video_codec(video):
    f = video.get("Format","").lower()
    if "av1" in f: return "AV1"
    if "hevc" in f or "265" in f: return "HEVC/H265/x265"
    if "avc" in f or "264" in f: return "AVC/H264/x264"
    if "mpeg" in f: return "MPEG"
    if "vc-1" in f: return "VC-1"
    if "vp9" in f: return "VP9"
    return "Autres"

# =====================
# Video flags
# =====================
def detect_video_flags(video):
    flags = []
    if video.get("BitDepth") == "10":
        flags.append("10 bits")

    hdr = (video.get("HDR_Format","") + video.get("Transfer_characteristics","")).lower()
    if "dolby vision" in hdr:
        flags.append("Dolby Vision")
    if "hdr10+" in hdr:
        flags.append("HDR10+")
    if "pq" in hdr or "hdr10" in hdr:
        flags.append("HDR")
    if "hlg" in hdr:
        flags.append("HLG")

    if not any(x in flags for x in ["HDR","Dolby Vision","HDR10+","HLG"]):
        flags.append("SDR")

    return flags

# =====================
# Source
# =====================
def detect_source(video, filename, bitrate):
    name = filename.lower()
    sources = []

    # --- Disque ---
    if "bluray" in name or "bdrip" in name:
        sources.append("BluRay")
    if "remux" in name:
        sources.append("REMUX")
    if "dvd" in name:
        sources.append("DVDRip")

    # --- WEB ---
    if "web-dl" in name:
        sources.append("WEB-DL")
    if "webrip" in name or "web" in name:
        sources.append("WEBRip")

    # --- Light detection ---
    duration = safe(video.get("Duration")) / 1000
    if duration > 0:
        mbph = (bitrate / 8 / 1024) * 3600

        if safe(video.get("Width")) >= 3800 and mbph < 6000:
            sources.append("4KLight")
        if safe(video.get("Width")) >= 1900 and mbph < 3500:
            sources.append("HDLight")

    # Nom du fichier a prioriser
    if "4klight" in name and "4KLight" not in sources:
        sources.append("4KLight")
    if "hdlight" in name and "HDLight" not in sources:
        sources.append("HDLight")

    return list(dict.fromkeys(sources))  # remove duplicates, keep order

# =====================
# Audio codec
# =====================
def detect_audio_codec(audios):
    found = set()
    atmos = False

    for a in audios:
        f = a.get("Format","").upper()
        c = a.get("Commercial_name","").lower()

        if "TRUEHD" in f: found.add("TrueHD")
        elif "E-AC-3" in f: found.add("E-AC3")
        elif "AC-3" in f: found.add("AC3")
        elif "DTS-HD MA" in f: found.add("DTS-HD MA")
        elif "DTS-HD" in f: found.add("DTS-HD HR")
        elif "DTS" in f: found.add("DTS")
        elif "AAC" in f: found.add("AAC")
        elif "FLAC" in f: found.add("FLAC")
        elif "MP3" in f: found.add("MP3")

        if "atmos" in c:
            atmos = True

    if atmos:
        return ["TrueHD Atmos"] if "TrueHD" in found else ["E-AC3 Atmos"]

    return list(found)

# =====================
# Langues audio
# =====================
def detect_languages(audios):
    langs = set()
    for a in audios:
        l = a.get("Language","").lower()
        if l in ["fr","fra","fre"]: langs.add("French")
        elif l in ["en","eng"]: langs.add("English")
        elif l in ["es","spa"]: langs.add("Spanish")
        elif l in ["it","ita"]: langs.add("Italian")
        elif l in ["ja","jpn"]: langs.add("Japanese")
        elif l in ["ko","kor"]: langs.add("Korean")
        elif l in ["zh","chi","zho"]: langs.add("Chinois")

    if len(langs) > 1:
        langs.add("MULTI")

    return list(langs)

# =====================
# Subs
# =====================
def detect_subs(subs):
    out = set()
    for s in subs:
        l = s.get("Language","").lower()
        if l in ["fr","fra","fre"]: out.add("FR")
        elif l in ["en","eng"]: out.add("ENG")
        else: out.add("Autres sous-titres")
    return list(out)

def normalize_sub_lang(code):
    code = code.lower()
    if code in ["fr","fra","fre"]: return "FR"
    if code in ["en","eng"]: return "ENG"
    if code in ["es","spa"]: return "ESP"
    if code in ["it","ita"]: return "ITA"
    return "Other"

def detect_sub_type(track):
    title = track.get("Title","").lower()
    forced = track.get("Forced","").lower()

    if forced == "yes" or "forced" in title or "forcé" in title:
        return "Forced"
    if "sdh" in title:
        return "SDH"
    if "full" in title or "complet" in title:
        return "Full"
    if "sign" in title or "song" in title:
        return "Signs & Songs"
    return ""

def detect_sub_tracks(subs):
    out = []

    for s in subs:
        lang = normalize_sub_lang(s.get("Language",""))
        typ = detect_sub_type(s)

        label = lang
        if typ:
            label += f" ({typ})"

        out.append(label)

    return out

# =====================
# Langue + Codec par piste
# =====================
def normalize_lang(code):
    code = code.lower()
    if code in ["fr","fra","fre"]: return "French"
    if code in ["en","eng"]: return "English"
    if code in ["es","spa"]: return "Spanish"
    if code in ["it","ita"]: return "Italian"
    if code in ["ja","jpn"]: return "Japanese"
    return "Other"

def detect_variant(title):
    t = title.lower()
    if "truefrench" in t or "vff" in t:
        return "VFF"
    if "vfq" in t:
        return "VFQ"
    if "vfi" in t:
        return "VFI"
    if "vo" in t:
        return "VO"
    return ""

def audio_codec_name(track):
    f = track.get("Format","").upper()
    if "TRUEHD" in f: return "TrueHD"
    if "E-AC-3" in f: return "E-AC3"
    if "AC-3" in f: return "AC3"
    if "DTS-HD MA" in f: return "DTS-HD MA"
    if "DTS-HD" in f: return "DTS-HD HR"
    if "DTS" in f: return "DTS"
    if "AAC" in f: return "AAC"
    if "FLAC" in f: return "FLAC"
    return "Other"

def detect_audio_tracks(audios):
    tracks = []

    for a in audios:
        lang = normalize_lang(a.get("Language",""))
        codec = audio_codec_name(a)
        title = a.get("Title","")
        variant = detect_variant(title)

        label = f"{lang} ({codec})"
        if variant:
            label += f" [{variant}]"

        tracks.append(label)

    return tracks

# =====================
# MAIN
# =====================
def main():
    f = choose_file()
    if not f: return

    tracks = run_mediainfo(f)
    video = next(t for t in tracks if t["@type"]=="Video")
    audios = [t for t in tracks if t["@type"]=="Audio"]
    subs = [t for t in tracks if t["@type"]=="Text"]

    w,h = safe(video.get("Width")), safe(video.get("Height"))
    bitrate = safe(video.get("BitRate"))

    print("\n=== FICHE UPLOAD LA-CALE ===\n")
    print("Qualité :", detect_quality(w,h))
    print("Codec Vidéo :", detect_video_codec(video))
    print("Caractéristiques :", ", ".join(detect_video_flags(video)))
    print("Source :", detect_source(video, os.path.basename(f), bitrate))
    print("Pistes Audio :")
    for a in detect_audio_tracks(audios):
        print("  -", a)
    print("Sous-titres :")
    for s in detect_sub_tracks(subs):
        print("  -", s)
    print("Extension :", os.path.splitext(f)[1].replace(".","").upper())
    print("Taille :", f"{os.path.getsize(f)/1024**3:.2f} GB")

if __name__ == "__main__":
    main()
