package br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Compra;
import org.springframework.stereotype.Repository;
import com.azure.spring.data.cosmos.repository.CosmosRepository;
import java.util.List;

@Repository
public interface CompraRepository extends CosmosRepository<Compra, String> {
    List<Compra> findByUsuarioId(String usuarioId);
    Compra findByUsuarioIdAndNumeroPedido(String usuarioId, String numeroPedido);
}