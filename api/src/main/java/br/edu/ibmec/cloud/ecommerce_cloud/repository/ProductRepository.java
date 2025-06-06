package br.edu.ibmec.cloud.ecommerce_cloud.repository;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Integer> {
    @Query("SELECT p FROM Product p WHERE " +
           "LOWER(p.productName) LIKE %:word% OR LOWER(p.productDescription) LIKE %:word%")
    List<Product> searchByWord(String word);
     List<Product> findByProductName(String productName); 
}