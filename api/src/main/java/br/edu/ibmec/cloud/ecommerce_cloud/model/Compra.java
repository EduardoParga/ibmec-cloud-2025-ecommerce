package br.edu.ibmec.cloud.ecommerce_cloud.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
public class Compra {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String nome_produto;
    private Double price;
    private LocalDateTime dtCompra;
    private String numeroPedido; 

    @Column(length = 512)
    private String imageUrl;

    @ManyToOne
    @JoinColumn(name = "usuario_id")
    private Usuario usuario;
}