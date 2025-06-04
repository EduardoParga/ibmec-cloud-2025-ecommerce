package br.edu.ibmec.cloud.ecommerce_cloud.request;

import lombok.Data;

@Data
public class TransacaoRequest {
    private String numero;
    private String cvv;
    private Double valor;
    private String nome_produto; 
}