const API_URL = '/detect';

const video = document.getElementById("camera");
const canvas = document.getElementById("snapshot");
const flipBtn = document.getElementById("flipCamera");
const captureBtn = document.getElementById("capturePhoto");
const submitBtn = document.getElementById("submitReport");
const locationInput = document.getElementById("location");

let currentCoords = null;
let currentStream = null;
let usingFrontCamera = true;
let lastCapturedBlob = null;

// ------------------- CAMERA -------------------
async function startCamera() {
  if (currentStream) currentStream.getTracks().forEach(track => track.stop());

  try {
    currentStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: usingFrontCamera ? 'user' : 'environment' }
    });
    video.srcObject = currentStream;
  } catch (err) {
    alert("Camera access denied or unavailable!");
    console.error(err);
  }
}

flipBtn.onclick = () => {
  usingFrontCamera = !usingFrontCamera;
  startCamera();
};
// ------------------- LOCATION -------------------
async function requestLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      console.warn("Geolocation not supported");
      currentCoords = { latitude: 0, longitude: 0 };
      locationInput.value = "Location unavailable";
      return resolve(currentCoords);
    }

    // Must be triggered by user gesture (e.g., button click)
    navigator.geolocation.getCurrentPosition(
      pos => {
        currentCoords = pos.coords;
        locationInput.value = `Lat ${pos.coords.latitude.toFixed(5)}, Lng ${pos.coords.longitude.toFixed(5)}`;
        resolve(currentCoords);
      },
      err => {
        console.warn("Geolocation failed:", err);
        // Fallback to 0,0 or any default location
        currentCoords = { latitude: 0, longitude: 0 };
        locationInput.value = "Location unavailable";
        resolve(currentCoords);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  });
}

// ------------------- CAPTURE -------------------
captureBtn.onclick = () => {
  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);

  canvas.toBlob(blob => {
    if (!blob) return alert("Failed to capture image");
    lastCapturedBlob = blob;
    alert("📸 Photo captured! Ready to submit.");
  }, "image/jpeg");
};
// ------------------- SUBMIT -------------------
submitBtn.onclick = async () => {
  if (!lastCapturedBlob) return alert("Please capture a photo first!");

  await requestLocation(); // ensure coords are ready
 
  console.debug(currentCoords)

  const formData = new FormData();
  formData.append("file", lastCapturedBlob, "report.jpg");
  if (currentCoords) {
    formData.append("latitude", currentCoords.latitude);
    formData.append("longitude", currentCoords.longitude);
  }
  else{
    formData.append("latitude",0);
    formData.append("longitude", 0);
  }
  try {
    const res = await fetch(API_URL, { method: "POST", body: formData });
    const data = await res.json();
    
    // Replace the alert with this aesthetic message
    showSuccessMessage(data.message || "Report submitted successfully!");
    
  } catch (err) {
    alert("❌ Failed to submit report!");
    console.error(err);
  }
};

// Add this function to show aesthetic success message
function showSuccessMessage(message) {
  // Create message element
  const messageDiv = document.createElement('div');
  messageDiv.innerHTML = `
    <div style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: #4CAF50;
      color: white;
      padding: 16px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 10px;
      animation: slideIn 0.3s ease-out;
      max-width: 400px;
    ">
      <span style="font-size: 1.2em;">✓</span>
      <span>${message}</span>
    </div>
  `;
  
  // Add styles for animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  // Add to page
  document.body.appendChild(messageDiv);
  
  // Auto remove after 4 seconds
  setTimeout(() => {
    messageDiv.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => {
      if (messageDiv.parentNode) {
        messageDiv.parentNode.removeChild(messageDiv);
      }
    }, 300);
  }, 4000);
}
// ------------------- INIT -------------------
startCamera();
