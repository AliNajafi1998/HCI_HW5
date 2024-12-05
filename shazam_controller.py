from shazamio import Shazam
import asyncio
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import os

class shazam_controller:
    def __init__(self):
        """
        Initialize the Shazam instance.
        """
        self.shazam = Shazam()

    async def recognize_song(self, audio_file_path):
        """
        Recognize a song from an audio file.

        Args:
            audio_file_path (str): The path to the audio file.

        Returns:
            dict: A dictionary with details about the recognized song.
        """
        try:
            print("Analyzing the audio file...")
            # Call Shazam API
            result = await self.shazam.recognize(audio_file_path)

            # Debugging step to check the raw result
            print("Raw Shazam API response:", result)

            # Ensure 'track' key exists in the result
            if 'track' not in result:
                print("No track information found in the response.")
                return None

            # Extract track details safely
            track_info = result['track']
            song_details = {
                "track": track_info.get('title', "Unknown Title"),
                "artist": track_info.get('subtitle', "Unknown Artist"),
                "album": next(
                    (metadata.get('text', "Unknown Album")
                    for metadata in track_info.get('sections', [{}])[0].get('metadata', [])
                    if metadata.get('title') == 'Album'),
                    "Unknown Album"
                ),
                "genres": track_info.get('genres', {}).get('primary', "Unknown Genre"),
                "release_date": next(
                    (metadata.get('text', "Unknown Date")
                    for metadata in track_info.get('sections', [{}])[0].get('metadata', [])
                    if metadata.get('title') == 'Released'),
                    "Unknown Date"
                ),
            }
            print(f"Recognized Song: {song_details['track']} by {song_details['artist']}")
            return song_details
        except Exception as e:
            print(f"Error recognizing song: {e}")
            return None


    def recognize_song_sync(self, audio_file_path):
        """
        Wrapper to run the async `recognize_song` method synchronously.
        
        Args:
            audio_file_path (str): The path to the audio file.
        
        Returns:
            dict: Song details or None if recognition failed.
        """
        return asyncio.run(self.recognize_song(audio_file_path))

    def listen_and_recognize(self, duration=10, samplerate=44100):
        """
        Record audio from the computer's microphone and recognize the song.

        Args:
            duration (int): Duration of the recording in seconds.
            samplerate (int): Sample rate for the audio recording.

        Returns:
            dict: Song details or None if recognition failed.
        """
        print(f"Recording for {duration} seconds...")
        try:
            # Determine the number of input channels supported
            input_device_info = sd.query_devices(sd.default.device[0], "input")
            channels = input_device_info['max_input_channels']

            if channels < 1:
                print("No input channels available on the default device.")
                return None

            print(f"Using {channels} channel(s) for recording.")

            # Temporary file for recording
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                audio_path = temp_audio.name
                # Record audio
                audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels)
                sd.wait()  # Wait for the recording to complete
                write(audio_path, samplerate, audio_data)
                print(f"Audio recorded and saved to {audio_path}")

                # Recognize the song
                result = self.recognize_song_sync(audio_path)

                # Clean up the temporary file
                os.remove(audio_path)

                return result
        except Exception as e:
            print(f"Error during recording or recognition: {e}")
            return None
