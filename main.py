#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║  🤖 YANDEX MUSIC DOWNLOADER v2.0 "MARK XLII"                  ║
║  Designed by Pavel • Powered by J.A.R.V.I.S. core             ║
║  "Sometimes you gotta run before you can walk." — T. Stark   ║
╚═══════════════════════════════════════════════════════════════╝
"""
import asyncio
import webbrowser
import sys
from pathlib import Path
from yandex_music import ClientAsync

# ─────────────────────────────────────────────────────────────
# 🎨 TONY STARK UI UTILS
# ─────────────────────────────────────────────────────────────
class StarkUI:
    """Интерфейс в стиле голографического дисплея Тони Старка"""
    
    COLORS = {
        'cyan': '\033[96m', 'blue': '\033[94m', 'green': '\033[92m',
        'yellow': '\033[93m', 'red': '\033[91m', 'bold': '\033[1m',
        'reset': '\033[0m'
    }
    
    @staticmethod
    def banner():
        return f"""
{StarkUI.COLORS['cyan']}
╔═══════════════════════════════════════════════════════════════╗
║  🤖  YANDEX MUSIC DOWNLOADER v2.0 "MARK XLII"                 ║
║  ⚡  Just another Tuesday in the workshop                     ║
║  🛠️  Powered by J.A.R.V.I.S. core • {StarkUI.COLORS['yellow']}Pavel Edition{StarkUI.COLORS['reset']}
╚═══════════════════════════════════════════════════════════════╝
{StarkUI.COLORS['reset']}"""
    
    @staticmethod
    def status(msg, color='cyan'):
        print(f"{StarkUI.COLORS.get(color, '')}[✦] {msg}{StarkUI.COLORS['reset']}", flush=True)
    
    @staticmethod
    def success(msg):
        print(f"{StarkUI.COLORS['green']}[✓] {msg}{StarkUI.COLORS['reset']}", flush=True)
    
    @staticmethod
    def warning(msg):
        print(f"{StarkUI.COLORS['yellow']}[⚠] {msg}{StarkUI.COLORS['reset']}", flush=True)
    
    @staticmethod
    def error(msg):
        print(f"{StarkUI.COLORS['red']}[✗] {msg}{StarkUI.COLORS['reset']}", flush=True)
    
    @staticmethod
    def progress(current, total, status="Processing"):
        percent = (current / total) * 100
        bar = "█" * int(percent // 5) + "░" * (20 - int(percent // 5))
        print(f"\r{StarkUI.COLORS['blue']}[{bar}] {percent:.1f}% {status}{StarkUI.COLORS['reset']}", end="", flush=True)

# ─────────────────────────────────────────────────────────────
# 🔗 КОНСТАНТЫ
# ─────────────────────────────────────────────────────────────
TOKEN_HELP_URL = "https://chromewebstore.google.com/detail/yandex-music-token/lcbjeookjibfhjjopieifgjnhlegmkib?hl=ru&utm_source=ext_sidebar"

# ─────────────────────────────────────────────────────────────
# 🎵 CORE LOGIC
# ─────────────────────────────────────────────────────────────
async def download_track(client: ClientAsync, short_track, folder: Path):
    """Загрузка трека. Быстро. Эффектно. Без компромиссов."""
    try:
        full_track = await short_track.fetch_track_async()
        artist = full_track.artists[0].name if full_track.artists else "Unknown Artist"
        title = full_track.title
        
        # 🛡️ Фильтр "кривых" символов — Тони не любит баги в путях
        safe = lambda s: "".join(c for c in s if c not in r'<>:"/\|?*').strip()
        filename = folder / f"{safe(artist)} - {safe(title)}.mp3"
        
        await full_track.download_async(filename=str(filename))
        return True, f"{artist} - {title}"
    except Exception as e:
        return False, str(e)

async def main(TOKEN, DOWNLOAD_DIR):
    StarkUI.status("Инициализация протоколов связи...", "blue")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    client = await ClientAsync(TOKEN).init()
    StarkUI.success("Авторизация пройдена. Добро пожаловать, сэр.")
    
    status = await client.account_status()
    StarkUI.status(f"Пользователь: {status.account.login}", "cyan")
    plus_status = "активен" if status.plus.has_plus else "не активен (качество будет стандартным)"
    StarkUI.status(f"Яндекс.Плюс: {plus_status}", "green" if status.plus.has_plus else "yellow")
    
    # 🎛️ Настройки (можно вынести в конфиг позже)
    USE_LIKES_PLAYLIST = True
    USER_ID, PLAYLIST_KIND = "12345678", "567890"
    
    StarkUI.status("Загрузка метаданных плейлиста...", "blue")
    if USE_LIKES_PLAYLIST:
        tracks_list = await client.users_likes_tracks()
        StarkUI.success("Плейлист 'Мне нравится' получен")
    else:
        playlist = await client.users_playlists(kind=PLAYLIST_KIND, user_id=USER_ID)
        if not playlist:
            StarkUI.error("Плейлист не найден. Проверьте координаты, сэр.")
            return
        tracks_list = playlist[0]
    
    tracks = tracks_list.tracks if hasattr(tracks_list, 'tracks') else []
    StarkUI.status(f"Обнаружено треков: {len(tracks)}. Начинаем загрузку...", "cyan")
    print()
    
    success, failed = 0, 0
    for i, short_track in enumerate(tracks, 1):
        StarkUI.progress(i, len(tracks), f"Track {i}/{len(tracks)}")
        ok, result = await download_track(client, short_track, DOWNLOAD_DIR)
        if ok:
            success += 1
        else:
            failed += 1
            StarkUI.warning(f"Пропуск: {result[:50]}...")
        await asyncio.sleep(0.25)  # Не будим спящих драконов Яндекса
    
    print()
    StarkUI.success(f"Миссия выполнена! ✅ Успешно: {success} | Пропущено: {failed}")
    StarkUI.status(f"Файлы сохранены в: {DOWNLOAD_DIR}", "green")
    await client.close()

# ─────────────────────────────────────────────────────────────
# 🚀 ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(StarkUI.banner())
    
    # 🌐 Открываем браузер для получения токена — Тони ценит ваше время
    StarkUI.status("Открываю панель получения токена в браузере...", "cyan")
    webbrowser.open(TOKEN_HELP_URL)
    print(f"{StarkUI.COLORS['yellow']}💡 Совет: скопируйте токен и вернитесь сюда. Я подожду.{StarkUI.COLORS['reset']}\n")
    
    # 🔐 Ввод токена
    TOKEN = input(f"{StarkUI.COLORS['bold']}🔐 Введите токен доступа:{StarkUI.COLORS['reset']} ").strip()
    if not TOKEN or len(TOKEN) < 20:
        StarkUI.error("Токен выглядит подозрительно. Проверьте, сэр.")
        input(f"\n{StarkUI.COLORS['yellow']}Нажмите Enter для выхода...{StarkUI.COLORS['reset']}")
        sys.exit(1)
    
    # 📁 Ввод пути
    folder_input = input(f"{StarkUI.COLORS['bold']}📁 Путь для сохранения (Enter для C:\\mus):{StarkUI.COLORS['reset']} ").strip()
    DOWNLOAD_DIR = Path(folder_input if folder_input else r"C:\mus")
    
    # 🚀 Запуск
    try:
        asyncio.run(main(TOKEN, DOWNLOAD_DIR))
    except KeyboardInterrupt:
        print(f"\n{StarkUI.COLORS['yellow']}⏹️ Прервано по команде пользователя. Как скажете.{StarkUI.COLORS['reset']}")
    except Exception as e:
        StarkUI.error(f"Критический сбой: {e}")
        StarkUI.warning("Рекомендация: проверьте соединение и попробуйте снова, сэр.")
    finally:
        print(f"\n{StarkUI.COLORS['green']}🎯 Система готова к следующей операции.{StarkUI.COLORS['reset']}")
        input(f"{StarkUI.COLORS['bold']}Нажмите Enter для завершения...{StarkUI.COLORS['reset']}")
