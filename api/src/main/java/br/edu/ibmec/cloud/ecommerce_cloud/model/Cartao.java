package br.edu.ibmec.cloud.ecommerce_cloud.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity(name="cartao")
public class Cartao {

    @Id
    private String id;

    @Column
    private String numero;

    @Column
    private LocalDateTime dtExpiracao;

    @Column
    private String cvv;

    @Column
    private Double saldo;

    @Column(name = "id_usuario")
    private String idUsuario;

    public String getIdUsuario() {
        return idUsuario;
    }

    public void setIdUsuario(String idUsuario) {
        this.idUsuario = idUsuario;
    }
}