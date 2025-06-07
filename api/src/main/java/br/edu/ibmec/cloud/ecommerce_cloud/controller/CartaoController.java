package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Compra;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Cartao;

import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CartaoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CompraRepository;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Product;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa.UsuarioRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa.ProductRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.request.TransacaoRequest;
import br.edu.ibmec.cloud.ecommerce_cloud.request.TransacaoResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;
import java.util.Random;
import java.util.List;

@RestController
@RequestMapping("/credit_card/{id_user}")
public class CartaoController {

    @Autowired
    private CartaoRepository cartaoRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private CompraRepository compraRepository;

    @Autowired
    private ProductRepository productRepository;

    @PostMapping
    public ResponseEntity<Cartao> create(@PathVariable("id_user") String id_user, @RequestBody Cartao cartao) {
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        // Gera o ID do cartão se não vier preenchido
        if (cartao.getId() == null || cartao.getId().isEmpty()) {
            cartao.setId(UUID.randomUUID().toString());
        }

        // Associa o cartão ao usuário (apenas referência)
        cartao.setIdUsuario(id_user);

        // Salva o cartão no CosmosDB
        cartaoRepository.save(cartao);

        return new ResponseEntity<>(cartao, HttpStatus.CREATED);
    }

    @PostMapping("/authorize")
    public ResponseEntity<TransacaoResponse> authorize(@PathVariable("id_user") String id_user, @RequestBody TransacaoRequest request) {
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        // Busca os cartões do usuário no CosmosDB
        List<Cartao> cartoes = cartaoRepository.findByIdUsuario(id_user);
        Cartao cartaoCompra = null;

        for (Cartao cartao : cartoes) {
            if (request.getNumero().equals(cartao.getNumero()) && request.getCvv().equals(cartao.getCvv())) {
                cartaoCompra = cartao;
                break;
            }
        }

        TransacaoResponse response = new TransacaoResponse();

        if (cartaoCompra == null) {
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Cartão não encontrado para o usuario");
            return new ResponseEntity<>(response, HttpStatus.NOT_FOUND);
        }

        if (cartaoCompra.getDtExpiracao() != null && cartaoCompra.getDtExpiracao().isBefore(LocalDateTime.now())) {
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Cartão Expirado");
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }

        if (cartaoCompra.getSaldo() < request.getValor()) {
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Sem saldo para realizar a compra");
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }

        cartaoCompra.setSaldo(cartaoCompra.getSaldo() - request.getValor());
        cartaoRepository.save(cartaoCompra);

        String letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        char letra = letras.charAt(new Random().nextInt(letras.length()));
        int numero = 1000000 + new Random().nextInt(9000000); // 7 dígitos
        String numeroPedido = "#P" + letra + numero;

        String imageUrl = null;
        if (request.getNome_produto() != null) {
            List<Product> produtos = productRepository.findByProductName(request.getNome_produto());
            if (produtos != null && !produtos.isEmpty()) {
                Product produto = produtos.get(0);
                if (produto.getImageUrl() != null && !produto.getImageUrl().isEmpty()) {
                    imageUrl = produto.getImageUrl().get(0);
                }
            }
        }

        Compra compra = new Compra();
        compra.setId(UUID.randomUUID().toString());
        compra.setUsuario(optionalUsuario.get());
        compra.setNome_produto(request.getNome_produto());
        compra.setPrice(request.getValor());
        compra.setDtCompra(LocalDateTime.now());
        compra.setNumeroPedido(numeroPedido);
        compra.setImageUrl(imageUrl);
        compraRepository.save(compra);

        response.setStatus("AUTHORIZED");
        response.setDtTransacao(LocalDateTime.now());
        response.setMessage("Compra autorizada");
        response.setCodigoAutorizacao(UUID.randomUUID());
        response.setNumeroPedido(numeroPedido);

        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    @GetMapping
    public ResponseEntity<List<Cartao>> list(@PathVariable("id_user") String id_user) {
        List<Cartao> cartoes = cartaoRepository.findByIdUsuario(id_user);
        return new ResponseEntity<>(cartoes, HttpStatus.OK);
    }
}