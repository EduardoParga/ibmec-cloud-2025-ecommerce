package br.edu.ibmec.cloud.ecommerce_cloud.model;

import jakarta.persistence.*;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Data
@Entity(name = "usuario")
public class Usuario {

    public Usuario() {
        this.cartoes = new ArrayList<>();
        this.enderecos = new ArrayList<>();
    }

    @Id
    private String id;

    @PrePersist
    public void generateId() {
        if (this.id == null) {
            this.id = UUID.randomUUID().toString();
        }
    }

    @Column
    private String nome;

    @Column
    private String email;

    @Column
    private String dt_nascimento;

    @Column
    private String cpf;

    @Column
    private String telefone;

    @OneToMany
    @JoinColumn(referencedColumnName = "id", name = "id_usuario")
    private List<Cartao> cartoes;

    @OneToMany
    @JoinColumn(referencedColumnName = "id", name = "id_usuario")
    private List<Endereco> enderecos;
}