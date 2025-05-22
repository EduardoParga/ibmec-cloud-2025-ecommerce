package br.edu.ibmec.cloud.ecommerce_cloud.model;

import jakarta.persistence.*;
import lombok.Data;
import java.util.List;

@Data
@Entity
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String productCategory;

    private String productName;

    private double price;

    @ElementCollection
    @CollectionTable(name = "product_images", joinColumns = @JoinColumn(name = "product_id"))
    @Column(name = "image_url") // <- nome da coluna no banco de dados
    private List<String> imageUrl; // <- nome da propriedade que vai para o JSON

    private String productDescription;
}
