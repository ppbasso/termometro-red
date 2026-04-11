package termometrored.api.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import termometrored.api.model.TelemetriaBus;
// Clean Code: Eliminamos la importación del Repositorio. El Controlador ya no toca la BD directa.
import termometrored.api.service.TelemetriaBusService;

import java.util.List;

@RestController
@RequestMapping("/api/telemetria")
// Habilita peticiones desde cualquier Frontend (Streamlit, React, Mobile) evitando el bloqueo de seguridad del navegador
@CrossOrigin(origins = "*") 
public class TelemetriaBusController {

    // INYECCIÓN DE DEPENDENCIAS (SOLID):
    // Conectamos el "Mesero" (Controlador) con el "Chef" (Servicio).
    @Autowired
    private TelemetriaBusService service;

    // Endpoint GET: Escucha en http://localhost:8080/api/telemetria
    // @RequestParam permite capturar variables de la URL (ej: ?recorrido=210)
    // required = false significa que si el usuario no manda la micro, no se cae, simplemente asume nulo.
    @GetMapping
    public List<TelemetriaBus> obtenerTelemetria(
            @RequestParam(required = false) String recorrido) {
        
        // Regla de Negocio (Clean Code: Ramificación simple y legible)
        if (recorrido != null && !recorrido.trim().isEmpty()) {
            // Si el cliente pide una micro específica, el Servicio la filtra
            return service.obtenerPorRecorrido(recorrido);
        } else {
            // Magia de Spring: Esto equivale a "SELECT * FROM telemetria_buses"
            // Si no se especifica recorrido, el Servicio trae el universo completo
            return service.obtenerTodos();
        }
    }
}