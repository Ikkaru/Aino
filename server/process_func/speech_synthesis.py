import sherpa_onnx
import numpy as np
from scipy.io.wavfile import write
from config import VOICE_MODEL, SPEAKER_ID, SPEED
import websockets_func.websockets as websockets

# Create TTS config
config = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=f"{VOICE_MODEL}/castorice_3100epoch.onnx",
            tokens=f"{VOICE_MODEL}/tokens.txt",
            data_dir="./espeak-ng-data",
        ),
        num_threads=1,
        debug=False,
    ),
    max_num_sentences=1,
)

# Create TTS engine
print("\x1B[35m(Speech) \x1B[37m Loading Speech model")
tts = sherpa_onnx.OfflineTts(config)

# Generate speech
async def speech(response):

    audio = tts.generate(
        response, 
        sid=SPEAKER_ID, 
        speed=SPEED,
    )

    # Save audio
    speech_output = np.array(audio.samples, dtype=np.float32)

    # Saving into File
    write('output.wav', audio.sample_rate, speech_output)
    print(f"Saving output audio\nDuration: {len(speech_output) / audio.sample_rate:.2f}")
    
    # Triggering Speak on Client
    await websockets.speak();