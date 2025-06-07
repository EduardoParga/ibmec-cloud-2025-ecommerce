package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CartaoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CompraRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Product;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/product")
public class ProductController {

    @Autowired
    private ProductRepository productRepository;

    @GetMapping
    public List<Product> getAll() {
        return productRepository.findAll();
    }

    @GetMapping("/search")
    public List<Product> searchProducts(@RequestParam("termo") String termo) {
        // Remove pontuação, deixa minúsculo e separa em palavras
        termo = termo.replaceAll("[^a-zA-Z0-9 ]", " ").toLowerCase();
        String[] palavras = termo.split("\\s+");
        Set<Product> resultado = new HashSet<>();
        for (String palavra : palavras) {
            if (palavra.length() > 1) { // ignora palavras muito curtas
                resultado.addAll(productRepository.searchByWord(palavra));
            }
        }
        return new ArrayList<>(resultado);
    }
}