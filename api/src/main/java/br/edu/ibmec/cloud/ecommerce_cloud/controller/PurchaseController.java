package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Compra;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CartaoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.CompraRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.jpa.UsuarioRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/purchase/{id_user}")
public class PurchaseController {

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private CompraRepository compraRepository;

    @GetMapping("/extract")
    public ResponseEntity<List<Map<String, Object>>> getExtract(@PathVariable("id_user") String id_user) {
        Optional<Usuario> optionalUsuario = usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        // Busca compras pelo ID do usuário (Cosmos)
        List<Compra> compras = compraRepository.findByUsuarioId(id_user);

        List<Map<String, Object>> extrato = new ArrayList<>();
        for (Compra compra : compras) {
            Map<String, Object> item = new HashMap<>();
            item.put("nome_produto", compra.getNome_produto());
            item.put("price", compra.getPrice());
            item.put("dtCompra", compra.getDtCompra() != null ? compra.getDtCompra().toString() : null);
            item.put("imageUrl", compra.getImageUrl());
            extrato.add(item);
        }

        return new ResponseEntity<>(extrato, HttpStatus.OK);
    }

    @GetMapping("/orders")
    public ResponseEntity<List<Map<String, Object>>> getOrders(@PathVariable("id_user") String id_user) {
        Optional<Usuario> optionalUsuario = usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        // Busca compras pelo ID do usuário (Cosmos)
        List<Compra> compras = compraRepository.findByUsuarioId(id_user);

        List<Map<String, Object>> pedidos = new ArrayList<>();
        for (Compra compra : compras) {
            Map<String, Object> item = new HashMap<>();
            item.put("nome_produto", compra.getNome_produto());
            item.put("price", compra.getPrice());
            item.put("dtCompra", compra.getDtCompra() != null ? compra.getDtCompra().toString() : null);
            item.put("numeroPedido", compra.getNumeroPedido());
            item.put("imageUrl", compra.getImageUrl());
            pedidos.add(item);
        }

        return new ResponseEntity<>(pedidos, HttpStatus.OK);
    }

    @GetMapping("/orders/{numeroPedido}")
    public ResponseEntity<Map<String, Object>> getOrderByNumeroPedido(
            @PathVariable("id_user") String id_user,
            @PathVariable("numeroPedido") String numeroPedido) {

        Optional<Usuario> optionalUsuario = usuarioRepository.findById(id_user);
        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        // Busca pedido com e sem #
        Compra compra = compraRepository.findByUsuarioIdAndNumeroPedido(id_user, numeroPedido);
        if (compra == null && !numeroPedido.startsWith("#")) {
            compra = compraRepository.findByUsuarioIdAndNumeroPedido(id_user, "#" + numeroPedido);
        }
        if (compra == null && numeroPedido.startsWith("#")) {
            compra = compraRepository.findByUsuarioIdAndNumeroPedido(id_user, numeroPedido.substring(1));
        }
        if (compra == null)
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        Map<String, Object> item = new HashMap<>();
        item.put("nome_produto", compra.getNome_produto());
        item.put("price", compra.getPrice());
        item.put("dtCompra", compra.getDtCompra() != null ? compra.getDtCompra().toString() : null);
        item.put("numeroPedido", compra.getNumeroPedido());
        item.put("imageUrl", compra.getImageUrl());

        return new ResponseEntity<>(item, HttpStatus.OK);
    }
}