const video = document.getElementById("video")

let embeddings = []

let blinkCount = 0
let lastEyeOpen = true
let headMovements = 0
let lastX = null

async function startVideo() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    video.srcObject = stream
}

async function loadModels() {
    await faceapi.nets.tinyFaceDetector.loadFromUri('/models')
    await faceapi.nets.faceRecognitionNet.loadFromUri('/models')
    await faceapi.nets.faceLandmark68Net.loadFromUri('/models')
}

// 👁️ BLINK DETECTION
function getEAR(landmarks) {
    const leftEye = landmarks.getLeftEye()

    const vertical =
        distance(leftEye[1], leftEye[5]) +
        distance(leftEye[2], leftEye[4])

    const horizontal = distance(leftEye[0], leftEye[3])

    return vertical / (2.0 * horizontal)
}

function distance(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y)
}

// 🎯 CAPTURE EMBEDDINGS
async function startCapture() {

    embeddings = []

    for (let i = 0; i < 10; i++) {

        const detection = await faceapi.detectSingleFace(video,
            new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks()
            .withFaceDescriptor()

        if (detection) {
            embeddings.push(Array.from(detection.descriptor))
        }

        await new Promise(r => setTimeout(r, 400))
    }

    document.getElementById("status").innerText =
        "Captured " + embeddings.length + " samples"
}

// 🧠 LIVENESS CHECK
async function startLivenessCheck() {

    blinkCount = 0
    headMovements = 0
    lastX = null

    document.getElementById("livenessStatus").innerText =
        "Please blink and move your head..."

    let frames = 0

    while (frames < 30) {

        const detection = await faceapi.detectSingleFace(video,
            new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks()
            .withFaceDescriptor()

        if (detection) {

            const landmarks = detection.landmarks

            // 👁️ Blink detection
            const ear = getEAR(landmarks)

            if (ear < 0.20 && lastEyeOpen) {
                blinkCount++
                lastEyeOpen = false
            }

            if (ear > 0.25) {
                lastEyeOpen = true
            }

            // 🔄 Head movement
            const box = detection.detection.box

            if (lastX !== null && Math.abs(box.x - lastX) > 10) {
                headMovements++
            }

            lastX = box.x
        }

        frames++
        await new Promise(r => setTimeout(r, 100))
    }

    console.log("Blinks:", blinkCount)
    console.log("Head moves:", headMovements)

    if (blinkCount >= 1 && headMovements >= 2) {
        document.getElementById("livenessStatus").innerText =
            "Liveness Passed ✅"

        markAttendance()
    } else {
        document.getElementById("livenessStatus").innerText =
            "Liveness Failed ❌ Try again"
    }
}

// 📡 REGISTER
async function registerStudent() {

    let name = document.getElementById("name").value
    let roll = document.getElementById("roll").value
    let dept = document.getElementById("dept").value

    const res = await fetch("/register_student", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name, roll, dept,
            embeddings: embeddings
        })
    })

    const data = await res.json()
    alert(data.message)
}

// 📡 ATTENDANCE
async function markAttendance() {

    const detection = await faceapi.detectSingleFace(video,
        new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceDescriptor()

    if (!detection) {
        alert("No face detected")
        return
    }

    const embedding = Array.from(detection.descriptor)

    const res = await fetch("/mark_attendance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ embedding })
    })

    const data = await res.json()
    alert(data.message)
}

startVideo()
loadModels()