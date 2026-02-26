// Three.js Parallax Background
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('canvas-container').appendChild(renderer.domElement);

const geometry = new THREE.TorusGeometry(10, 3, 16, 100);
const material = new THREE.MeshBasicMaterial({ color: 0x00f2ff, wireframe: true });
const torus = new THREE.Mesh(geometry, material);
scene.add(torus);
camera.position.z = 30;

function animate() {
    requestAnimationFrame(animate);
    torus.rotation.x += 0.01;
    torus.rotation.y += 0.005;
    renderer.render(scene, camera);
}
animate();

// API Call Function
async function analyzeData() {
    const statusText = document.getElementById('statusText');
    const tipsList = document.getElementById('tipsList');
    
    statusText.innerText = "Scanning Biometrics...";
    
    const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            "patient_metrics": { "scalp_health": "dry", "vision_clarity": "blurred" }
        })
    });
    
    const result = await response.json();
    
    // AI Output Display
    statusText.innerText = `Diagnosis: ${result.diagnosis}`;
    tipsList.innerHTML = result.tips.map(tip => `<li>${tip}</li>`).join('');
}