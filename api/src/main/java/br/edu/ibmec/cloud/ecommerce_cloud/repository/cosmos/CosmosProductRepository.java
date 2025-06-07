package br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos;

import com.azure.spring.data.cosmos.repository.CosmosRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Product;
import org.springframework.stereotype.Repository;

@Repository
public interface CosmosProductRepository extends CosmosRepository<Product, String> {
    // Agora está integrado ao CosmosDB!
}