"""
Koda Hotkey Service — keyboard hooks in a separate process.

Windows silently kills WH_KEYBOARD_LL hooks when the hook thread can't
respond within the OS timeout (~300ms).  Whisper transcription holds
Python's GIL for seconds, starving the hook thread in the main process.

This service runs in its own process with its own GIL, so hooks always
respond promptly regardless of what the main process is doing.

Protocol (over multiprocessing.Pipe):
    Child → Parent events:
        "ready"                 — hooks registered, service is live
        ("pong", float)         — reply to "ping"; float is monotonic time of last key event
        "pong"                  — legacy plain pong (only sent if _hooks_alive() check fails path)
        "dictation_press"       — hold mode: hotkey pressed
        "dictation_release"     — hold mode: trigger key released
        "command_press"         — hold mode: hotkey pressed
        "command_release"       — hold mode: trigger key released
        "dictation_toggle"      — toggle mode: hotkey pressed
        "command_toggle"        — toggle mode: hotkey pressed
        "correction"            — correction hotkey pressed
        "readback"              — read-back hotkey pressed
        "readback_selected"     — read-selected hotkey pressed

    Parent → Child commands:
        "ping"                  — health check (expects "pong" back)
        "quit"                  — graceful shutdown
"""

import keyboard
import os
import sys
import logging
import threading
import time

logger = logging.getLogger("koda.hotkey")

# Tracks the monotonic time of the last key event actually delivered by Windows.
# Updated by a catch-all keyboard.on_press hook. If this stops updating while
# the listener thread stays alive, the Windows WH_KEYBOARD_LL hook is dead.
_last_any_key_time = time.monotonic()
_last_any_key_lock = threading.Lock()


def _touch_last_key(_event=None):
    global _last_any_key_time
    with _last_any_key_lock:
        _last_any_key_time = time.monotonic()


def service_main(conn, hotkey_config):
    """Entry point for the hotkey service process.

    Args:
        conn: multiprocessing.Connection — bidirectional pipe to parent.
        hotkey_config: dict with hotkey settings from Koda config.
    """
    # Set up logging to the same debug.log as the main process
    log_path = hotkey_config.get("_log_path", "debug.log")
    logging.basicConfig(
        filename=log_path,
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger.setLevel(logging.DEBUG)
    logger.info("Hotkey service starting (pid=%d)", os.getpid())

    registered_release_keys = set()

    def send_event(event_type):
        try:
            conn.send(event_type)
        except Exception as e:
            logger.error("Failed to send event %s: %s", event_type, e)

    def register_hotkey(hotkey_str, on_press_event, on_release_event=None):
        parts = [p.strip() for p in hotkey_str.split("+")]
        trigger_key = parts[-1]
        modifiers = parts[:-1]

        try:
            if modifiers:
                keyboard.add_hotkey(
                    hotkey_str,
                    lambda evt=on_press_event: send_event(evt),
                    suppress=False,
                )
                if on_release_event and trigger_key not in registered_release_keys:
                    registered_release_keys.add(trigger_key)
                    keyboard.on_release_key(
                        trigger_key,
                        lambda e, evt=on_release_event: send_event(evt),
                    )
            else:
                keyboard.on_press_key(
                    trigger_key,
                    lambda e, evt=on_press_event: send_event(evt),
                )
                if on_release_event and trigger_key not in registered_release_keys:
                    registered_release_keys.add(trigger_key)
                    keyboard.on_release_key(
                        trigger_key,
                        lambda e, evt=on_release_event: send_event(evt),
                    )
            logger.debug("Hotkey service: registered %s", hotkey_str)
        except Exception as e:
            logger.error("Hotkey service: failed to register %s: %s", hotkey_str, e)

    # --- Read config ---
    hotkey_dict = hotkey_config.get("hotkey_dictation", "ctrl+space")
    hotkey_cmd = hotkey_config.get("hotkey_command", "f8")
    hotkey_prompt = hotkey_config.get("hotkey_prompt", "f9")
    hotkey_correct = hotkey_config.get("hotkey_correction", "f7")
    hotkey_read = hotkey_config.get("hotkey_readback", "f6")
    hotkey_read_sel = hotkey_config.get("hotkey_readback_selected", "f5")
    mode = hotkey_config.get("hotkey_mode", "hold")

    # --- Register hotkeys ---
    if mode == "hold":
        register_hotkey(hotkey_dict, "dictation_press", "dictation_release")
        register_hotkey(hotkey_cmd, "command_press", "command_release")
        register_hotkey(hotkey_prompt, "prompt_press", "prompt_release")
    else:
        register_hotkey(hotkey_dict, "dictation_toggle")
        register_hotkey(hotkey_cmd, "command_toggle")
        register_hotkey(hotkey_prompt, "prompt_toggle")

    register_hotkey(hotkey_correct, "correction")
    register_hotkey(hotkey_read, "readback")
    register_hotkey(hotkey_read_sel, "readback_selected")

    # Catch-all hook: any key delivery proves Windows hook is still alive.
    # This does NOT suppress or affect normal key processing.
    keyboard.on_press(_touch_last_key)

    logger.info("Hotkey service ready (mode=%s, pid=%d)", mode, os.getpid())
    send_event("ready")

    def _hooks_alive():
        """Check if keyboard hooks are still active.

        The keyboard library uses a listener thread with a Windows hook.
        If Windows killed the hook, the listener thread dies or the hook
        handle becomes invalid. We check both.
        """
        try:
            # keyboard._listener is the hook thread — if it's dead, hooks are dead
            listener = getattr(keyboard, '_listener', None)
            if listener is not None and hasattr(listener, 'is_alive'):
                if not listener.is_alive():
                    return False
            # Also check if any hooks are registered
            if not keyboard._hooks:
                return False
            return True
        except Exception:
            return True  # If we can't check, assume alive

    # --- Event loop: respond to parent commands ---
    try:
        while True:
            try:
                if conn.poll(2.0):
                    cmd = conn.recv()
                    if cmd == "quit":
                        logger.info("Hotkey service shutting down (quit command)")
                        break
                    elif cmd == "ping":
                        if _hooks_alive():
                            with _last_any_key_lock:
                                last_key = _last_any_key_time
                            send_event(("pong", last_key))
                        else:
                            # Don't respond with pong — parent will detect timeout
                            # and restart us. This is the right thing to do.
                            logger.warning("Hooks appear dead — not responding to ping (will be restarted)")
                            send_event("hooks_dead")
            except EOFError:
                logger.warning("Hotkey service: parent pipe closed, exiting")
                break
            except Exception as e:
                logger.error("Hotkey service loop error: %s", e)
                time.sleep(0.5)
    finally:
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        logger.info("Hotkey service stopped (pid=%d)", os.getpid())
