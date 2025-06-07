package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CartaoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CompraRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Endereco;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa.UsuarioRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa.EnderecoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/address/{id_user}")
public class EnderecoController {

    @Autowired
    private EnderecoRepository enderecoRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @PostMapping
    public ResponseEntity<Endereco> create(@PathVariable("id_user") String id_user, @RequestBody Endereco endereco) {
        // Verificando se o usuario existe na base
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        // Gera o ID do endereço se não vier preenchido
        if (endereco.getId() == null || endereco.getId().isEmpty()) {
            endereco.setId(UUID.randomUUID().toString());
        }

        // Cria o endereco na base
        enderecoRepository.save(endereco);

        // Associa o endereco ao usuario
        Usuario usuario = optionalUsuario.get();
        usuario.getEnderecos().add(endereco);
        usuarioRepository.save(usuario);

        return new ResponseEntity<>(endereco, HttpStatus.CREATED);
    }
}