let video = document.getElementById("video")
let canvas = document.getElementById("canvas")
let ctx = canvas.getContext("2d")

let images = []
let faceCascade

// Auto capture settings
let captureInterval = 1000 // 1 second between captures
let lastCaptureTime = 0
let maxImages = 20

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream
    })

function onOpenCvReady() {

    faceCascade = new cv.CascadeClassifier()

    fetch('/static/haarcascade_frontalface_default.xml')
        .then(res => res.arrayBuffer())
        .then(data => {

            let bytes = new Uint8Array(data)
            cv.FS_createDataFile('/', 'face.xml', bytes, true, false, false)

            faceCascade.load('face.xml')

            startDetection()
        })
}

function startDetection() {

    let src = new cv.Mat(canvas.height, canvas.width, cv.CV_8UC4)
    let gray = new cv.Mat()
    let cap = new cv.VideoCapture(video)

    function process() {

        cap.read(src)

        cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY)

        let faces = new cv.RectVector()

        faceCascade.detectMultiScale(gray, faces, 1.3, 5)

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        if (faces.size() > 0) {

            let face = faces.get(0)

            ctx.strokeStyle = "lime"
            ctx.lineWidth = 2
            ctx.strokeRect(face.x, face.y, face.width, face.height)

            autoCapture()
        }

        requestAnimationFrame(process)
    }

    process()
}

function autoCapture() {

    let now = Date.now()

    if (images.length >= maxImages) {
        return
    }

    if (now - lastCaptureTime > captureInterval) {

        let data = canvas.toDataURL("image/jpeg")

        images.push(data)

        lastCaptureTime = now

        document.getElementById("count").innerText =
            "Images: " + images.length + " / " + maxImages
    }

    if (images.length == maxImages) {
        document.getElementById("faceCapturedMessage").innerText = "Face capture complete. Click Register."
        document.getElementById("registerBtn").disabled = false
    }
}

// function capture() {

//     if (!faceDetected) {

//         document.getElementById("warning").innerText =
//             "No face detected. Please move closer to the camera."

//         return
//     }

//     let data = canvas.toDataURL("image/jpeg")

//     images.push(data)

//     document.getElementById("count").innerText =
//         "Images: " + images.length

//     // document.getElementById("warning").innerText = "Face captured successfully"

//     if (images.length >= 5) {
//         document.getElementById("registerBtn").disabled = false
//     }
// }

function registerStudent() {

    // if (images.length < 15) {

    //     document.getElementById("warning").innerText =
    //         "Please capture at least 15 face images before registering."

    //     return
    // }

    let name = document.getElementById("name").value;
    let roll = document.getElementById("roll").value;
    let dept = document.getElementById("dept").value;

    if (name === "") {
        alert("Username must be filled out");
        return false;
    }
    else if (roll == "" || roll == null) {
        roll.textContent = "Roll No must be filled out";
        return false;
    }
    else if (dept == "" || dept == null) {
        dept.textContent = "Department must be filled out";
        return false;
    }

    fetch("/register_student", {  
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: name,
            roll: roll,
            dept: dept,
            images: images
        })
    })
        // .then(res => res.json())
        .then(res => {
            if(!res.ok){
                throw new Error("Server error")
            }
            return res.json()
        })
        .then(data => alert(data.message))
        .catch(err => console.error(err))
}

function startAttendance() {

    fetch("/start_attendance")
        .then(res => res.json())
        .then(data => alert(data.message))
}

function loadStudents() {

    fetch("/students")
        .then(res => res.json())
        .then(data => {

            let html = "<table><tr><th>ID</th><th>Name</th><th>Roll</th><th>Dept</th></tr>"

            data.forEach(s => {
                html += `<tr>
<td>${s[0]}</td>
<td>${s[1]}</td>
<td>${s[2]}</td>
<td>${s[3]}</td>
</tr>`
            })

            html += "</table>"

            document.getElementById("output").innerHTML = html
        })
}

async function loadAttendance(){

    const res = await fetch("/attendance")
    const data = await res.json()

    console.log(data)
}
// function loadAttendance() { - 16 march 2026

//     fetch("/attendance")
//         .then(res => res.json())
//         .then(data => {

//             let html = "<table><tr><th>Name</th><th>Roll</th><th>Date</th><th>Time</th></tr>"

//             data.forEach(a => {
//                 html += `<tr>
//                 <td>${a[0]}</td>
//                 <td>${a[1]}</td>
//                 <td>${a[2]}</td>
//                 <td>${a[3]}</td>
//                 </tr>`
//             })

//             html += "</table>"

//             document.getElementById("output").innerHTML = html
//         })
// }