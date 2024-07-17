document.addEventListener('DOMContentLoaded', () => {
    const increaseButton = document.getElementById('increase-bandwidth');
    const currentBandwidthElement = document.getElementById('current-bandwidth');
    const remainingTimeElement = document.getElementById('remaining-time');

    // Fetch and display current bandwidth
    fetch(`/networks/${networkId}/appliance/trafficShaping`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Fallo al obtener la configuración de Traffic Shaping');
                console.error(data.error);
            } else {
                const bandwidth = data.globalBandwidthLimits;
                currentBandwidthElement.textContent = `Subida: ${bandwidth.limitUp} Kbps, Bajada: ${bandwidth.limitDown} Kbps`;
            }
        })
        .catch(error => {
            alert('Ocurrió un error');
            console.error('Error:', error);
        });

    // Display server date and time
    const serverDatetimeElement = document.getElementById('server-datetime');
    setInterval(() => {
        const now = new Date();
        serverDatetimeElement.textContent = now.toISOString();
    }, 1000);

    // Increase bandwidth by 50%
    increaseButton.addEventListener('click', () => {
        fetch(`/networks/${networkId}/appliance/trafficShaping`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Fallo al incrementar el ancho de banda');
                console.error(data.error);
            } else {
                alert('Ancho de banda incrementado exitosamente');
                increaseButton.disabled = true;

                // Update current bandwidth
                const bandwidth = data.bandwidth.globalBandwidthLimits;
                currentBandwidthElement.textContent = `Subida: ${bandwidth.limitUp} Kbps, Bajada: ${bandwidth.limitDown} Kbps`;

                // Update remaining time for bandwidth reset
                const resetTime = new Date(data.reset_time);
                const interval = setInterval(() => {
                    const now = new Date();
                    const remainingTime = resetTime - now;
                    if (remainingTime <= 0) {
                        clearInterval(interval);
                        remainingTimeElement.textContent = 'El ancho de banda se ha restablecido a los valores originales';
                        increaseButton.disabled = false;
                    } else {
                        //const hours = Math.floor(remainingTime / 3600000);
                       // const minutes = Math.floor((remainingTime % 3600000) / 60000);
                        const seconds = Math.floor((remainingTime % 10000) / 1000);
                        remainingTimeElement.textContent = ` ${seconds}s`;
                    }
                }, 1000);
            }
        })
        .catch(error => {
            alert('Ocurrió un error');
            console.error('Error:', error);
        });
    });
});







