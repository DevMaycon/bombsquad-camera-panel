const inputs = new URLSearchParams(window.location.search);
const ip = inputs.get('ip');
const port = inputs.get('port');
const server_hostname = `https://${ip}:${port}/`

// Do verification of inputs!
if (!ip || !port) {
    document.body.innerHTML = '<h1>Invalid parameters provided.</h1>';
}

document.addEventListener('DOMContentLoaded', function () {
    let connection = fetch(server_hostname, {
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

function SetRemoteCamera(camera_element) {
    let connection = fetch(server_hostname, {
        method: 'POST', // Specify the method
        headers: {
          'Content-Type': 'application/json', // Indicate the content type
        },
        body: JSON.stringify({
            action: 'set_camera',
            camera_id: camera_element.className.split(' ')[1].toLowerCase()
        })
      })
      .then(response => {
        response.json().then(data => {
            console.log('Success:', data);
        })
      }) // Parse the response as JSON  
      .catch(error => console.error('Error:', error)); // Handle network errors
}

function CreateCameraNode(camera, camera_name) {
    let real_name = camera_name

    let container = document.createElement('div')
    container.className = `camera ${real_name}` ;
    container.onclick = function() { SetRemoteCamera(container); };

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
    cameras = data["cameras"]

    let camerasContainer = document.getElementById('cameras');
    Object.keys(cameras).forEach(camera_name => {
        camerasContainer.appendChild(CreateCameraNode(cameras[camera_name], camera_name));
    });
}
