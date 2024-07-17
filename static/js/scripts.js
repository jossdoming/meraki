document.getElementById('get-organization-button').addEventListener('click', () => {
    fetch('/organizations')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Fallo al obtener Organizaciones');
                console.error(data.error);
            } else {
                document.getElementById('result-data').textContent = JSON.stringify(data.data, null, 2);
            }
        })
        .catch(error => {
            alert('Ocurrió un error');
            console.error('Error:', error);
        });
});

// Obtener dispositivos para una organización específica
document.getElementById('fetch-devices-button').addEventListener('click', () => {
    const networkId = document.getElementById('network-id').value;
    fetch(`/organizations/${networkId}/devices`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Fallo al obtener dispositivos');
                console.error(data.error);
            } else {
                document.getElementById('result-data').textContent = JSON.stringify(data.data, null, 2);
            }
        })
        .catch(error => {
            alert('Ocurrió un error');
            console.error('Error:', error);
        });
});

// Manejar el envío del formulario de inicio de sesión
document.getElementById('login-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const networkId = document.getElementById('network-id').value;
    if (networkId) {
        window.location.href = `/dashboard/${networkId}`;
    } else {
        alert('Por favor, ingrese un ID de red válido.');
    }
});



document.getElementById('login-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const networkId = document.getElementById('network-id').value;
    window.location.href = `/dashboard/${networkId}`;
});
