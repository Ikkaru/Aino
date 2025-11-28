import { Live2DModel } from 'pixi-live2d-display-lipsyncpatch';
import { Application, Ticker, Rectangle } from 'pixi.js';

(async function() {
    const app = new Application({
        view: document.getElementById('canvas'),
        resizeTo: window,
        autoStart: true,
        backgroundColor: 0x333333,
        enableGlobalMoveEvents: true
    });

    // Define Model
    const model = await Live2DModel.from('/free1/free1.model3.json', {
        ticker: Ticker.shared
    });

    app.stage.addChild(model);

    // transforms
    model.x = window.innerHeight / 2;
    model.y = window.innerHeight / 2;
    model.scale.set(0.2, 0.2);
    model.anchor.set(0.5, 0.5);

    // Interaction states
    let dragging = false;
    let previousPosition = { x: 0, y: 0 };
    // const headArea = new Rectangle(-250, -450, 500, 400);

    // focus points
    let focusX = model.x;
    let focusY = model.y;
    let targetX = model.x;
    let targetY = model.y;

    // Camera Panning Function
    app.stage.eventMode = 'dynamic';
    app.stage.hitArea = app.screen;

    const HEAD_Y_OFFSET = -400;

    app.stage.on('pointerdown', (event) => {
        dragging = true;
        previousPosition = { x: event.data.global.x, y: event.data.global.y };
    });

    app.stage.on('pointerup', () => {
        dragging = false;
    });

    app.stage.on('pointerupoutside', () => {
        dragging = false;
    });

    app.stage.on('pointerout', () => {
        // Reset Character focus when pointer is not deteted
        targetX = model.x;
        targetY = model.y + (HEAD_Y_OFFSET * model.scale.y) + 25;
    });

    app.stage.on('pointermove', (event) => {
        const globalPos = event.data.global;
        const currentHeadOffset = HEAD_Y_OFFSET * model.scale.y;

        // Apply calibration offset to the mouse target
        targetX = globalPos.x;
        targetY = globalPos.y - currentHeadOffset;
        if (dragging) {
            const currentPosition = { x: globalPos.x, y: globalPos.y };
            const dx = currentPosition.x - previousPosition.x;
            const dy = currentPosition.y - previousPosition.y;

            model.x += dx;
            model.y += dy;

            previousPosition = currentPosition;
        }

    });
    // Smooth eye tracking
    app.ticker.add(() => {
        const smoothing = 0.05;
        focusX += (targetX - focusX) * smoothing;
        focusY += (targetY - focusY) * smoothing;

        // Use the smoothed, calibrated points directly
        model.focus(focusX, focusY);
    });



    // // Body Hit Interaction
    // model.on('hit', (hitAreas) => {
    //     if(hitAreas.includes('body')) {
    //         console.log("Body Hit");
    //     }
    // })

    // Lipsync Function
    function audioBufferToWavBlobURL(audioBuffer) {
        const numOfChan = audioBuffer.numberOfChannels;
        const length = audioBuffer.length * numOfChan * 2 + 44;
        const buffer = new ArrayBuffer(length);
        const view = new DataView(buffer);
        const channels = [];
        let i, sample;
        let offset = 0;
        let pos = 0;

        // Menulis Header WAV (RIFF WAVE)
        setUint32(0x46464952); // "RIFF"
        setUint32(length - 8); // file length - 8
        setUint32(0x45564157); // "WAVE"
        setUint32(0x20746d66); // "fmt " chunk
        setUint32(16); // length = 16
        setUint16(1); // PCM (uncompressed)
        setUint16(numOfChan);
        setUint32(audioBuffer.sampleRate);
        setUint32(audioBuffer.sampleRate * 2 * numOfChan); // avg. bytes/sec
        setUint16(numOfChan * 2); // block-align
        setUint16(16); // 16-bit (hardcoded)
        setUint32(0x61746164); // "data" - chunk
        setUint32(length - pos - 4); // chunk length

        // Menulis Data Audio (Interleaving)
        for (i = 0; i < audioBuffer.numberOfChannels; i++)
            channels.push(audioBuffer.getChannelData(i));

        while (pos < audioBuffer.length) {
            for (i = 0; i < numOfChan; i++) {
                sample = Math.max(-1, Math.min(1, channels[i][pos]));
                sample = (0.5 + sample < 0 ? sample * 32768 : sample * 32767) | 0;
                view.setInt16(44 + offset, sample, true);
                offset += 2;
            }
            pos++;
        }

        function setUint16(data) { view.setUint16(pos, data, true); pos += 2; }
        function setUint32(data) { view.setUint32(pos, data, true); pos += 4; }

        // Membuat Blob dan URL Virtual
        return URL.createObjectURL(new Blob([buffer], { type: 'audio/wav' }));
    }

    let audioCtx; // Global variable

    window.triggerSpeak = async (arrayBufferData) => {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 22050 
            });
        }

        if (audioCtx.state === 'suspended') {
            await audioCtx.resume();
        }

        try {
            console.log("Processing audio...");

            // 2. Ubah Raw Bytes dari SocketIO menjadi Float32Array
            const float32Data = new Float32Array(arrayBufferData);

            // 3. Masukkan ke dalam AudioBuffer
            const audioBuffer = audioCtx.createBuffer(1, float32Data.length, audioCtx.sampleRate);
            audioBuffer.copyToChannel(float32Data, 0);
            
            const blobUrl = audioBufferToWavBlobURL(audioBuffer);

            if (model) {
                await model.speak(blobUrl, { 
                    volume: 1
                });
                
                URL.revokeObjectURL(blobUrl);
            }
        } catch (e) {
            console.error("Error di triggerSpeak:", e);
        }
    }

    // Zoom function
    document.addEventListener('wheel', (event) => {
        const zoomFactor = 1.1;
        const minScale = 0.1;
        const maxScale = 2.0;
        let newScale = model.scale.x;

        if (event.deltaY < 0) {
            newScale *= zoomFactor;
        } else {
            newScale /= zoomFactor;
        }

        newScale = Math.max(minScale, Math.min(maxScale, newScale));
        model.scale.set(newScale, newScale);
    });
})();