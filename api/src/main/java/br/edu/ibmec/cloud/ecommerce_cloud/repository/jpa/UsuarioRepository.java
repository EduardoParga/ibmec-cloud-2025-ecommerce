package br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa;

import org.springframework.data.jpa.repository.JpaRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;

public interface UsuarioRepository extends JpaRepository<Usuario, String> {
    // métodos customizados, se houver
}