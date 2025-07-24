from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
import torchaudio
import torchvision.transforms as transforms
from PIL import Image
import io
import numpy as np
import os
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func # For func.now()
from models import Base, Recording
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Model Loading ---
# Import model class and utility functions
try:
    from model import HypernasalityDetectorResNet18
    from spectrogram_utils import audio_to_mel_spectrogram, normalize_mel_spectrogram
except ImportError as e:
    logger.error(f"Error importing model or spectrogram_utils: {e}. Make sure model.py and spectrogram_utils.py are in the 'backend' directory.")
    raise

MODEL_PATH = 'best_hypernasality_resnet18.pth'
NUM_CLASSES = 2
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = HypernasalityDetectorResNet18(num_classes=NUM_CLASSES)
try:
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    logger.info("PyTorch model loaded successfully.")
except FileNotFoundError:
    logger.error(f"Model file not found at {MODEL_PATH}. Please ensure your model weights are in the 'backend' directory.")
    raise
except Exception as e:
    logger.error(f"Error loading PyTorch model: {e}")
    raise

inference_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Ensure directory for saving audio exists
AUDIO_STORAGE_DIR = "recorded_audio"
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)
logger.info(f"Audio storage directory '{AUDIO_STORAGE_DIR}' ensured.")

# --- FastAPI App Setup ----
app = FastAPI()

# CORS middleware for allowing requests from your mobile app 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Be more restrictive in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Hypernasality Detection API - Ready"}

@app.post("/predict")
async def predict_vowel(
    audio: UploadFile = File(...),
    vowel_name: str = Form(...), # Expecting the vowel name as form data
    db: Session = Depends(get_db)
):
    audio_file_path = None # Initialize to None for error handling
    try:
        # 1. Save audio file temporarily (optional, but good for debugging/records)
        audio_filename = f"{uuid.uuid4()}_{audio.filename}"
        audio_file_path = os.path.join(AUDIO_STORAGE_DIR, audio_filename)
        with open(audio_file_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        logger.info(f"Received and saved audio to: {audio_file_path}")

        # Load audio for processing
        # torchaudio.load can sometimes struggle with files not natively recognized by its backend
        # For robustness, consider using soundfile or pydub to load into numpy, then convert to tensor
        try:
            audio_tensor, sr = torchaudio.load(audio_file_path)
        except Exception as e:
            logger.error(f"Failed to load audio with torchaudio: {e}. Attempting with soundfile/io.BytesIO...")
            # Fallback for common formats if torchaudio.load fails directly
            import soundfile as sf
            audio_data, sr = sf.read(io.BytesIO(content))
            audio_tensor = torch.from_numpy(audio_data).unsqueeze(0) # Add batch dim


        audio_np = audio_tensor.squeeze().numpy()
        if audio_np.ndim > 1: # If stereo, convert to mono
            audio_np = audio_np.mean(axis=0)
        logger.info(f"Audio loaded (SR: {sr}, Samples: {len(audio_np)})")

        # Generate Spectrogram
        mel_spectrogram_db = audio_to_mel_spectrogram(audio_np, sr=sr)
        normalized_mel_spectrogram = normalize_mel_spectrogram(mel_spectrogram_db)
        
        # Convert to PIL Image 
        spectrogram_pil = Image.fromarray((normalized_mel_spectrogram * 255).astype(np.uint8)).convert('RGB')
        logger.info("Spectrogram generated.")
        
        # Prepare for Model Input
        input_tensor = inference_transforms(spectrogram_pil).unsqueeze(0).to(DEVICE)
        logger.info(f"Input tensor prepared: {input_tensor.shape}, on device: {DEVICE}")

        # 5. Make Prediction
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            _, predicted_class = torch.max(outputs, 1)
            confidence = probabilities[0][predicted_class.item()].item()

        prediction_label = "Hypernasal" if predicted_class.item() == 1 else "Control"
        logger.info(f"Prediction: {prediction_label}, Confidence: {confidence:.4f}")

        # Store Prediction in Database
        new_recording = Recording(
            vowel_recorded=vowel_name,
            prediction=predicted_class.item(),
            confidence=confidence,
            audio_file_path=audio_file_path # Store path relative to backend dir
        )
        db.add(new_recording)
        db.commit()
        db.refresh(new_recording) # To get the generated ID and timestamp
        logger.info(f"Prediction stored in DB (ID: {new_recording.id}).")

        # Return Response
        return {
            "status": "success",
            "prediction": prediction_label,
            "class_id": predicted_class.item(),
            "confidence": f"{confidence:.4f}",
            "probabilities": probabilities[0].tolist(),
            "recording_id": new_recording.id
        }

    except Exception as e:
        logger.exception("An error occurred during prediction:")
        # Clean up the temporarily saved audio file if an error occurs
        if audio_file_path and os.path.exists(audio_file_path):
            try:
                os.remove(audio_file_path)
                logger.info(f"Cleaned up temporary audio file: {audio_file_path}")
            except Exception as cleanup_e:
                logger.error(f"Error during audio file cleanup: {cleanup_e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction failed: {e}")