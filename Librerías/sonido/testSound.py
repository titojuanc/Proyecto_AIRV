import os
import subprocess

# Variables para controlar el volumen
volumeFactor = 100
lastVolume = 100  # Por defecto al volumen máximo inicial

def confirm_volume():
    """Aplicar el nivel de volumen al sistema usando amixer"""
    global volumeFactor
    try:
        # Try different amixer command variations
        commands = [
            ['amixer', '-D', 'pulse', 'sset', 'Master', f'{volumeFactor}%'],
            ['amixer', '-D', 'default', 'sset', 'Master', f'{volumeFactor}%'],
            ['amixer', 'sset', 'Master', f'{volumeFactor}%'],
            ['amixer', 'sset', 'PCM', f'{volumeFactor}%'],
            ['amixer', 'sset', 'Speaker', f'{volumeFactor}%']
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                if result.returncode == 0:
                    print(f"Volumen establecido a: {volumeFactor}%")
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        print("Error: No se pudo ajustar el volumen con amixer")
        return False
        
    except Exception as e:
        print(f"Error al ajustar el volumen: {e}")
        return False

def confirmationSound():
    """Reproducir sonido de confirmación usando aplay"""
    folderPath = "audio"
    file_path = os.path.join(folderPath, "f1.wav")  # Using WAV file

    if not os.path.exists(file_path):
        print(f"Error: Archivo '{file_path}' no encontrado.")
        return False

    try:
        # Play the WAV file with aplay
        result = subprocess.run(['aplay', '-q', file_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error reproduciendo sonido: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error al reproducir sonido: {e}")
        return False

def volumeUp():
    """Aumentar el volumen en un 5% (máx 100%)"""
    global volumeFactor
    volumeFactor = min(volumeFactor + 5, 100)
    confirm_volume()

def volumeDown():
    """Disminuir el volumen en un 5% (mín 0%)"""
    global volumeFactor
    volumeFactor = max(volumeFactor - 5, 0)
    confirm_volume()

def set_volume(newVolume):
    """Establecer el volumen de manera segura con validación"""
    global volumeFactor
    try:
        newVolume = int(newVolume)
        if 0 <= newVolume <= 100:
            volumeFactor = newVolume
            confirm_volume()
        else:
            print("Error: volumen fuera de rango (0-100).")
    except ValueError:
        print("Error: entrada no válida, ingrese un número.")

def mute():
    """Silenciar el sonido, guardando el volumen anterior"""
    global volumeFactor, lastVolume
    lastVolume = volumeFactor
    
    try:
        # Try different mute commands
        commands = [
            ['amixer', '-D', 'pulse', 'sset', 'Master', 'mute'],
            ['amixer', '-D', 'default', 'sset', 'Master', 'mute'],
            ['amixer', 'sset', 'Master', 'mute'],
            ['amixer', 'sset', 'PCM', 'mute']
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                if result.returncode == 0:
                    volumeFactor = 0
                    print("Silenciado")
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
                
        print("Error: No se pudo silenciar con amixer")
        return False
        
    except Exception as e:
        print(f"Error al silenciar: {e}")
        return False

def unmute():
    """Restaurar el volumen si estaba previamente silenciado"""
    global volumeFactor
    if volumeFactor == 0:
        volumeFactor = lastVolume
        
        try:
            # Try different unmute commands
            commands = [
                ['amixer', '-D', 'pulse', 'sset', 'Master', 'unmute'],
                ['amixer', '-D', 'default', 'sset', 'Master', 'unmute'],
                ['amixer', 'sset', 'Master', 'unmute'],
                ['amixer', 'sset', 'PCM', 'unmute']
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    if result.returncode == 0:
                        # Now set the volume
                        if confirm_volume():
                            print(f"Sonido activado - Volumen: {volumeFactor}%")
                            return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
                    
            print("Error: No se pudo activar el sonido con amixer")
            return False
            
        except Exception as e:
            print(f"Error al activar sonido: {e}")
            return False
    else:
        print("El sonido ya está activado")
        return True

# Test function
def test_audio_system():
    """Función para probar el sistema de audio completo"""
    print("=== Probando sistema de audio ===")
    
    print("1. Configurando volumen al 80%...")
    set_volume(80)
    
    print("2. Probando reproducción de sonido...")
    if confirmationSound():
        print("✓ Sonido reproducido correctamente")
    else:
        print("✗ Error reproduciendo sonido")
    
    print("3. Probando mute...")
    mute()
    
    print("4. Probando unmute...")
    unmute()
    
    print("5. Probando reproducción después de unmute...")
    if confirmationSound():
        print("✓ Sonido reproducido correctamente después de unmute")
    else:
        print("✗ Error reproduciendo sonido después de unmute")
    
    print("6. Probando aumento de volumen después de unmute...")
    volumeUp()

    print("7. Probando baja de volumen después de unmute...")
    volumeDown()

    print("=== Prueba completada ===")

# Run test if this file is executed directly
if __name__ == "__main__":
    test_audio_system()