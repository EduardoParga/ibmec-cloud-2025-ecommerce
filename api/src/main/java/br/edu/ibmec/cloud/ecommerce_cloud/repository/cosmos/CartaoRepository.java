package br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Cartao;
import com.azure.spring.data.cosmos.repository.CosmosRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface CartaoRepository extends CosmosRepository<Cartao, String> {
    List<Cartao> findByIdUsuario(String idUsuario);
}