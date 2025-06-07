package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CartaoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CompraRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa.UsuarioRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario; 
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

// ...restante do código...
@RestController
@RequestMapping("/users")
public class UsuarioController {

    @Autowired
    private UsuarioRepository repository;

    @GetMapping
    public ResponseEntity<List<Usuario>> getUsers() {
        List<Usuario> response = repository.findAll();
        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    @GetMapping("{id}")
    public ResponseEntity<Usuario> getById(@PathVariable String id) {
        Optional<Usuario> response = this.repository.findById(id);
        if (response.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        return new ResponseEntity<>(response.get(), HttpStatus.OK);
    }

    @PostMapping
    public ResponseEntity<Usuario> create(@RequestBody Usuario usuario){
        // Gera o ID do usuário se não vier preenchido
        if (usuario.getId() == null || usuario.getId().isEmpty()) {
            usuario.setId(UUID.randomUUID().toString());
        }
        this.repository.save(usuario);
        return new ResponseEntity<>(usuario, HttpStatus.CREATED);
    }

    @DeleteMapping("{id}")
    public ResponseEntity<Usuario> delete(@PathVariable String id) {
        Optional<Usuario> response = this.repository.findById(id);
        if (response.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        // Exclui o usuario da base
        this.repository.delete(response.get());

        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}