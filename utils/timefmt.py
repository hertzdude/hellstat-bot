def fmt_duration(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    parts = []
    if h: parts.append(f"{h} ч")
    if m: parts.append(f"{m} мин")
    if s or not parts: parts.append(f"{s} с")
    return " ".join(parts)
