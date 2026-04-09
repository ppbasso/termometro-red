package termometrored.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class TermometroRedApiApplication {
    public static void main(String[] args) {
        SpringApplication.run(TermometroRedApiApplication.class, args);
        System.out.println("====== MOTOR TERMOMETRO-RED (SPRING BOOT 2.7) INICIADO CON EXITO ======");
    }
}
