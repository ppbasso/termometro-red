package termometrored.api.model;

import javax.persistence.*;

@Entity
@Table(name = "telemetria_buses")
public class TelemetriaBus {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String paradero;
    private String recorrido;
    private String patente;

    @Column(name = "distancia_metros")
    private Integer distanciaMetros;

    @Column(name = "tiempo_estimado_min")
    private Integer tiempoEstimadoMin;

    // Constructor vacío exigido por Hibernate
    public TelemetriaBus() {}

    // Getters
    public Long getId() { return id; }
    public String getParadero() { return paradero; }
    public String getRecorrido() { return recorrido; }
    public String getPatente() { return patente; }
    public Integer getDistanciaMetros() { return distanciaMetros; }
    public Integer getTiempoEstimadoMin() { return tiempoEstimadoMin; }

    // SETTERS (CRÍTICOS para recibir el POST de Python)
    public void setId(Long id) { this.id = id; }
    public void setParadero(String paradero) { this.paradero = paradero; }
    public void setRecorrido(String recorrido) { this.recorrido = recorrido; }
    public void setPatente(String patente) { this.patente = patente; }
    public void setDistanciaMetros(Integer distanciaMetros) { this.distanciaMetros = distanciaMetros; }
    public void setTiempoEstimadoMin(Integer tiempoEstimadoMin) { this.tiempoEstimadoMin = tiempoEstimadoMin; }
}