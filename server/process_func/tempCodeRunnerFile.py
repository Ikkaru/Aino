

    # Save audio
    speech_output = np.array(audio.samples, dtype=np.float32)

    # Saving into File
    write('output.wav', audio.sample_rate, speech_output)
    print(f"Saving output audio\nDuration: {len(speech_output) / audio.sample_rate:.2f}")
    
    # Triggering Speak on Client
    await websockets.speak();