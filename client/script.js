const Live2DModel = PIXI.live2d.Live2DModel;



(async function () {
    const app = new PIXI.Application({
        view: document.getElementById('canvas'),
        autoStart: true,
        resizeTo: window,
        backgroundColor: 0x333333
    });

    const model = await Live2DModel.from('./free1/free1.model3.json');

    app.stage.addChild(model);

    // Create expression buttons
    const expressionNames = model.internalModel.settings.expressions.map(e => e.Name);
    const buttonsContainer = document.getElementById('expression-buttons');

    // Add a reset button
    const resetButton = document.createElement('button');
    resetButton.innerText = 'Reset';
    resetButton.onclick = () => {
        model.expression();
    };
    buttonsContainer.appendChild(resetButton);

    for (const name of expressionNames) {
        const button = document.createElement('button');
        // Clean up the name for display
        button.innerText = name.replace('.exp3.json', '').replace(/_/g, ' ');
        button.onclick = () => {
            model.expression(name);
        };
        buttonsContainer.appendChild(button);
    }

    // transforms
    model.x = window.innerWidth / 2;
    model.y = window.innerHeight / 2;
    model.scale.set(0.2, 0.2);
    model.anchor.set(0.5, 0.5);

    // Start idle animation
    model.motion('Idle');

    // interaction
    model.on('hit', (hitAreas) => {
        if (hitAreas.includes('body')) {
            model.motion('tap_body');
        }
    });

    // Interaction states
    let dragging = false;
    let previousPosition = { x: 0, y: 0 };
    let isPatting = false;
    const headArea = new PIXI.Rectangle(-250, -450, 500, 400);

    // Smoothed focus points
    let focusX = model.x;
    let focusY = model.y;
    let targetX = model.x;
    let targetY = model.y;

    // Add camera-like panning functionality
    app.stage.interactive = true;
    app.stage.hitArea = app.screen;

    const HEAD_Y_OFFSET = -400; // Estimated offset from model origin to eyes in model coordinates

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
        // When the pointer leaves the canvas, reset the focus to the model's origin
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

        // Head pat interaction
        const localPos = model.toLocal(globalPos);

        if (headArea.contains(localPos.x, localPos.y)) {
            if (!isPatting) {
                isPatting = true;
                // Stop idle animation and set expression
                model.internalModel.motionManager.stopAllMotions();
                model.expression('3.exp3.json');
            }
        } else {
            if (isPatting) {
                isPatting = false;
                // Reset expression and restart idle animation
                model.expression();
                model.motion('Idle');
            }
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

    // Add zoom functionality
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
