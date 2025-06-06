package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Cartao;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Compra;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Product;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.CartaoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.UsuarioRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.CompraRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.ProductRepository;
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
    public ResponseEntity<Cartao> create(@PathVariable("id_user") int id_user, @RequestBody Cartao cartao) {
        // Verificando se o usuario existe na base
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        // Cria o cartao de credito na base
        cartaoRepository.save(cartao);

        // Associa o cartao de credito ao usuario
        Usuario usuario = optionalUsuario.get();
        usuario.getCartoes().add(cartao);
        usuarioRepository.save(usuario);

        return new ResponseEntity<>(cartao, HttpStatus.CREATED);
    }

    @PostMapping("/authorize")
    public ResponseEntity<TransacaoResponse> authorize(@PathVariable("id_user") int id_user, @RequestBody TransacaoRequest request) {
        // Verificando se o usuario existe na base
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        Usuario usuario = optionalUsuario.get();
        Cartao cartaoCompra = null;

        // Busca os dados do cartao de credito;
        for (Cartao cartao : usuario.getCartoes()) {
            if (request.getNumero().equals(cartao.getNumero()) && request.getCvv().equals(cartao.getCvv())) {
                cartaoCompra = cartao;
                break;
            }
        }

        TransacaoResponse response = new TransacaoResponse();

        // Não achei o cartao do usuario
        if (cartaoCompra == null) {
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Cartão não encontrado para o usuario");
            return new ResponseEntity<>(response, HttpStatus.NOT_FOUND);
        }

        // Verifica se o cartao não está expirado
        if (cartaoCompra.getDtExpiracao() != null && cartaoCompra.getDtExpiracao().isBefore(LocalDateTime.now())) {
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Cartão Expirado");
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }

        // Verifica se tem dinheiro no cartao para realizar a compra
        if (cartaoCompra.getSaldo() < request.getValor()) {
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Sem saldo para realizar a compra");
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }

        // Debita no cartao de credito o valor da compra
        cartaoCompra.setSaldo(cartaoCompra.getSaldo() - request.getValor());

        // Atualiza o cartao na base de dados
        cartaoRepository.save(cartaoCompra);

        // Gera número de pedido
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
        compra.setUsuario(usuario);
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
}