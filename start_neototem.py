#!/usr/bin/env python3
"""
Script de inicio automático para NeoTotem
Inicia tanto el backend como el frontend de manera coordinada
"""
import subprocess
import time
import os
import sys
import signal
import threading

def check_port(port):
    """Verifica si un puerto está en uso"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        return result == 0

def kill_port(port):
    """Mata procesos en un puerto específico"""
    try:
        os.system(f"lsof -ti:{port} | xargs kill -9 2>/dev/null")
        time.sleep(1)
    except:
        pass

def start_backend():
    """Inicia el servidor backend FastAPI"""
    print("🔧 Iniciando backend...")
    
    # Limpiar puertos
    kill_port(8001)
    
    # Verificar dependencias
    try:
        import uvicorn
        from fastapi import FastAPI
    except ImportError:
        print("❌ Dependencias faltantes. Instalando...")
        os.system("pip install fastapi uvicorn sqlalchemy")
    
    # Inicializar base de datos
    print("🗄️ Inicializando base de datos...")
    os.system("python3 init_db.py")
    
    # Iniciar servidor
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8001", 
        "--reload"
    ]
    
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_frontend():
    """Inicia el frontend Flutter"""
    print("📱 Iniciando frontend...")
    
    # Limpiar puerto
    kill_port(3000)
    
    # Cambiar al directorio del frontend
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print("❌ Directorio frontend no encontrado")
        return None
    
    # Verificar Flutter
    flutter_check = subprocess.run(["flutter", "--version"], capture_output=True)
    if flutter_check.returncode != 0:
        print("❌ Flutter no está instalado o no está en PATH")
        return None
    
    # Iniciar Flutter
    cmd = ["flutter", "run", "-d", "chrome", "--web-port", "3000"]
    
    return subprocess.Popen(cmd, cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def monitor_processes(backend_proc, frontend_proc):
    """Monitorea los procesos y muestra su estado"""
    print("\n🎯 NeoTotem iniciado!")
    print("=" * 50)
    print("🔗 Backend API: http://localhost:8001")
    print("📖 Documentación: http://localhost:8001/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("=" * 50)
    print("💡 Presiona Ctrl+C para detener todos los servicios")
    print()
    
    try:
        while True:
            # Verificar estado del backend
            if backend_proc and backend_proc.poll() is not None:
                print("❌ Backend se detuvo inesperadamente")
                break
            
            # Verificar estado del frontend
            if frontend_proc and frontend_proc.poll() is not None:
                print("❌ Frontend se detuvo inesperadamente")
            
            # Mostrar estado cada 30 segundos
            backend_status = "✅" if check_port(8001) else "❌"
            frontend_status = "✅" if check_port(3000) else "❌"
            
            print(f"Estado: Backend {backend_status} | Frontend {frontend_status}", end="\r")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo servicios...")
        
        # Detener procesos
        if backend_proc:
            backend_proc.terminate()
            backend_proc.wait()
        
        if frontend_proc:
            frontend_proc.terminate()
            frontend_proc.wait()
        
        # Limpiar puertos
        kill_port(8001)
        kill_port(3000)
        
        print("✅ Todos los servicios han sido detenidos")

def main():
    """Función principal"""
    print("🚀 Iniciando NeoTotem...")
    
    # Verificar directorio de trabajo
    if not os.path.exists("api/main.py"):
        print("❌ No estás en el directorio correcto del proyecto")
        print("💡 Ejecuta este script desde la raíz del proyecto apt-totem")
        sys.exit(1)
    
    backend_proc = None
    frontend_proc = None
    
    try:
        # Iniciar backend
        backend_proc = start_backend()
        time.sleep(3)  # Dar tiempo al backend para iniciar
        
        # Verificar que el backend esté corriendo
        if not check_port(8001):
            print("❌ El backend no se pudo iniciar en el puerto 8001")
            return
        
        print("✅ Backend iniciado correctamente")
        
        # Iniciar frontend
        frontend_proc = start_frontend()
        
        # Monitorear procesos
        monitor_processes(backend_proc, frontend_proc)
        
    except Exception as e:
        print(f"❌ Error durante el inicio: {e}")
    finally:
        # Limpiar al salir
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()

if __name__ == "__main__":
    main()


