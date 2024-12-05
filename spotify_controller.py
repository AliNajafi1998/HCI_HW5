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

    def pause(self):
        """
        Pause playback on the current active device.
        """
        try:
            self.sp.pause_playback()
            print("Playback paused.")
        except Exception as e:
            print(f"Error during pause: {e}")
    
    def next_track(self):
        """
        Skip to the next track on the current active device.
        """
        try:
            self.sp.next_track()
            print("Skipped to the next track.")
        except Exception as e:
            print(f"Error during next track: {e}")
    
    def previous_track(self):
        """
        Skip to the previous track on the current active device.
        """
        try:
            self.sp.previous_track()
            print("Skipped to the previous track.")
        except Exception as e:
            print(f"Error during previous track: {e}")

    def like_current_track(self):
        """
        Add the current track to the user's liked songs.
        """
        try:
            current_track = self.sp.current_playback()
            if current_track and 'item' in current_track and current_track['item']:
                track_id = current_track['item']['id']
                self.sp.current_user_saved_tracks_add([track_id])
                print(f"Added track {current_track['item']['name']} by {current_track['item']['artists'][0]['name']} to liked songs.")
            else:
                print("No track is currently playing.")
        except Exception as e:
            print(f"Error liking the current track: {e}")


    
    def volume_up(self, step=10):
        """
        Increase volume by a specified step.
        """
        try:
            devices = self.sp.devices()
            for device in devices['devices']:
                if device['is_active']:
                    if 'volume_percent' not in device:
                        print(f"Volume control not supported on device: {device['name']}")
                        return
                    new_volume = min(device['volume_percent'] + step, 100)
                    self.sp.volume(new_volume)
                    print(f"Volume increased to {new_volume}% on {device['name']}.")
                    return
            print("No active device found.")
        except Exception as e:
            print(f"Error during volume up: {e}")

    def volume_down(self, step=10):
        """
        Decrease volume by a specified step.
        """
        try:
            devices = self.sp.devices()
            for device in devices['devices']:
                if device['is_active']:
                    if 'volume_percent' not in device:
                        print(f"Volume control not supported on device: {device['name']}")
                        return
                    new_volume = max(device['volume_percent'] - step, 0)
                    self.sp.volume(new_volume)
                    print(f"Volume decreased to {new_volume}% on {device['name']}.")
                    return
            print("No active device found.")
        except Exception as e:
            print(f"Error during volume down: {e}")


    def _get_current_volume(self):
        """
        Retrieve the current volume from the active device.
        """
        try:
            devices = self.sp.devices()
            for device in devices['devices']:
                if device['is_active']:
                    return device.get('volume_percent', 50)  # Default to 50% if no volume is found
            print("No active device found.")
        except Exception as e:
            print(f"Error retrieving current volume: {e}")
        return 50  # Return a safe default if volume cannot be retrieved


    def _get_active_device(self):
        """
        Retrieve the current active device.
        """
        devices = self.sp.devices()
        for device in devices['devices']:
            if device['is_active']:
                return device
        return None
    
    def play_search_result(self, query):
        """
        Search for a track on Spotify and play the top result.

        Args:
            query (str): The search query (e.g., "Song Name Artist Name").
        """
        try:
            # Search for the track on Spotify
            results = self.sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                print(f"Playing track: {results['tracks']['items'][0]['name']} by {results['tracks']['items'][0]['artists'][0]['name']}")
                # Start playback of the track
                self.sp.start_playback(uris=[track_uri])
            else:
                print("No tracks found for the given query.")
        except Exception as e:
            print(f"Error during play_search_result: {e}")
