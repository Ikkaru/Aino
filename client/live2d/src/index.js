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
        console.log("Pointer Not Detected")
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

    const audioFile = "/output.wav"

    // Lipsync Function
    window.triggerSpeak = () => {
        console.log("Playing Speech: ". audioFile);
        if (model) {
            model.speak(audioFile, {
                volume: 1,
            })
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