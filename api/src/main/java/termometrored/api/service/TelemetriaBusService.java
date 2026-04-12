package termometrored.api.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import termometrored.api.model.TelemetriaBus;
import termometrored.api.repository.TelemetriaBusRepository;

import java.util.List;

@Service
public class TelemetriaBusService {

    @Autowired
    private TelemetriaBusRepository repository;

    public List<TelemetriaBus> obtenerTodos() {
        return repository.findAll();
    }

    public List<TelemetriaBus> obtenerPorRecorrido(String recorrido) {
        return repository.findByRecorrido(recorrido);
    }

    // NUEVO MÉTODO: Recibe el objeto desde el Controlador y lo guarda en Neon
    public TelemetriaBus guardar(TelemetriaBus bus) {
        return repository.save(bus);
    }
}