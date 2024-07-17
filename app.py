from flask import Flask, jsonify, render_template, request
import requests
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# Configuración de la API de Meraki
MERAKI_API_KEY = 'e44bfbb8c75b53dc36c4eb81b7dc9b867fd91350'
BASE_URL = 'https://api.meraki.com/api/v1'

# Variable para almacenar el estado del ancho de banda
bandwidth_reset_time = None

# Función para obtener los headers requeridos por la API de Meraki
def get_headers():
    return {
        'Authorization': f'Bearer {MERAKI_API_KEY}',
        'Accept': 'application/json'
    }

# Ruta principal para renderizar el formulario de login
@app.route('/')
def index():
    return render_template('index.html')

# Ruta del dashboard
@app.route('/dashboard/<network_id>')
def dashboard(network_id):
    return render_template('dashboard.html', network_id=network_id)

# Endpoint para obtener la lista de organizaciones desde Meraki
@app.route('/organizations', methods=['GET'])
def get_organizations():
    try:
        response = requests.get(f'{BASE_URL}/organizations', headers=get_headers())
        response.raise_for_status()
        return jsonify({
            'message': 'Organizaciones obtenidas exitosamente',
            'data': response.json()
        }), 200
    except requests.exceptions.RequestException as e:
        print(f'Error obteniendo organizaciones: {e}')
        return jsonify({'error': 'Fallo al obtener organizaciones'}), 500

@app.route('/organizations/<organization_id>/devices', methods=['GET'])
def get_devices(organization_id):
    try:
        response = requests.get(f'{BASE_URL}/organizations/{organization_id}/devices', headers=get_headers())
        response.raise_for_status()
        return jsonify({
            'data': response.json()
        }), 200
    except requests.exceptions.RequestException as e:
        print(f'Error obteniendo dispositivos: {e}')
        return jsonify({'error': 'Fallo al obtener dispositivos'}), 500

# Endpoint para obtener la configuración de traffic shaping de una red específica
@app.route('/networks/<network_id>/appliance/trafficShaping', methods=['GET'])
def get_traffic_shaping(network_id):
    try:
        response = requests.get(f'{BASE_URL}/networks/{network_id}/appliance/trafficShaping', headers=get_headers())
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        print(f'Error obteniendo configuración de traffic shaping para la red {network_id}: {e}')
        return jsonify({'error': 'Fallo al obtener configuración de traffic shaping'}), 500

# Función para resetear el ancho de banda después de 1 hora
def reset_bandwidth(network_id, original_settings):
    global bandwidth_reset_time
    try:
        threading.Event().wait(10)  # Espera 1 hora
        response = requests.put(f'{BASE_URL}/networks/{network_id}/appliance/trafficShaping', headers=get_headers(), json=original_settings)
        response.raise_for_status()
        bandwidth_reset_time = None
        print(f'Ancho de banda reseteado a la configuración original para la red {network_id}')
    except requests.exceptions.RequestException as e:
        print(f'Error reseteando el ancho de banda: {e}')

# Endpoint para actualizar la configuración de traffic shaping de una red específica
@app.route('/networks/<network_id>/appliance/trafficShaping', methods=['PUT'])
def update_traffic_shaping(network_id):
    global bandwidth_reset_time
    try:
        url = f'{BASE_URL}/networks/{network_id}/appliance/trafficShaping'
        headers = {
            'X-Cisco-Meraki-API-Key': MERAKI_API_KEY,
            'Content-Type': 'application/json'
        }
        data = request.get_json()

        # Obtener la configuración actual
        current_response = requests.get(url, headers=headers)
        current_response.raise_for_status()
        current_settings = current_response.json()

        # Actualizar el ancho de banda
        updated_bandwidth = {
            'globalBandwidthLimits': {
                'limitUp': int(current_settings['globalBandwidthLimits']['limitUp'] * 1.5),
                'limitDown': int(current_settings['globalBandwidthLimits']['limitDown'] * 1.5)
            }
        }
        update_response = requests.put(url, headers=headers, json=updated_bandwidth)
        update_response.raise_for_status()

        # Programar el reseteo del ancho de banda en 10 segundos
        bandwidth_reset_time = datetime.now() + timedelta(seconds=10)
        threading.Thread(target=reset_bandwidth, args=(network_id, current_settings)).start()

        return jsonify({
            'message': 'Configuración de traffic shaping actualizada exitosamente',
            'reset_time': bandwidth_reset_time.strftime('%Y-%m-%d %H:%M:%S'),
            'bandwidth': updated_bandwidth
        }), 200
    except requests.exceptions.RequestException as e:
        print(f'Error actualizando configuración de traffic shaping: {e}')
        return jsonify({'error': 'Fallo al actualizar configuración de traffic shaping'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
