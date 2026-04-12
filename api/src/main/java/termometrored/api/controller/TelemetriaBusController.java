package termometrored.api.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import termometrored.api.model.TelemetriaBus;
import termometrored.api.service.TelemetriaBusService;

import java.util.List;

@RestController
@RequestMapping("/api/telemetria")
@CrossOrigin(origins = "*") 
public class TelemetriaBusController {

    @Autowired
    private TelemetriaBusService service;

    @GetMapping
    public List<TelemetriaBus> obtenerTelemetria(@RequestParam(required = false) String recorrido) {
        if (recorrido != null && !recorrido.trim().isEmpty()) {
            return service.obtenerPorRecorrido(recorrido);
        } else {
            return service.obtenerTodos();
        }
    }

    // NUEVO ENDPOINT: Recibe el JSON de Python (@RequestBody) y lo inserta en el sistema
    @PostMapping
    public TelemetriaBus guardarTelemetria(@RequestBody TelemetriaBus bus) {
        return service.guardar(bus);
    }
}