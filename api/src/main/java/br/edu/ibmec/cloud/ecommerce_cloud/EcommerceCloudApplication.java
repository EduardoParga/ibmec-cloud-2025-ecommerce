package br.edu.ibmec.cloud.ecommerce_cloud;

import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.boot.autoconfigure.SpringBootApplication; 
import org.springframework.boot.SpringApplication;

@EnableJpaRepositories(basePackages = "br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa")
@SpringBootApplication
public class EcommerceCloudApplication {
    public static void main(String[] args) {
        SpringApplication.run(EcommerceCloudApplication.class, args);
    }
}