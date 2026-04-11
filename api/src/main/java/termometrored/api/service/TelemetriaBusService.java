package termometrored.api.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import termometrored.api.model.TelemetriaBus;
import termometrored.api.repository.TelemetriaBusRepository;

import java.util.List;

@Service // Esta anotación le dice a Spring que esta clase es el "Cerebro" de negocio
public class TelemetriaBusService {

    // INYECCIÓN DE DEPENDENCIAS:
    // Spring Boot instancia y conecta el repositorio automáticamente.
    // El servicio no sabe cómo funciona la base de datos, solo usa esta interfaz.
    @Autowired
    private TelemetriaBusRepository repository;

    // Método 1: Obtener la foto completa (Útil para un dashboard general)
    public List<TelemetriaBus> obtenerTodos() {
        return repository.findAll();
    }

    // Método 2: La regla de negocio de nuestro "Auditor Ciudadano"
    // Recibe el parámetro desde la web y se lo pasa a la capa de datos
    public List<TelemetriaBus> obtenerPorRecorrido(String recorrido) {
        return repository.findByRecorrido(recorrido);
    }
}