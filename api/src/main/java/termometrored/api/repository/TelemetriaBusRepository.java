package termometrored.api.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import termometrored.api.model.TelemetriaBus;

@Repository
public interface TelemetriaBusRepository extends JpaRepository<TelemetriaBus, Long> {
}
