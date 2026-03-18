let video

let embeddings = []
let images = []

let captureCount = 0
let maxCaptures = 10

let blinkCount = 0
let lastEyeOpen = true
let headMovements = 0
let lastX = null

async function startVideo() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    video.srcObject = stream
}

async function loadModels() {
    await faceapi.nets.tinyFaceDetector.loadFromUri('static/models')
    await faceapi.nets.faceRecognitionNet.loadFromUri('static/models')
    await faceapi.nets.faceLandmark68Net.loadFromUri('static/models')
}

// 🚀 AUTO CAPTURE
async function startCapture() {

    embeddings = []
    images = []
    captureCount = 0

    document.getElementById("status").innerText = "Capturing..."

    let interval = setInterval(async () => {

        const detection = await faceapi.detectSingleFace(video,
            new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks()
            .withFaceDescriptor()

        if (detection) {

            embeddings.push(Array.from(detection.descriptor))

            // 📸 crop face
            const box = detection.detection.box

            let canvas = document.createElement("canvas")
            canvas.width = 200
            canvas.height = 200

            let ctx = canvas.getContext("2d")

            ctx.drawImage(
                video,
                box.x, box.y, box.width, box.height,
                0, 0, 200, 200
            )

            images.push(canvas.toDataURL("image/jpeg"))

            captureCount++

            document.getElementById("status").innerText =
                `Captured ${captureCount}/${maxCaptures}`
        }

        if (captureCount >= maxCaptures) {
            clearInterval(interval)

            document.getElementById("status").innerText =
                "Capture complete ✅"
        }

    }, 500)
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
// async function startCapture() {

//     embeddings = []

//     for (let i = 0; i < 10; i++) {

//         const detection = await faceapi.detectSingleFace(video,
//             new faceapi.TinyFaceDetectorOptions())
//             .withFaceLandmarks()
//             .withFaceDescriptor()

//         if (detection) {
//             embeddings.push(Array.from(detection.descriptor))
//         }

//         await new Promise(r => setTimeout(r, 400))
//     }

//     document.getElementById("status").innerText =
//         "Captured " + embeddings.length + " samples"
// }

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

    let name = document.getElementById("name").value.trim()
    let roll = document.getElementById("roll").value.trim()
    let dept = document.getElementById("dept").value.trim()


    // ✅ VALIDATION
    if (!name || !roll || !dept) {
        alert("All fields are required!")
        return
    }

    if (embeddings.length < 5) {
        alert("Please capture face properly!")
        return
    }

    const res = await fetch("/register_student", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name, roll, dept,
            embeddings: embeddings,
            images: images
        })
    })

    const text = await res.text()

    try {
        const data = JSON.parse(text)
        alert(data.message || data.error)
    }
    catch (e) {
        console.error("Server returned HTML:", text)
        alert("Server error — check backend logs")
    }

    // const data = await res.json()
    // alert(data.message)
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

window.onload = async () => {

    video = document.getElementById("video")

    if (!video) {
        alert("Video element not found!")
        return
    }

    if (typeof faceapi === "undefined") {
        alert("face-api.js failed to load!")
        return
    }

    await loadModels()
    await startVideo()

    setTimeout(() => {
        startCapture()
    }, 2000)
}