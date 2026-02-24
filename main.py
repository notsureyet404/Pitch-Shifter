import flet as ft
import os
import tempfile
import shutil
import atexit
from src.audio_processor import detect_key, process_audio, get_target_key

def main(page: ft.Page):
    page.title = "Pitch-Shifter"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 800
    page.window_height = 600
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # State
    state = {
        "file_path": None,
        "original_key": "Unknown",
        "processed_buffer": None,
        "processed_path": None
    }

    def cleanup_temp_file():
        if state["processed_path"] and os.path.exists(state["processed_path"]):
            try:
                os.remove(state["processed_path"])
                print(f"Cleaned up temp file: {state['processed_path']}")
            except Exception as e:
                print(f"Error cleaning up temp file: {e}")

    atexit.register(cleanup_temp_file)

    # Components

    # 1. Header
    header = ft.Text("Pitch-Shifter", size=30, weight=ft.FontWeight.BOLD)

    # 2. File Picker
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            state["file_path"] = file_path
            selected_file_text.value = f"Selected: {e.files[0].name}"

            # Detect Key
            key = detect_key(file_path)
            state["original_key"] = key
            original_key_text.value = f"Original Key: {key}"

            # Reset target key
            update_target_key()

            # Enable controls
            apply_btn.disabled = False
            slider.disabled = False

            page.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    upload_btn = ft.ElevatedButton(
        "Upload Audio",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: pick_files_dialog.pick_files(
            allow_multiple=False,
            allowed_extensions=["mp3", "wav", "flac"]
        )
    )
    selected_file_text = ft.Text("No file selected", italic=True)

    # 3. Key Display
    original_key_text = ft.Text("Original Key: -", size=20, weight=ft.FontWeight.BOLD)
    target_key_text = ft.Text("Target Key: -", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_200)

    # 4. Slider
    def slider_changed(e):
        update_target_key()
        page.update()

    def update_target_key():
        if state["original_key"] and state["original_key"] != "Unknown":
            new_key = get_target_key(state["original_key"], int(slider.value))
            target_key_text.value = f"Target Key: {new_key}"
        else:
            target_key_text.value = "Target Key: -"

    slider = ft.Slider(
        min=-12, max=12, divisions=24, value=0, label="{value}",
        on_change=slider_changed,
        disabled=True
    )

    # 5. Apply & Play
    audio_player = ft.Audio(autoplay=False)
    page.overlay.append(audio_player)

    def apply_click(e):
        if not state["file_path"]:
            return

        apply_btn.text = "Processing..."
        apply_btn.disabled = True
        page.update()

        try:
            # Process Audio
            buffer = process_audio(state["file_path"], slider.value)
            state["processed_buffer"] = buffer

            # Save to temp file for playback
            # We need a persistent temp file so the player can access it
            # Using tempfile.NamedTemporaryFile with delete=False
            if state["processed_path"] and os.path.exists(state["processed_path"]):
                os.remove(state["processed_path"])

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                shutil.copyfileobj(buffer, tmp)
                state["processed_path"] = tmp.name

            # Update Audio Player
            audio_player.src = state["processed_path"]
            audio_player.update()

            save_btn.disabled = False
            apply_btn.text = "Apply Pitch Shift"
            apply_btn.disabled = False

            page.snack_bar = ft.SnackBar(ft.Text("Processing Complete!"))
            page.snack_bar.open = True

        except Exception as ex:
            print(f"Error applying effect: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            page.snack_bar.open = True
            apply_btn.text = "Apply Pitch Shift"
            apply_btn.disabled = False

        page.update()

    apply_btn = ft.ElevatedButton("Apply Pitch Shift", on_click=apply_click, disabled=True)

    # 6. Save
    def save_file_result(e: ft.FilePickerResultEvent):
        if e.path and state["processed_buffer"]:
            try:
                with open(e.path, 'wb') as f:
                    state["processed_buffer"].seek(0)
                    shutil.copyfileobj(state["processed_buffer"], f)
                page.snack_bar = ft.SnackBar(ft.Text(f"Saved to {e.path}"))
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                print(f"Error saving file: {ex}")

    save_file_dialog = ft.FilePicker(on_result=save_file_result)
    page.overlay.append(save_file_dialog)

    save_btn = ft.ElevatedButton(
        "Save Result",
        icon=ft.icons.SAVE,
        on_click=lambda _: save_file_dialog.save_file(
            allowed_extensions=["wav"],
            file_name="processed_audio.wav"
        ),
        disabled=True
    )

    # Layout
    page.add(
        ft.Column(
            [
                header,
                ft.Divider(),
                ft.Row([upload_btn, selected_file_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        original_key_text,
                        target_key_text
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=10
                ),
                ft.Text("Pitch Shift (Semitones)", size=16),
                slider,
                ft.Row([apply_btn, save_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text("Preview controls are built-in to the Audio player (once processed).", size=12, italic=True)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

    # Add play button for audio player manually if needed, or rely on auto-play or just add controls?
    # Flet Audio doesn't have visible controls by default.
    # We should add a play/pause button that controls the audio_player.

    def play_audio(e):
        audio_player.play()

    def pause_audio(e):
        audio_player.pause()

    play_btn = ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=play_audio, tooltip="Play Preview")
    pause_btn = ft.IconButton(icon=ft.icons.PAUSE, on_click=pause_audio, tooltip="Pause Preview")

    page.add(ft.Row([play_btn, pause_btn], alignment=ft.MainAxisAlignment.CENTER))


if __name__ == "__main__":
    ft.app(target=main)
