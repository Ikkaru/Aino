import { io } from "socket.io-client";

let audioFile = "../output.wav"

// Connect to websocket
const socket = io("http://localhost:8000/");
socket.on("connect", () => {
    console.log("Connected to the Server");
});

// Speak Function
socket.on("triggerSpeak", (data) => {
    
    if (typeof window.triggerSpeak == "function") {
        window.triggerSpeak(data);
    }
    else {
        console.warn("Error: Model not Loaded Yet");
    }
});

// Checking when Disconnected
socket.on("disconnect", () => {
    console.warn("Disconnected from server, Reconnecting...")
});