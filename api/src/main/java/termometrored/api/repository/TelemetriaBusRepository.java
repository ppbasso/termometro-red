package termometrored.api.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import termometrored.api.model.TelemetriaBus;
import java.util.List; // Importación necesaria para devolver una lista de resultados

@Repository
public interface TelemetriaBusRepository extends JpaRepository<TelemetriaBus, Long> {
    
    // EXPLICACIÓN DIDÁCTICA (Capa de Datos):
    // Spring Data JPA lee "findBy" y sabe que debe ejecutar una instrucción SELECT.
    // Luego lee "Recorrido" y mapea dinámicamente el parámetro (String recorrido) 
    // generando en tiempo de ejecución: SELECT * FROM telemetria_buses WHERE recorrido = ?
    List<TelemetriaBus> findByRecorrido(String recorrido);
}