const inputs = new URLSearchParams(window.location.search);
const ip = inputs.get('ip');
const port = inputs.get('port');


document.addEventListener('DOMContentLoaded', function () {
    // Do verification of inputs!
    if (!ip || !port) {
        document.body.innerHTML = '<h1>Invalid parameters provided.</h1>';
        return;
    }

    let connection = fetch(`https://${ip}:${port}/`, {
        method: 'POST', // Specify the method
        headers: {
          'Content-Type': 'application/json', // Indicate the content type
        },
        body: JSON.stringify({
            action: 'get_cameras'
        })
      })
      .then(response => {
        response.json().then(data => {
            CreateCameraNodes(data);
        })
      }) // Parse the response as JSON  
      .catch(error => console.error('Error:', error)); // Handle network errors
})


function CreateCameraNode(camera) {

    let container = document.createElement('div')
    container.className = "camera";

    let real_name = Object.keys(camera)[0]

    let title = document.createElement('h2');
    title.innerText = real_name[0].toUpperCase() + real_name.slice(1);

    let position = document.createElement('p');
    position.innerText = `Camera Position: ( ${camera[real_name]} ) `;

    container.appendChild(title)
    container.appendChild(position)

    return container;
}

function CreateCameraNodes(data) {
    document.title = "Camera Panel";
    cameras = data["Cameras"]

    let camerasContainer = document.getElementById('cameras');
    cameras.forEach(element => {
        camerasContainer.appendChild(CreateCameraNode(element));
    });
}
