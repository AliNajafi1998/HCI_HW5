import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyController:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-modify-playback-state user-read-playback-state"
        ))
    
    def play(self):
        """
        Resume playback on the current active device.
        """
        try:
            self.sp.start_playback()
            print("Playback started.")
        except Exception as e:
            print(f"Error during play: {e}")
    
    def next_track(self):
        """
        Skip to the next track on the current active device.
        """
        try:
            self.sp.next_track()
            print("Skipped to the next track.")
        except Exception as e:
            print(f"Error during next track: {e}")
    
    def volume_up(self, step=10):
        """
        Increase volume by a specified step.
        """
        try:
            current_device = self._get_active_device()
            if current_device:
                new_volume = min(current_device['volume_percent'] + step, 100)
                self.sp.volume(new_volume)
                print(f"Volume increased to {new_volume}%.")
            else:
                print("No active device found.")
        except Exception as e:
            print(f"Error during volume up: {e}")
    
    def volume_down(self, step=10):
        """
        Decrease volume by a specified step.
        """
        try:
            current_device = self._get_active_device()
            print("DEVICE: ", current_device)
            if current_device:
                new_volume = max(current_device['volume_percent'] - step, 0)
                self.sp.volume(new_volume)
                print(f"Volume decreased to {new_volume}%.")
            else:
                print("No active device found.")
        except Exception as e:
            print(f"Error during volume down: {e}")

    def _get_active_device(self):
        """
        Retrieve the current active device.
        """
        devices = self.sp.devices()
        for device in devices['devices']:
            if device['is_active']:
                return device
        return None