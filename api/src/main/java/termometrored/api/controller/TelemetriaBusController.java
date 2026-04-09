package termometrored.api.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import termometrored.api.model.TelemetriaBus;
import termometrored.api.repository.TelemetriaBusRepository;

import java.util.List;

@RestController
@RequestMapping("/api/telemetria")
public class TelemetriaBusController {

    @Autowired
    private TelemetriaBusRepository repository;

    @GetMapping
    public List<TelemetriaBus> obtenerTodos() {
        // Magia de Spring: Esto equivale a "SELECT * FROM telemetria_buses"
        return repository.findAll();
    }
}