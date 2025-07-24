import librosa
import librosa.display
import numpy as np
import torch
import torchaudio # While not directly used in the current functions, useful for audio loading/processing if needed elsewhere

# --- Spectrogram Parameters (ensure these match your model's training parameters) ---
SR = 16000 # Sample rate of the audio. IMPORTANT: Match your training SR.
N_FFT = 400 # Length of the FFT window.
HOP_LENGTH = 160 # Number of samples between successive frames.
N_MELS = 128 # Number of Mel bands to generate.
F_MIN = 50 # Minimum frequency for Mel bands.
F_MAX = 8000 # Maximum frequency for Mel bands.
DURATION_SECONDS = 3 # Expected duration of audio for model input. IMPORTANT: Match your training duration.
SAMPLES_TO_PAD = SR * DURATION_SECONDS # Total samples expected for the model.

def audio_to_mel_spectrogram(audio_np: np.ndarray, sr: int = SR) -> np.ndarray:
    """
    Converts a raw audio signal to a Mel spectrogram.

    Args:
        audio_np (np.ndarray): The input audio signal as a NumPy array.
        sr (int): The sample rate of the audio.

    Returns:
        np.ndarray: The Mel spectrogram in decibels (log scale).
    """
    # Pad or truncate audio to a fixed length
    if len(audio_np) < SAMPLES_TO_PAD:
        # Pad with zeros at the end
        padded_audio = np.pad(audio_np, (0, SAMPLES_TO_PAD - len(audio_np)), mode='constant')
    elif len(audio_np) > SAMPLES_TO_PAD:
        # Truncate
        padded_audio = audio_np[:SAMPLES_TO_PAD]
    else:
        padded_audio = audio_np

    # Generate Mel spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(
        y=padded_audio,
        sr=sr,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        fmin=F_MIN,
        fmax=F_MAX
    )
    
    # Convert to decibels (log scale)
    mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
    
    return mel_spectrogram_db

def normalize_mel_spectrogram(mel_spectrogram_db: np.ndarray) -> np.ndarray:
    """
    Normalizes a Mel spectrogram to a 0-1 range.

    Args:
        mel_spectrogram_db (np.ndarray): The Mel spectrogram in decibels.

    Returns:
        np.ndarray: The normalized Mel spectrogram (values between 0 and 1).
    """
    # Normalize to 0-1 range (e.g., min-max scaling)
    # A common range for spectrograms in dB is -80dB to 0dB.

    min_db = -80.0
    max_db = 0.0 # Or np.max(mel_spectrogram_db)
    
    normalized_spectrogram = (mel_spectrogram_db - min_db) / (max_db - min_db)
    normalized_spectrogram = np.clip(normalized_spectrogram, 0, 1) # Ensure values are strictly within 0-1
    
    return normalized_spectrogram

if __name__ == '__main__':
    # --- Example Usage (only runs when spectrogram_utils.py is executed directly) ---
    print("Testing spectrogram_utils.py functions...")
    
    # Generate dummy audio data (e.g., 3 seconds of silence)
    dummy_audio_data = np.zeros(SR * DURATION_SECONDS, dtype=np.float32)
    # Or load a small audio file for testing
    # try:
    #     dummy_audio_data, _ = librosa.load("your_test_audio.wav", sr=SR)
    # except Exception:
    #     print("Could not load test audio. Using dummy data.")

    print(f"Dummy audio shape: {dummy_audio_data.shape}, SR: {SR}")

    # Test audio_to_mel_spectrogram
    mel_db = audio_to_mel_spectrogram(dummy_audio_data, sr=SR)
    print(f"Mel spectrogram (dB) shape: {mel_db.shape}")
    print(f"Mel spectrogram (dB) min: {mel_db.min():.2f}, max: {mel_db.max():.2f}")

    # Test normalize_mel_spectrogram
    normalized_mel = normalize_mel_spectrogram(mel_db)
    print(f"Normalized Mel spectrogram shape: {normalized_mel.shape}")
    print(f"Normalized Mel spectrogram min: {normalized_mel.min():.2f}, max: {normalized_mel.max():.2f}")

    if normalized_mel.min() >= 0 and normalized_mel.max() <= 1:
        print("Normalization successful (values between 0 and 1).")
    else:
        print("Normalization outside 0-1 range. Check parameters.")

    print("Spectrogram utility functions tested successfully.")